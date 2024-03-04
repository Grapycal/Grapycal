from abc import ABCMeta
import io
from itertools import count
import logging
import random
from grapycal.sobjects.controls.buttonControl import ButtonControl
from grapycal.sobjects.controls.imageControl import ImageControl
from grapycal.sobjects.controls.linePlotControl import LinePlotControl
from grapycal.sobjects.controls.nullControl import NullControl
from grapycal.sobjects.controls.optionControl import OptionControl

from grapycal.sobjects.controls.textControl import TextControl

logger = logging.getLogger(__name__)
from grapycal.utils.logging import error_extension, user_logger, warn_extension
from contextlib import contextmanager
import functools
import traceback
from typing import TYPE_CHECKING, Any, Callable, Generator, Literal, Self, TypeVar
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.controls.control import Control, ValuedControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.utils.io import OutputStream
from objectsync import (
    DictTopic,
    SObject,
    StringTopic,
    IntTopic,
    ListTopic,
    ObjListTopic,
    FloatTopic,
    Topic,
    ObjDictTopic,
    SetTopic,
)
from objectsync.sobject import SObjectSerialized, WrappedTopic

if TYPE_CHECKING:
    from grapycal.core.workspace import Workspace


def warn_no_control_name(control_type, node):
    node_type = node.get_type_name().split('.')[1]
    warn_extension(
        node,
        f"Consider giving a name to the {control_type.__name__} in {node_type} \
to prevent error when Grapycal auto restores the control.",
        extra={"key": f"No control name {node_type}"},
    )


def singletonNode(auto_instantiate=True):
    """
    Decorator for singleton nodes.
    There can be only one instance of a singleton node in the workspace.
    The instance can be accessed by the `instance` attribute of the class after it is instantiated.
    Raises an error if the node is instantiated more than once.

    Args:
        - auto_instantiate: If set to True, the node will be instantiated (not visible) automatically when the extension is loaded. Otherwise, the user or extension can instantiate the node at any time.

    Example:
    ```
        @singletonNode()
        class TestSingNode(Node):
            category = "test"

    The instance can be accessed by `TestSingNode.instance`.
    ```

    """
    T = TypeVar("T", bound=Node)

    def wrapper(cls: type[T]):
        # class WrapperClass(cls):
        #     instance: T
        #     def __init__(self,*args,**kwargs):
        #         super().__init__(*args,**kwargs)
        #         if hasattr(WrapperClass, "instance"):
        #             raise RuntimeError("Singleton node can only be instantiated once")
        #         WrapperClass.instance = self # type: ignore # strange complaint from linter

        #     def destroy(self) -> SObjectSerialized:
        #         del WrapperClass.instance
        #         return super().destroy()

        # WrapperClass._is_singleton = True
        # WrapperClass._auto_instantiate = auto_instantiate
        # WrapperClass.__name__ = cls.__name__

        def new_init(self, *args, **kwargs):
            if hasattr(cls, "instance"):
                raise RuntimeError("Singleton node can only be instantiated once")
            super(cls, self).__init__(*args, **kwargs)
            cls.instance = self

        cls.__init__ = new_init

        def new_destroy(self) -> SObjectSerialized:
            del cls.instance
            return super(cls, self).destroy()

        cls.destroy = new_destroy

        cls._is_singleton = True
        cls._auto_instantiate = auto_instantiate
        return cls

    return wrapper


def deprecated(message: str, from_version: str, to_version: str):
    """
    Decorator for deprecated nodes.
    """

    def wrapper(cls: type[Node]):
        old_init_node = cls.init_node

        def new_init_node(self: Node, **kwargs):
            old_init_node(self, **kwargs)
            self.print_exception(
                RuntimeWarning(
                    f"{cls.__name__} is deprecated from version {from_version}, and will be removed in version {to_version}. {message}"
                )
            )
            user_logger.warning(
                f"{cls.__name__} is deprecated from version {from_version} to {to_version}. {message}"
            )

        cls.init_node = new_init_node

        if cls._deprecated is False:
            cls._deprecated = True
            cls.category = "hidden"
            cls.__doc__ = f"{cls.__doc__}\n\nDeprecated from version {from_version} to {to_version}. {message}"

        return cls

    return wrapper


class NodeMeta(ABCMeta):
    class_def_counter = count()
    def_order = {}

    def __init__(self, name, bases, attrs):
        self.def_order[name] = next(self.class_def_counter)
        self._is_singleton = (
            False  # True if @sigletonNode. Used internally by the ExtensionManager.
        )
        self._auto_instantiate = True  # Used internally by the ExtensionManager.
        return super().__init__(name, bases, attrs)


class Node(SObject, metaclass=NodeMeta):
    frontend_type = "Node"
    category = "hidden"
    instance: Self  # The singleton instance. Used by singleton nodes.
    _deprecated = False  # TODO: If set to True, the node will be marked as deprecated in the inspector.

    @classmethod
    def get_def_order(cls):
        return cls.def_order[cls.__name__]

    def initialize(self, serialized=None, *args, **kwargs):
        # TODO: consider add this switch to objectsync level
        if "serialized" in kwargs:
            del kwargs["serialized"]  # a hack making build() always called
        return super().initialize(*args, **kwargs)

    def build(
        self,
        is_preview=False,
        translation="0,0",
        is_new=True,
        old_node_info: NodeInfo | None = None,
        **build_node_args,
    ):
        self.workspace: Workspace = self._server.globals.workspace
        self.is_new = is_new
        self.old_node_info = old_node_info
        self._already_restored_attributes = set()
        self._already_restored_controls = set()

        self.shape = self.add_attribute(
            "shape", StringTopic, "normal", restore_from=False
        )  # normal, simple, round
        self.output = self.add_attribute(
            "output", ListTopic, [], is_stateful=False, restore_from=False
        )
        self.label = self.add_attribute(
            "label", StringTopic, "", is_stateful=False, restore_from=False
        )
        self.label_offset = self.add_attribute(
            "label_offset", FloatTopic, 0, restore_from=False
        )
        self.translation = self.add_attribute("translation", StringTopic, translation)
        self.is_preview = self.add_attribute(
            "is_preview", IntTopic, 1 if is_preview else 0, restore_from=False
        )
        self.category_ = self.add_attribute(
            "category", StringTopic, self.category, restore_from=False
        )
        self.exposed_attributes = self.add_attribute(
            "exposed_attributes", ListTopic, [], restore_from=False
        )
        self.globally_exposed_attributes = self.add_attribute(
            "globally_exposed_attributes", DictTopic, restore_from=False
        )
        self.running = self.add_attribute(
            "running", IntTopic, 1, is_stateful=False, restore_from=False
        )  # 0 for running, other for not running
        self.css_classes = self.add_attribute(
            "css_classes", SetTopic, [], restore_from=False
        )
        self.icon_path = self.add_attribute(
            "icon_path",
            StringTopic,
            f"{self.__class__.__name__[:-4].lower()}",
            is_stateful=False,
            restore_from=False,
        )

        # for inspector
        self.type_topic = self.add_attribute(
            "type", StringTopic, self.get_type_name(), restore_from=False
        )

        self.in_ports = self.add_attribute(
            "in_ports", ObjListTopic[InputPort], restore_from=False
        )
        self.out_ports = self.add_attribute(
            "out_ports", ObjListTopic[OutputPort], restore_from=False
        )

        self.controls = self.add_attribute(
            "controls", ObjDictTopic[Control], restore_from=False
        )

        self.workspace: Workspace = self._server.globals.workspace

        self.on("double_click", self.double_click, is_stateful=False)
        self.on("spawn", self.spawn, is_stateful=False)

        self._output_stream = OutputStream(self.raw_print)
        self._output_stream.set_event_loop(
            self.workspace.get_communication_event_loop()
        )
        self.workspace.get_communication_event_loop().create_task(
            self._output_stream.run()
        )

        from grapycal.sobjects.workspaceObject import WorkspaceObject

        self.globally_exposed_attributes.on_add.add_auto(
            lambda k, v: WorkspaceObject.ins.settings.entries.add(k, v)
        )
        for k, v in self.globally_exposed_attributes.get().items():
            WorkspaceObject.ins.settings.entries.add(k, v)

        self.build_node(**build_node_args)

        self.create()

    def create(self):
        """
        This method was orignated from a wrong design and should not be used. It will be removed in few commits.
        Use build_node() and init_node() instead.
        """
        # check for override of create
        if self.create != Node.create:
            error_extension(self,
                f"Class {self.__class__.__name__} has overridden create() method. The Node.create() method was orignated from a wrong design and should not be used. It will be removed in few commits. Use build_node() and init_node() instead."
            )
            exit(1)

    def build_node(self):
        """
        Create attributes, ports, and controls here.

        Note:
            This method will not be called when the object is being restored. The child objects will be restored automatically instead of
        running this method again.
        """

    def init(self):
        from grapycal.sobjects.editor import (
            Editor,
        )  # import here to avoid circular import

        parent = self.get_parent()
        if isinstance(parent, Editor):
            self.editor = parent
        else:
            self.editor = None

        self.init_node()

    def init_node(self):
        """
        This method is called after the node is built and its ports and controls are created. Use this method if you want to do something after
        the node is built.

        Do not affect other nodes' attributes, controls, or ports or create/destroy other nodes in this method. Use post_create() for that purpose.
        """
        pass

    def _restore(self, version: str): # manually restore the node
        assert self.old_node_info is not None
        self.restore(version, self.old_node_info)
        self.restore_from_version(version, self.old_node_info)

    def restore(self, version, old):
        """
        If the node is recreated from a serialized information, this method will be called after create().
        The old node's information (including attribute values) is in the `old` argument.
        """

    def restore_from_version(self, version: str, old: NodeInfo):
        """
        DEPRECATED from v0.11.0: Use restore() instead.
        """

    def restore_attributes(self, *attribute_names: str | tuple[str, str]):
        """
        You can call it in the `restore` method to restore attributes from the old node.
        For each entry in `attribute_names`, if it's a string, the attribute with the same name will be restored from the old node. If it's a tuple, the first element is the name of the attribute in the old node, and the second element is the name of the attribute in the new node.

        Example:
        ```
        def restore(self,version,old):
            self.restore_attributes('position,'rotation')
            self.restore_attributes(('old_name1','new_name1'),('old_name2','new_name2'))
        ```
        """
        if self.is_new:
            return
        for name in attribute_names:
            if isinstance(name, tuple):
                old_name, new_name = name
            else:
                old_name, new_name = name, name

            if new_name in self._already_restored_attributes:
                continue
            self._already_restored_attributes.add(new_name)

            if not self.has_attribute(new_name):
                warn_extension(
                    self,
                    f"Attribute {new_name} does not exist in {self}",
                    extra={"key": f"Attribute not exist {self.get_type_name()}"},
                )
                continue
            if not self.old_node_info.has_attribute(old_name):
                warn_extension(
                    self,
                    f"Attribute {old_name} does not exist in the old node of {self}",
                    extra={"key": f"Attribute not exist old {self.get_type_name()}"},
                )
                continue
            new_attr = self.get_attribute(new_name)
            old_attr = self.old_node_info[old_name] #type: ignore # not self.is_new grarauntees old_node_info is not None
            if isinstance(new_attr, WrappedTopic):
                new_attr.set_raw(old_attr)
            else:
                new_attr.set(old_attr)

    def restore_controls(self, *control_names: str | tuple[str, str]):
        """
        Recover controls from the old node.
        """
        if self.is_new:
            return
        assert self.old_node_info is not None
        for name in control_names:
            if isinstance(name, tuple):
                old_name, new_name = name
            else:
                old_name, new_name = name, name

            # DEPRECATED from v0.11.0: this check is for backward compatibility.
            if new_name in self._already_restored_controls:
                continue
            self._already_restored_controls.add(new_name)

            if not (new_name in self.controls):
                warn_extension(
                    self,
                    f"Control {new_name} does not exist in {self}",
                    extra={"key": f"Control not exist {self.get_type_name()}"},
                )
                continue
            if not (old_name in self.old_node_info.controls):
                warn_extension(
                    self,
                    f"Control {old_name} does not exist in the old node of {self}",
                    extra={"key": f"Control not exist old {self.get_type_name()}"},
                )
                continue
            try:
                self.controls[new_name].restore_from(
                    self.old_node_info.controls[old_name]
                )
            except Exception as e:
                self.efagrwthnh = ""

    def post_create(self):
        """
        Called after the node is created and restored. Use it for affecting other nodes during the creation process. "Affecting" means creating or destroying other nodes, or modifying other nodes' attributes, controls, or ports.

        It will not be called when the node is restored from undo/redo because if so, other nodes will be affected twice.
        """

    def spawn(self, client_id):
        """
        Called when a client wants to spawn a node.
        """
        new_node = self.workspace.get_workspace_object().main_editor.create_node(
            type(self)
        )
        if new_node is None:  # failed to create node
            return
        new_node.add_tag(
            f"spawned_by_{client_id}"
        )  # So the client can find the node it spawned and make it follow the mouse

    def destroy(self) -> SObjectSerialized:
        """
        Called when the node is destroyed. You can override this method to do something before the node is destroyed.
        Note: Overrided methods should call return super().destroy() at the end.
        """
        self._output_stream.close()
        # # remove all edges connected to the ports
        # for port in self.in_ports:
        #     for edge in port.edges[:]:
        #         edge.remove()
        # for port in self.out_ports:
        #     for edge in port.edges[:]:
        #         edge.remove()
        # raise error if the node is destroyed but still has edges
        for port in self.in_ports:
            if len(port.edges) > 0:
                raise RuntimeError(
                    f"Trying to destroy node {self.get_id()} but it still has input edges"
                )
        for port in self.out_ports:
            if len(port.edges) > 0:
                raise RuntimeError(
                    f"Trying to destroy node {self.get_id()} but it still has output edges"
                )
        for name in self.globally_exposed_attributes.get():
            self.workspace.get_workspace_object().settings.entries.pop(name)
        return super().destroy()

    T = TypeVar("T", bound=ValuedControl)

    def add_in_port(
        self,
        name: str,
        max_edges=64,
        display_name=None,
        control_type: type[T] = NullControl,
        control_name=None,
        restore_from: str | None | Literal[False] = None,
        **control_kwargs,
    ) -> InputPort[T]:
        """
        Add an input port to the node.
        If control_type is not None, a control will be added to the port. It must be a subclass of ValuedControl.
        When no edges are connected to the port, the control will be used to get the data.
        """
        if control_name is None:
            control_name = name
        id = f"{self.get_id()}_ip_{name}"  # specify id so it can be restored with the same id
        port = self.add_child(
            InputPort,
            control_type=control_type,
            name=name,
            max_edges=max_edges,
            display_name=display_name,
            control_name=control_name,
            id=id,
            **control_kwargs,
        )
        self.in_ports.insert(port)
        if control_type is not NullControl:
            if restore_from is None:
                self.restore_controls(name)
            elif restore_from is False:
                pass
            else:
                self.restore_controls((restore_from, name))
        return port

    def add_out_port(self, name: str, max_edges=64, display_name=None):
        """
        Add an output port to the node.
        """
        id = f"{self.get_id()}_op_{name}"  # specify id so it can be restored with the same id
        port = self.add_child(
            OutputPort, name=name, max_edges=max_edges, display_name=display_name, id=id
        )
        self.out_ports.insert(port)
        return port

    def remove_in_port(self, name: str):
        """
        Remove an input port from the node.
        """
        # find the port with the given name
        for port in self.in_ports:
            assert port is not None
            if port.name.get() == name:
                break
        else:
            raise ValueError(f"Port with name {name} does not exist")

        # remove all edges connected to the port
        for edge in port.edges[:]:
            edge.remove()  # do this in port.remove()?

        # remove the port
        self.in_ports.remove(port)
        port.remove()

    def remove_out_port(self, name: str):
        """
        Remove an output port from the node.
        """
        # find the port with the given name
        for port in self.out_ports:
            assert port is not None
            if port.name.get() == name:
                break
        else:
            raise ValueError(f"Port with name {name} does not exist")

        # remove all edges connected to the port
        for edge in port.edges[:]:
            edge.remove()  # do this in port.remove()?

        # remove the port
        self.out_ports.remove(port)
        port.remove()

    def get_in_port(self, name: str) -> InputPort:
        """
        Get an input port by its name.
        """
        for port in self.in_ports:
            assert port is not None
            if port.name.get() == name:
                return port
        raise ValueError(f"Port with name {name} does not exist")

    def get_out_port(self, name: str) -> OutputPort:
        """
        an output port by its name.
        """
        for port in self.out_ports:
            assert port is not None
            if port.name.get() == name:
                return port
        raise ValueError(f"Port with name {name} does not exist")

    def has_in_port(self, name: str) -> bool:
        """
        Check if an input port exists.
        """
        for port in self.in_ports:
            assert port is not None
            if port.name.get() == name:
                return True
        return False

    def has_out_port(self, name: str) -> bool:
        """
        Check if an output port exists.
        """
        for port in self.out_ports:
            assert port is not None
            if port.name.get() == name:
                return True
        return False

    T = TypeVar("T", bound=Control)

    def add_control(
        self,
        control_type: type[T],
        name: str | None = None,
        restore_from: str | None | Literal[False] = None,
        **kwargs,
    ) -> T:
        """
        Add a control to the node.
        """
        if name is not None:
            if name in self.controls:
                raise ValueError(f"Control with name {name} already exists")
        else:
            if control_type not in [ButtonControl] and restore_from is not False:
                warn_no_control_name(control_type, self)
            name = "Control0"
            i = 0
            while name in self.controls:
                i += 1
                name = f"Control{i}"

        id = f"{self.get_id()}_c_{name}"  # specify id so it can be restored with the same id
        control = self.add_child(control_type, id=id, **kwargs)
        self.controls.add(name, control)

        # restore the control
        if restore_from is None:
            self.restore_controls(name)
        elif restore_from is False:
            pass
        else:
            self.restore_controls((restore_from, name))

        return control

    def add_text_control(
        self,
        text: str = "",
        label: str = "",
        readonly=False,
        editable: bool = True,
        name: str | None = None,
        placeholder: str = "",
    ) -> TextControl:
        """
        Add a text control to the node.
        """
        control = self.add_control(
            TextControl,
            text=text,
            label=label,
            readonly=readonly,
            editable=editable,
            name=name,
            placeholder=placeholder,
        )
        return control

    def add_button_control(
        self, label: str = "", name: str | None = None
    ) -> ButtonControl:
        """
        Add a button control to the node.
        """
        control = self.add_control(ButtonControl, label=label, name=name)
        return control

    def add_image_control(self, name: str | None = None) -> ImageControl:
        """
        Add an image control to the node.
        """
        control = self.add_control(ImageControl, name=name)
        return control

    def add_lineplot_control(self, name: str | None = None) -> LinePlotControl:
        """
        Add a line plot control to the node.
        """
        control = self.add_control(LinePlotControl, name=name)
        return control

    def add_option_control(
        self, value: str, options: list[str], label: str = "", name: str | None = None
    ) -> OptionControl:
        """
        Add an option control to the node.
        """
        control = self.add_control(
            OptionControl, value=value, options=options, label=label, name=name
        )
        return control

    def remove_control(self, control: str | Control):
        if isinstance(control, str):
            control = self.controls[control]
        self.controls.remove(control)
        control.remove()

    # Wrap the SObject.addattribute() to make shorthand of exposing attributes after adding them.
    T1 = TypeVar("T1", bound=Topic | WrappedTopic)

    def add_attribute(
        self,
        topic_name: str,
        topic_type: type[T1],
        init_value=None,
        is_stateful=True,
        editor_type: str | None = None,
        display_name: str | None = None,
        target: Literal["self", "global"] = "self",
        order_strict: bool | None = None,
        restore_from: str | None | Literal[False] = None,
        **editor_args,
    ) -> T1:
        """
        Add an attribute to the node.

        Args:
            - topic_name: The name of the attribute. Has to be unique in the node.
            - topic_type: The type of the attribute. Can be one of the following: StringTopic, IntTopic, FloatTopic, ListTopic, DictTopic, SetTopic, ObjTopic, ObjListTopic, ObjDictTopic, ObjSetTopic.
            - init_value: The initial value of the attribute. If set to None, the attribute will be initialized with the default value of the topic type.
            - is_stateful: If set to True, the changes to the attribute will be stored in the history and can be undone or redone. If set to False, the changes will not be stored.
            - editor_type, display_name, target, and editor_args: If editor_type is not None, the attribute will be exposed to the inspector. Please see Node.expose_attribute() for details.
            - order_strict: If set to True, the changes to the attribute won't be merged or reordered with other changes for communication efficiency. If set to None, it will be set to the same as is_stateful.
            - restore_from: The name of the attribute to restore from. If set to None, the attribute will restore from the attribute with the same name in the old node. If set to False, the attribute will not be restored. To restore an attribute based on different source version, see Node.restore().
        """

        if order_strict is None:
            order_strict = is_stateful

        attribute = super().add_attribute(
            topic_name, topic_type, init_value, is_stateful, order_strict=order_strict
        )
        if editor_type is not None:
            self.expose_attribute(
                attribute, editor_type, display_name, target=target, **editor_args
            )
        if restore_from is None:
            self.restore_attributes(topic_name)
        elif restore_from is False:
            pass
        else:
            self.restore_attributes((restore_from, topic_name))
        return attribute

    def expose_attribute(
        self,
        attribute: Topic | WrappedTopic,
        editor_type,
        display_name=None,
        target: Literal["self", "global"] = "self",
        **editor_args,
    ):
        """
        Expose an attribute to the inspector.

        Args:
            - attribute: The attribute to expose.

            - editor_type: The type of the editor to use. Can be ``text`` or ``list``.

            - display_name: The name to display in the editor. If not specified, the attribute's name will be used.

            - target: The target of the attribute. Can be ``self`` or ``global``. If set to ``self``, the attribute will be exposed to the inspector of the node. If set to ``global``, the attribute will be exposed to the global settings tab.

            - **editor_args: The arguments to pass to the editor. See below for details.


        There are 2 ways to expose an attribute:
        1. Call this method. For example:
            ```
            my_attr = self.add_attribute('my_attr',ListTopic,[])
            self.expose_attribute(my_attr,'list')
            ```
        2. Call the `add_attribute` method with the `editor_type` argument. For example:
            ```
            my_attr = self.add_attribute('my_attr',ListTopic,[],editor_type='list')
            ```

        Both ways are equivalent.

        List of editor types:
            - ``dict``: A dictionary editor. Goes with a DictTopic. editor_args:

            ```
            {
                'key_options':list[str]|None,
                'value_options':list[str]|None,
                'key_strict':bool|None,
                'value_strict':bool|None,
            }
            ```

            - ``list``: A list editor. Goes with a ListTopic. editor_args: `{}`

            - ``options``: A dropdown editor. Goes with a StringTopic. editor_args:

            ```
            {
                'options':list[str],
            }
            ```

            - ``text``: A text editor. Goes with a StringTopic. editor_args: `{}`

            - ``int``: An integer editor. Goes with an IntTopic. editor_args: `{}`

            - ``float``: A float editor. Goes with a FloatTopic. editor_args: `{}`
        """
        if editor_args is None:  # not stepping into the dangerous trap of Python :D
            editor_args = {}
        name = attribute.get_name()
        if display_name is None:
            display_name = name.split("/")[-1]
        editor_args["type"] = editor_type

        if target == "self":
            self.exposed_attributes.insert(
                {"name": name, "display_name": display_name, "editor_args": editor_args}
            )
        elif target == "global":
            self.globally_exposed_attributes.add(
                name,
                {
                    "name": name,
                    "display_name": display_name,
                    "editor_args": editor_args,
                },
            )

    def print(self, *args, **kwargs):
        """
        Print to the node's output.
        """
        # print(*args,**kwargs,file=self._output_stream)
        # self._output_stream.flush()

        # maybe the self._output_stream can be abandoned
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()

        self.raw_print(contents)

    def raw_print(self, data):
        if data == "":
            return
        if self.is_destroyed():
            logger.debug(
                f"Output received from a destroyed node {self.get_id()}: {data}"
            )
        else:
            if len(self.output) > 100:
                self.output.set([])
                self.output.insert(["error", "Too many output lines. Cleared.\n"])
            self.output.insert(["output", data])

    """
    Run tasks in the background or foreground, redirecting stdout to the node's output stream.
    """

    @contextmanager
    def _redirect_output(self):
        """
        Returns a context manager that redirects stdout to the node's output stream.
        """

        try:
            self._output_stream.enable_flush()
            with self.workspace.redirect(self._output_stream):
                yield
        finally:
            self._output_stream.disable_flush()

    def _run_in_background(
        self, task: Callable[[], None], to_queue=True, redirect_output=False
    ):
        """
        Run a task in the background thread.
        """

        def exception_callback(e):
            self.print_exception(e, truncate=3)
            if isinstance(e, KeyboardInterrupt):
                self.workspace.send_message_to_all("Runner interrupted by user.")
            self.workspace.background_runner.set_exception_callback(None)
            self.workspace.clear_edges()

        def wrapped():
            self.set_running(True)
            self.workspace.background_runner.set_exception_callback(exception_callback)
            if redirect_output:
                with self._redirect_output():
                    ret = task()
            else:
                ret = task()
            self.set_running(False)
            self.workspace.background_runner.set_exception_callback(None)
            return ret

        self.workspace.background_runner.push(wrapped, to_queue=to_queue)

    def _run_directly(self, task: Callable[[], None], redirect_output=False):
        """
        Run a task in the current thread.
        """
        self.set_running(True)
        try:
            if redirect_output:
                with self._redirect_output():
                    task()
            else:
                task()
        except Exception as e:
            self.print_exception(e, truncate=1)
        self.set_running(False)

    def run(
        self,
        task: Callable,
        background=True,
        to_queue=True,
        redirect_output=False,
        *args,
        **kwargs,
    ):
        """
        Run a task in the node's context i.e. the stdout and errors will be redirected to the node's output attribute and be displayed in front-end.

        Args:
            - task: The task to run.

            - background: If set to True, the task will be scheduled to run in the background thread. Otherwise, it will be run in the current thread immediately.

            - to_queue: This argument is used only when `background` is True. If set to True, the task will be pushed to the :class:`.BackgroundRunner`'s queue.\
            If set to False, the task will be pushed to its stack. See :class:`.BackgroundRunner` for more details.
        """
        task = functools.partial(task, *args, **kwargs)
        if background:
            self._run_in_background(task, to_queue, redirect_output=False)
        else:
            self._run_directly(task, redirect_output=False)

    def print_exception(self, e, truncate=0):
        message = "".join(traceback.format_exception(e)[truncate:])
        if self.is_destroyed():
            logger.warning(
                f"Exception occured in a destroyed node {self.get_id()}: {message}"
            )
        else:
            self.set_running(False)
            if len(self.output) > 100:
                self.output.set([])
                self.output.insert(["error", "Too many output lines. Cleared.\n"])
            self.output.insert(["error", message])

    def flash_running_indicator(self):
        self.set_running(True)
        self.set_running(False)

    def set_running(self, running: bool):
        with self._server.record(
            allow_reentry=True
        ):  # aquire the lock to prevent setting the attribute while the sobject being deleted
            if self.is_destroyed():
                return
            if running:
                self.running.set(0)
            else:
                self.running.set(random.randint(0, 10000))

    """
    Node events
    """

    def edge_activated(self, edge: Edge | ValuedControl, port: InputPort):
        """
        Called when an edge on an input port is activated.
        """
        pass

    def input_edge_added(self, edge: Edge, port: InputPort):
        """
        Called when an edge is added to an input port.
        """
        pass

    def input_edge_removed(self, edge: Edge, port: InputPort):
        """
        Called when an edge is removed from an input port.
        """
        pass

    def output_edge_added(self, edge: Edge, port: OutputPort):
        """
        Called when an edge is added to an output port.
        """
        pass

    def output_edge_removed(self, edge: Edge, port: OutputPort):
        """
        Called when an edge is removed from an output port.
        """
        pass

    def double_click(self):
        """
        Called when the node is double clicked by an user.
        """
        pass
