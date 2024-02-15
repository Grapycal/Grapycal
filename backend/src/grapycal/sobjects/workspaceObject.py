import logging

logger = logging.getLogger("WORKSPACE")
from typing import Any, Dict, Self
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.fileView import FileView, LocalFileView, RemoteFileView
from grapycal.sobjects.node import Node
from grapycal.sobjects.sidebar import Sidebar
from grapycal.sobjects.settings import Settings
from objectsync import (
    SObject,
    ObjTopic,
    SObjectSerialized,
    StringTopic,
    IntTopic,
    Topic,
    WrappedTopic,
)


class WorkspaceObject(SObject):
    frontend_type = "Workspace"
    ins: Self

    def build(self, old: SObjectSerialized | None = None):
        from grapycal.core.workspace import Workspace

        self._workspace: Workspace = self._server.globals.workspace
        WorkspaceObject.ins = self
        if old is None:
            self.settings = self.add_child(Settings)
            self.webcam = self.add_child(WebcamStream)
            self.sidebar = self.add_child(Sidebar)
            self.main_editor = self.add_child(Editor)
        else:
            if old.has_child("settings"):
                self.settings = self.add_child(Settings, old=old.get_child("settings"))
            else:
                self.settings = self.add_child(Settings)
            if old.has_child("webcam"):
                self.webcam = self.add_child(WebcamStream, old=old.get_child("webcam"))
            else:
                self.webcam = self.add_child(WebcamStream)
            self.sidebar = self.add_child(Sidebar, old=old.get_child("sidebar"))

            if old.has_child("main_editor"):
                self.main_editor = self.add_child(
                    Editor, old=old.get_child("main_editor")
                )
            else:
                self.main_editor = self.add_child(
                    Editor, old=old.children[old.get_attribute("main_editor")]
                )

        # Add local file view and remote file view
        self.file_view = self.add_child(LocalFileView, name="Local Files 💻")

        async def add_examples_file_view():
            if not await self._workspace.data_yaml.is_avaliable():
                logger.info("Cannot get example files from GitHub.")
                return  # no internet connection
            data_yaml = await self._workspace.data_yaml.get()

            self.add_child(
                RemoteFileView, url=data_yaml["examples_url"], name="Examples💡"
            )
            self._server.clear_history()

        self._workspace.add_task_to_event_loop(add_examples_file_view())

        # read by frontend
        self.add_attribute("main_editor", ObjTopic).set(self.main_editor)


class WebcamStream(SObject):
    frontend_type = "WebcamStream"

    def build(self, old: SObjectSerialized | None = None):
        self.image = self.add_attribute("image", StringTopic, is_stateful=False)
        self.source_client = self.add_attribute(
            "source_client", IntTopic, -1, is_stateful=False
        )

    def init(self):
        self.source_client.set(-1)
        self._server.globals.workspace.webcam = self
