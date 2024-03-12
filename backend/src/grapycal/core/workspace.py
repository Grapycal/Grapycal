from enum import Enum
import os
import time
import grapycal
from grapycal.core.slash_command import SlashCommandManager
from grapycal.extension.extensionManager import ExtensionManager
from grapycal.extension.utils import Clock
from grapycal.sobjects.controls.linePlotControl import LinePlotControl
from grapycal.sobjects.controls.nullControl import NullControl
from grapycal.sobjects.controls.optionControl import OptionControl
from grapycal.sobjects.controls.threeControl import ThreeControl
from grapycal.sobjects.fileView import LocalFileView, RemoteFileView
from grapycal.sobjects.settings import Settings
from grapycal.sobjects.controls import *
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.workspaceObject import WebcamStream, WorkspaceObject
from grapycal.utils.httpResource import HttpResource
from grapycal.utils.io import file_exists, read_workspace, write_workspace

from grapycal.utils.logging import setup_logging

setup_logging()
import logging

logger = logging.getLogger("workspace")

from typing import Any, Callable, Dict

import threading
import objectsync
from objectsync.sobject import SObjectSerialized
import asyncio
import signal
from dacite import from_dict
import importlib.metadata


from grapycal.core import stdout_helper


from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.sobjects.sidebar import Sidebar

from grapycal.core.background_runner import BackgroundRunner
from grapycal.sobjects.node import Node

from grapycal.core import running_module


class ClientMsgTypes:
    STATUS = "status"
    NOTIFICATION = "notification"
    BOTH = "both"


class Workspace:
    def __init__(self, port, host, path, workspace_id) -> None:
        self.path = path
        self.port = port
        self.host = host
        self.workspace_id = workspace_id # used for exit message file
        self.running_module = running_module
        """"""

        """
        Enable stdout proxy for this process
        """
        stdout_helper.enable_proxy(redirect_error=False)
        self.redirect = stdout_helper.redirect

        self._communication_event_loop: asyncio.AbstractEventLoop | None = None

        self.background_runner = BackgroundRunner()

        self._objectsync = objectsync.Server(port, host)

        self._extention_manager = ExtensionManager(self._objectsync, self)

        self.do_after_transition = self._objectsync.do_after_transition

        self.clock = Clock(0.1)

        self.webcam: WebcamStream | None = None
        self._slash_commands_topic = self._objectsync.create_topic("slash_commands", objectsync.DictTopic)
        self.slash = SlashCommandManager(self._slash_commands_topic)

        self.slash.register("save workspace", lambda: self.save_workspace(self.path))
        
        self.data_yaml = HttpResource(
            "https://github.com/Grapycal/grapycal_data/raw/main/data.yaml", dict
        )

        self.grapycal_id_count = 0
        self.is_running = False

    def _communication_thread(self, event_loop_set_event: threading.Event):
        asyncio.run(self._async_communication_thread(event_loop_set_event))

    async def _async_communication_thread(self, event_loop_set_event: threading.Event):
        self._communication_event_loop = asyncio.get_event_loop()
        event_loop_set_event.set()
        try:
            await asyncio.gather(self._objectsync.serve(), self.clock.run())
        except OSError as e:
            if e.errno == 10048:
                logger.error(
                    f"Port {self.port} is already in use. Maybe another instance of grapycal is running?"
                )
                self.get_communication_event_loop().stop()
                # send signal to the main thread to exit
                os.kill(os.getpid(), signal.SIGTERM)
            else:
                raise e

    def run(self) -> None:
        event_loop_set_event = threading.Event()
        t = threading.Thread(
            target=self._communication_thread, daemon=True, args=[event_loop_set_event]
        )  # daemon=True until we have a proper exit strategy

        t.start()
        event_loop_set_event.wait()

        self._extention_manager.start()

        self._objectsync.globals.workspace = self

        self._objectsync.register_service("exit", self.exit)
        self._objectsync.register_service("interrupt", self.interrupt)

        self._objectsync.register(WorkspaceObject)
        self._objectsync.register(Editor)
        self._objectsync.register(Sidebar)
        self._objectsync.register(Settings)
        self._objectsync.register(LocalFileView)
        self._objectsync.register(RemoteFileView)
        self._objectsync.register(InputPort)
        self._objectsync.register(OutputPort)
        self._objectsync.register(Edge)

        self._objectsync.register(TextControl)
        self._objectsync.register(ButtonControl)
        self._objectsync.register(ImageControl)
        self._objectsync.register(ThreeControl)
        self._objectsync.register(NullControl)
        self._objectsync.register(OptionControl)

        self._objectsync.register(WebcamStream)
        self._objectsync.register(LinePlotControl)

        """
        Register all built-in node types
        """

        signal.signal(signal.SIGTERM, lambda sig, frame: self.exit())

        if file_exists(self.path):
            logger.info(f"Found existing workspace file {self.path}. Loading.")
            self.load_workspace(self.path)
        else:
            logger.info(
                f"No workspace file found at {self.path}. Creating a new workspace to start with."
            )
            self.initialize_workspace()

        # creates the status message topic so client can subscribe to it
        self._objectsync.on_client_connect += self.client_connected
        self._objectsync.on_client_disconnect += self.client_disconnected
        self._objectsync.create_topic(
            f"status_message", objectsync.EventTopic, is_stateful=False
        )
        import grapycal.utils.logging

        grapycal.utils.logging.send_client_msg = self.send_message_to_all

        self._objectsync.create_topic(
            "meta", objectsync.DictTopic, {"workspace name": self.path}
        )

        if not file_exists(self.path):
            self.save_workspace(
                self.path
            )  # this line uses status_message, so should be after the topic is created

        self._objectsync.on(
            "ctrl+s", lambda: self.save_workspace(self.path), is_stateful=False
        )
        self._objectsync.on(
            "open_workspace", self._open_workspace_callback, is_stateful=False
        )

        self._objectsync.register_service("slash_command", self.slash.call)

        self.is_running = True

        self.background_runner.run()

    def exit(self):
        self.background_runner.exit()

    def interrupt(self):
        self.background_runner.interrupt()
        self.background_runner.clear_tasks()

    def get_communication_event_loop(self) -> asyncio.AbstractEventLoop:
        assert self._communication_event_loop is not None
        return self._communication_event_loop

    """
    Save and load
    """

    def initialize_workspace(self) -> None:
        self._objectsync.create_object(WorkspaceObject, parent_id="root")
        try:
            self._extention_manager.import_extension("grapycal_builtin")
        except ModuleNotFoundError:
            pass

    def save_workspace(self, path: str) -> None:
        workspace_serialized = self.get_workspace_object().serialize()

        metadata = {
            "version": grapycal.__version__,
            "extensions": self._extention_manager.get_extensions_info(),
        }
        data = {
            "extensions": self._extention_manager.get_extention_names(),
            "client_id_count": self._objectsync.get_client_id_count(),
            "id_count": self._objectsync.get_id_count(),
            "grapycal_id_count": self.grapycal_id_count,
            "workspace_serialized": workspace_serialized.to_dict(),
        }
        file_size = write_workspace(path, metadata, data, compress=True)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        node_count = len(
            self.get_workspace_object().main_editor.top_down_search(type=Node)
        )
        edge_count = len(
            self.get_workspace_object().main_editor.top_down_search(type=Edge)
        )
        logger.info(
            f"Workspace saved to {path}. Node count: {node_count}. Edge count: {edge_count}. File size: {file_size//1024} KB."
        )
        self.send_message_to_all(
            f"Workspace saved to {path}. Node count: {node_count}. Edge count: {edge_count}. File size: {file_size//1024} KB."
        )

    def load_workspace(self, path: str) -> None:
        version, metadata, data = read_workspace(path)

        self._check_grapycal_version(version)
        if (
            "extensions" in metadata
        ):  # DEPRECATED from v0.10.0: v0.9.0 and before has no extensions in metadata
            self._check_extensions_version(metadata["extensions"])

        self._objectsync.set_client_id_count(data["client_id_count"])
        self._objectsync.set_id_count(data["id_count"])
        if (
            "grapycal_id_count" in data
        ):  # DEPRECATED from v0.11.0: v0.10.0 and before has no grapycal_id_count
            self.grapycal_id_count = data["grapycal_id_count"]
        else:
            # we cannot know the exact value of grapycal_id_count, so we set it to 032.5, which will never collide. Very smart 🤯
            self.grapycal_id_count = 032.5
        workspace_serialized = from_dict(
            SObjectSerialized, data["workspace_serialized"]
        )

        # DEPRECATED from v0.10.0: The old format of attributes is [name, type, value, value].
        def resolve_deprecated_attr_format(obj: SObjectSerialized):
            for attr in obj.attributes:
                if attr.__len__() == 4:
                    attr.append(attr[3])
            for child in obj.children.values():
                resolve_deprecated_attr_format(child)

        resolve_deprecated_attr_format(workspace_serialized)

        for extension_name in data["extensions"]:
            self._extention_manager.import_extension(extension_name, create_nodes=False)

        self._objectsync.create_object(
            WorkspaceObject,
            parent_id="root",
            old=workspace_serialized,
            id=workspace_serialized.id,
        )

        for extension_name in data["extensions"]:
            self._extention_manager.create_preview_nodes(extension_name)
            self._extention_manager._instantiate_singletons(extension_name)

        self._objectsync.clear_history_inclusive()

    def _check_grapycal_version(self, version: str):
        # check if the workspace version is compatible with the current version
        workspace_version_tuple = tuple(map(int, version.split(".")))
        current_version_tuple = tuple(map(int, grapycal.__version__.split(".")))
        if current_version_tuple < workspace_version_tuple:
            logger.warning(
                f"Attempting to downgrade workspace from version {version} to {grapycal.__version__}. This may cause errors."
            )

    def _check_extensions_version(self, extensions_info):
        # check if all extensions version are compatible with the current version
        for extension_info in extensions_info:
            extension_version_tuple = tuple(
                map(int, extension_info["version"].split("."))
            )
            try:
                current_version_tuple = tuple(
                    map(
                        int,
                        importlib.metadata.version(extension_info["name"]).split("."),
                    )
                )
            except importlib.metadata.PackageNotFoundError:
                continue  # ignore extensions that are not installed
            if current_version_tuple < extension_version_tuple:
                logger.warning(
                    f'Attempting to downgrade extension {extension_info["name"]} from version {extension_info["version"]} to {importlib.metadata.version(extension_info["name"])}. This may cause errors.'
                )

    def get_workspace_object(self) -> WorkspaceObject:
        # In case this called in self._objectsync.create_object(WorkspaceObject),
        return self._objectsync.get_root_object().get_child_of_type(WorkspaceObject)

    def vars(self) -> Dict[str, Any]:
        return self.running_module.__dict__

    def _open_workspace_callback(self, path, no_exist_ok=False):
        if not no_exist_ok:
            if not os.path.exists(path):
                raise Exception(f"File {path} does not exist")
        if not path.endswith(".grapycal"):
            raise Exception(f"File {path} does not end with .grapycal")

        logger.info(f"Opening workspace {path}...")
        self.send_message_to_all(f"Opening workspace {path}...")

        exit_message_file = f"grapycal_exit_message_{self.workspace_id}"
        with open(exit_message_file, "w") as f:
            f.write(f"open {path}")
        self.exit()

    def add_task_to_event_loop(self, task):
        self._communication_event_loop.create_task(task)

    def send_message_to_all(self, message, type=ClientMsgTypes.NOTIFICATION):
        if not self.is_running:
            return
        if type == ClientMsgTypes.BOTH:
            self.send_message_to_all(message, ClientMsgTypes.NOTIFICATION)
            self.send_message_to_all(message, ClientMsgTypes.STATUS)

        self._objectsync.emit("status_message", message=message, type=type)

    def send_message(self, message, client_id=None, type=ClientMsgTypes.NOTIFICATION):
        if not self.is_running:
            return
        if type == ClientMsgTypes.BOTH:
            self.send_message(message, ClientMsgTypes.NOTIFICATION)
            self.send_message(message, ClientMsgTypes.STATUS)
        if client_id is None:
            client_id = self._objectsync.get_action_source()
        self._objectsync.emit(f"status_message_{client_id}", message=message, type=type)

    def client_connected(self, client_id):
        self._objectsync.create_topic(
            f"status_message_{client_id}", objectsync.EventTopic
        )

    def client_disconnected(self, client_id):
        try:
            self._objectsync.remove_topic(f"status_message_{client_id}")
        except:
            pass  # topic may have not been created successfully.

    def next_id(self):
        self.grapycal_id_count += 1
        return self.grapycal_id_count

    def clear_edges(self):
        edges = self.get_workspace_object().top_down_search(type=Edge)
        for edge in edges:
            edge.clear_data()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--path", type=str, default="workspace.grapycal")
    parser.add_argument("--workspace_id", type=int, default=0)
    args = parser.parse_args()

    workspace = Workspace(args.port, args.host, args.path, args.workspace_id)
    workspace.run()
