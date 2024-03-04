import logging
import threading

from grapycal.utils.misc import as_type

logger = logging.getLogger(__name__)
from grapycal.utils.logging import user_logger, warn_extension

from typing import Any, Dict, List
from dacite import from_dict
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node, NodeMeta
from grapycal.sobjects.port import InputPort, OutputPort, Port
from objectsync import ObjSetTopic, SObject, SObjectSerialized
from itertools import count


class Editor(SObject):
    frontend_type = "Editor"

    def build(self, old: SObjectSerialized | None = None):
        from grapycal.core.workspace import Workspace  # avoid circular import

        self.workspace: Workspace = self._server.globals.workspace
        self.node_types = self.workspace._extention_manager._node_types_topic

        if old is not None:
            # If the editor is loaded from a save, we need to recreate the nodes and edges.
            nodes: list[SObjectSerialized] = []
            edges: list[SObjectSerialized] = []
            node_types = self.node_types.get()
            for obj in old.children.values():
                if obj.type in node_types:
                    nodes.append(obj)
                elif obj.type == "Edge":
                    edges.append(obj)
                else:
                    extension_name, type_name = obj.type.split(".")
                    user_logger.warning(
                        f"{type_name} is not defined in the current version of {extension_name}. Nodes instances of this type are discarded.",
                        extra={"key": f"{type_name} node not defined"},
                    )
            self.restore(nodes, edges)

        # called by client
        self.register_service("create_edge", self.create_edge_from_port_id)
        self.register_service("create_node", self._create_node_service)
        self.register_service("copy", self._copy)
        self.register_service("paste", self._paste, pass_sender=True)
        self.register_service("delete", self._delete)

        # used by frontend
        self._running_nodes = self.add_attribute("running_nodes", ObjSetTopic, is_stateful=False)
        self._set_running_true = set()
        self._set_running_true_2 = set()
        self._running = set()
        self._set_running_lock = threading.Lock()

        self.workspace.clock.on_tick += self.check_running_nodes

    def check_running_nodes(self):
        with self._set_running_lock:
            self._running_nodes.set(list(self._running | self._set_running_true | self._set_running_true_2))
            self._set_running_true_2 = self._set_running_true
            self._set_running_true = set()

    def set_running(self, node: Node, running: bool):
        with self._set_running_lock:
            if running:
                self._set_running_true.add(node)
                self._running.add(node)
            else:
                self._running.discard(node)

    def restore(self, nodes: list[SObjectSerialized], edges: list[SObjectSerialized]):
        # restore the nodes and edges
        with self._server.record(allow_reentry=True):
            new_node_ids, new_edge_ids = self._restore(nodes, edges)
            for node in self._restored_nodes:
                # the post_create method must called outside of the restore_event to be in auto mode
                node.post_create()

        self._new_node_ids = new_node_ids  # the _paste() method will use this
        n_nodes = len(new_node_ids)
        n_edges = len(new_edge_ids)
        if n_nodes != 0 or n_edges != 0:
            msg = "Restored "
            if n_nodes > 0:
                msg += f"{n_nodes} node"
                if n_nodes > 1:
                    msg += "s"  # english is hard :(
            if n_edges > 0:
                if n_nodes > 0:
                    msg += " and "
                msg += f"{n_edges} edge"
                if n_edges > 1:
                    msg += "s"
            user_logger.info(msg)
        

    def _restore(
        self, node_list: list[SObjectSerialized], edge_list: list[SObjectSerialized]
    ):
        # Generate new ids for the nodes and edges
        nodes: dict[str, SObjectSerialized] = {}
        edges: dict[str, SObjectSerialized] = {}
        for obj in node_list:
            if obj.id in self._server._objects:
                new_id = f"r_{self.workspace.next_id()}"  # r means restored
            else:
                new_id = obj.id  # if possible, keep the old id
            nodes[new_id] = obj

        for obj in edge_list:
            if obj.id in self._server._objects:
                new_id = f"r_{self.workspace.next_id()}"
            else:
                new_id = obj.id
            edges[new_id] = obj

        # Edges and nodes may reference each other with attributes, so we need to update the references
        id_map: dict[str, str] = {}
        for new_id, old in nodes.items():
            id_map[old.id] = new_id
        for new_id, old in edges.items():
            id_map[old.id] = new_id

        for obj in nodes.values():
            obj.update_references(id_map)

        for obj in edges.values():
            obj.update_references(id_map)

        # TODO: also update references of existing nodes

        # To handle edge recovery, we need to know the mapping between old and new port ids.
        # We use the port name and the node id to identify a port.
        # The mapping can be accessed by combining the following maps:
        #   port_map_1: old id -> (port name, old node id)
        #   node_id_map: old node id -> new node id
        #   port_map_2: (port name, new node id) -> new id

        port_map_1 = {}
        for node in nodes.values():
            old_port_ids: List[str] = node.get_attribute(
                "in_ports"
            ) + node.get_attribute("out_ports")
            for old_port in old_port_ids:
                old_port_info = node.children[old_port]
                port_map_1[old_port] = (
                    old_port_info.get_attribute("is_input"),
                    old_port_info.get_attribute("name"),
                    node.id,
                )

        # Recreate the nodes
        new_nodes: dict[str, tuple[SObjectSerialized, Node]] = {}
        for obj in nodes.values():
            # Here we don't pass serialized = obj because we don't want to use the SObject._deserialize.
            # Instead we want a clean build of the node then calling restore_from_version explicitly.
            # By doing this, the node can resolve any backward compatibility issues manually.
            new_node_id = id_map[obj.id]

            # The node may fail to create when the restore() method is called when pasting, and it should not be treated as an error.
            # For example, copy and paste a node that should be unique.
            try:
                old_node_info = NodeInfo(obj)
                node = self.add_child_s(
                    obj.type, id=new_node_id, is_new=False, old_node_info=old_node_info
                )
                assert isinstance(node, Node), f"Expected node, got {node}"
            except Exception:
                extension_name, type_name = obj.type.split(".")
                warn_extension(
                    extension_name,
                    f"Failed to restore {type_name} {obj.id}",
                    exc_info=True,
                )
                if self._server.has_object(new_node_id):
                    self._server.destroy_object(new_node_id)
            else:
                new_nodes[obj.id] = (obj, node)

        # After the nodes are created and before the edges are created, we must map the port ids so edges can find the ports on new nodes
        port_map_2 = {}
        for old_serialized, new_node in new_nodes.values():
            ports: List[Port] = new_node.in_ports.get() + new_node.out_ports.get()  # type: ignore
            for port in ports:
                port_map_2[
                    (port.is_input.get(), port.name.get(), new_node.get_id())
                ] = port.get_id()

        existing_ports = []
        for node in self.get_children_of_type(Node):
            existing_ports += [
                port.get_id() for port in (node.in_ports.get() + node.out_ports.get())
            ]

        existing_ports = set(existing_ports)

        def port_id_map(old_port_id: str) -> str | None:
            """
            With port_map_1 and port_map_2, we can map old ports to new ones by matching their names
            None is returned if the port does not exist in the new editor
            """

            try:
                is_input, port_name, old_node_id = port_map_1[old_port_id]
            except KeyError:
                # fallback to finding the existing port
                if old_port_id in existing_ports:
                    return old_port_id
                else:
                    return None

            new_node_id = id_map[old_node_id]

            try:
                new_port_id = port_map_2[(is_input, port_name, new_node_id)]
            except KeyError:
                if old_port_id in existing_ports:
                    return old_port_id
                else:
                    return None

            return new_port_id

        # Now we can recreate the edges

        new_edge_ids = []
        for obj in edges.values():
            new_tail_id = port_id_map(obj.get_attribute("tail"))
            new_head_id = port_id_map(obj.get_attribute("head"))
            if new_tail_id is None or new_head_id is None:
                logger.debug(
                    f"edge {obj.id} was not restored. head: {new_head_id} tail: {new_tail_id}"
                )
                continue  # skip edges that reference ports that don't exist in the new version of nodes

            # check the ports accept the edge
            tail = self._server.get_object(new_tail_id)
            head = self._server.get_object(new_head_id)
            assert isinstance(tail, OutputPort) and isinstance(head, InputPort)
            if tail.is_full() or head.is_full():
                logger.debug(
                    f"edge {obj.id} was not restored. head: {new_head_id} tail: {new_tail_id}"
                )
                continue  # skip edges that reference ports that are full

            # keep the old id if possible
            if obj.id in self._server._objects:
                new_edge_id = f"r_{self.workspace.next_id()}"
            else:
                new_edge_id = obj.id
            new_edge_id = self.create_edge_from_port_id(
                new_tail_id, new_head_id, new_edge_id
            )
            new_edge_ids.append(new_edge_id)

        # return the ids of the restored nodes and edges
        new_node_ids = []
        for _, node in new_nodes.values():
            new_node_ids.append(node.get_id())

        # used by self.restore()
        self._restored_nodes = [node for _, node in new_nodes.values()]

        return new_node_ids, new_edge_ids

    def _create_node_service(self, node_type: str, **kwargs):
        self.create_node(node_type, **kwargs)

    def create_node(self, node_type: str | type[Node], **kwargs) -> Node | None:
        if isinstance(node_type, str):
            node_type_cls = as_type(self._server._object_types[node_type], NodeMeta)
        else:
            node_type_cls = node_type
        if node_type_cls._is_singleton and hasattr(node_type_cls, "instance"):
            user_logger.warning(
                f"Node type {node_type} is a singleton and already exists"
            )
            return None
        new_node = self.add_child(node_type_cls, is_preview=False, **kwargs)
        assert isinstance(new_node, Node)
        new_node.post_create()
        user_logger.info(f"Created {new_node.get_type_name()}")
        return new_node

    def create_edge(
        self, tail: OutputPort, head: InputPort, new_edge_id: str | None = None
    ) -> Edge:
        # Check the tail and head have space for the edge
        if tail.is_full() or head.is_full():
            raise Exception("A port is full")
        return self.add_child(Edge, tail=tail, head=head, id=new_edge_id)

    def create_edge_from_port_id(
        self, tail_id: str, head_id: str, new_edge_id: str | None = None
    ) -> str:
        tail = self._server.get_object(tail_id)
        head = self._server.get_object(head_id)
        assert isinstance(tail, OutputPort)
        assert isinstance(head, InputPort)
        new_edge = self.create_edge(tail, head, new_edge_id)
        return new_edge.get_id()

    def _copy(self, ids: list[str]):
        """
        Returns a list of serialized objects
        """

        result = {"nodes": [], "edges": []}  # type: dict[str,list[Dict[str,Any]]]

        for id in ids:
            obj = self._server.get_object(id)
            if isinstance(obj, Node):
                result["nodes"].append(obj.serialize().to_dict())
            elif isinstance(obj, Edge):
                result["edges"].append(obj.serialize().to_dict())
            else:
                raise Exception(f"Unknown object type {obj}")

        return result

    def _paste(
        self, data: dict[str, list[Dict]], mouse_pos: dict[str, int], sender: int
    ):
        """
        data is the result of _copy
        """
        try:
            # convert the dicts to SObjectSerialized
            nodes = [from_dict(SObjectSerialized, d) for d in data["nodes"]]
            edges = [from_dict(SObjectSerialized, d) for d in data["edges"]]
        except Exception as e:
            user_logger.info(f"Invalid paste content")
            return

        # translate the center of the nodes to the mouse position
        if len(nodes) > 0:

            def get_x(node: SObjectSerialized):
                return float(node.get_attribute("translation").split(",")[0])

            def get_y(node: SObjectSerialized):
                return float(node.get_attribute("translation").split(",")[1])

            x1 = min(get_x(node) for node in nodes)
            y1 = min(get_y(node) for node in nodes)
            x2 = max(get_x(node) for node in nodes)
            y2 = max(get_y(node) for node in nodes)

            dx = mouse_pos["x"] - (x1 + x2) / 2
            dy = mouse_pos["y"] - (y1 + y2) / 2

            snap = 17
            for node in nodes:
                new_x = float(get_x(node)) + dx
                new_y = float(get_y(node)) + dy
                new_x = round(new_x / snap) * snap
                new_y = round(new_y / snap) * snap
                new_translation = f"{new_x},{new_y}"
                for attr in node.attributes:
                    name, type, value, is_stateful, order_strict = attr
                    if name == "translation":
                        attr[2] = new_translation

        with self._server.record():
            self.restore(nodes=nodes, edges=edges)
            for node_id in self._new_node_ids:
                node = self._server.get_object(node_id)
                node.add_tag(f"pasted_by_{sender}")

    def _delete(self, ids: list[str]):
        """
        Ctrl+X, delete, and backspace lead to this method
        """
        # separate the nodes and edges
        node_ids = []
        edge_ids = []

        # check for duplicate deletion
        # this happens when the previous delete message are still flying to the client
        for id in ids:
            if not self._server.has_object(id):
                user_logger.warning(
                    f"Object {id} does not exist. It may have been deleted already"
                )
                return
            obj = self._server.get_object(id)
            if isinstance(obj, Node):
                if obj.is_destroyed():
                    user_logger.warning(f"Node {obj} is already destroyed")
                    return
                node_ids.append(id)
            elif isinstance(obj, Edge):
                if obj.is_destroyed():
                    user_logger.warning(f"Edge {obj} is already destroyed")
                    return
                edge_ids.append(id)
            else:
                raise Exception(f"Unknown object type {obj}")
            
        for id in node_ids:
            obj = self._server.get_object(id)
            

        if len(node_ids) == 0 and len(edge_ids) == 0:
            return

        nodes: set[Node] = set()
        edges: set[Edge] = set()
        for id in node_ids:
            obj = self._server.get_object(id)
            if isinstance(obj, Node):
                nodes.add(obj)
            else:
                raise Exception(f"{obj} is not a node")
        for id in edge_ids:
            obj = self._server.get_object(id)
            if isinstance(obj, Edge):
                edges.add(obj)
            else:
                raise Exception(f"{obj} is not an edge")
        
        # also include the edges connected to the nodes
        for node in nodes:
            for port in node.in_ports.get() + node.out_ports.get():
                for edge in port.edges:
                    edges.add(edge)
        
        # check for duplicate deletion
        # this happens when the previous delete message are still flying to the client
        for edge in edges:
            if edge.is_destroyed():
                raise Exception(f"Edge {edge} is already destroyed")
        for node in nodes:
            if node.is_destroyed():
                raise Exception(f"Node {node} is already destroyed")
        
        with self._server.record():
            # actually delete the nodes and edges
            for edge in edges:
                edge.remove()
            for node in nodes:
                node.remove()
        
        # log the deletion
        # TODO: deleting nodes may need thread locking
        msg = "Deleted "
        if len(nodes) > 0:
            msg += f"{len(nodes)} node"
            if len(nodes) > 1:
                msg += "s"  # english is hard :(
        if len(edges) > 0:
            if len(nodes) > 0:
                msg += " and "
            msg += f"{len(edges)} edge"
            if len(edges) > 1:
                msg += "s"
        user_logger.info(msg)

    def _delete_callback(self, node_ids, edge_ids, **kwargs):
        # the opposite of _restore_callback
        # we need to delete the nodes and edges that were pasted
        # this is called when undoing the paste_wrapper

        # determine the nodes and edges to delete
        nodes: set[Node] = set()
        edges: set[Edge] = set()
        for id in node_ids:
            obj = self._server.get_object(id)
            if isinstance(obj, Node):
                nodes.add(obj)
            else:
                raise Exception(f"{obj} is not a node")
        for id in edge_ids:
            obj = self._server.get_object(id)
            if isinstance(obj, Edge):
                edges.add(obj)
            else:
                raise Exception(f"{obj} is not an edge")

        # also include the edges connected to the nodes
        for node in nodes:
            for port in node.in_ports.get() + node.out_ports.get():
                for edge in port.edges:
                    edges.add(edge)

        # check for duplicate deletion
        # this happens when the previous delete message are still flying to the client
        for edge in edges:
            if edge.is_destroyed():
                raise Exception(f"Edge {edge} is already destroyed")
        for node in nodes:
            if node.is_destroyed():
                raise Exception(f"Node {node} is already destroyed")

        # before deleting the nodes and edges, we need to serialize them so we can restore them when the event is undone
        node_serialized = [node.serialize() for node in nodes]
        edge_serialized = [edge.serialize() for edge in edges]

        # actually the nodes and edges
        for edge in edges:
            edge.remove()
        for node in nodes:
            node.remove()

        # log the deletion
        # TODO: deleting nodes may need thread locking
        msg = "Deleted "
        if len(nodes) > 0:
            msg += f"{len(nodes)} node"
            if len(nodes) > 1:
                msg += "s"  # english is hard :(
        if len(edges) > 0:
            if len(nodes) > 0:
                msg += " and "
            msg += f"{len(edges)} edge"
            if len(edges) > 1:
                msg += "s"
        user_logger.info(msg)

        # return the serialized nodes and edges so when the event is undone,
        # _restore_callback() can restore the nodes and edges
        return {"nodes": node_serialized, "edges": edge_serialized}
