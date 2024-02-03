
from grapycal import Node
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.node import singletonNode
from objectsync import StringTopic

@singletonNode()
class SettingsNode(Node):
    def build_node(self):
        # TODO: discorver devices on the machine
        self.default_device = self.add_attribute("default device", StringTopic, "cpu", editor_type="options", options=["cpu", "cuda"],target='global',display_name='torch/default device')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes("default device")