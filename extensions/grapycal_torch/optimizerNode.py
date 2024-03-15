from typing import TYPE_CHECKING, List
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.controls.buttonControl import ButtonControl
from grapycal.sobjects.controls.optionControl import OptionControl
from grapycal.sobjects.controls.textControl import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.functionNode import FunctionNode
from grapycal.sobjects.node import Node, deprecated
from grapycal.sobjects.port import InputPort
from grapycal import FloatTopic, StringTopic
from objectsync import ObjSetTopic, SObject
import torch
from torch import nn

from .utils import setup_net_name_ctrl
from .moduleNode import ModuleNode

if TYPE_CHECKING:
    from grapycal_torch import GrapycalTorch


@deprecated("Use TrainNode instead.", "0.3.0", "0.4.0")
class TrainerNode(Node):
    ext: "GrapycalTorch"
    category = "torch/training"

    def build_node(self):
        self.label.set("Trainer")
        self.css_classes.append("fit-content")
        self.lr = self.add_attribute("lr", FloatTopic, 0.001, editor_type="float")
        self.device = self.add_in_port("device", control_type=TextControl)
        self.network_names = self.add_in_port("network names", control_type=TextControl)
        self.init_modules_port = self.add_in_port(
            "initialize network", control_type=ButtonControl
        )

        self.train_port = self.add_in_port("train network using loss")

        self.train_mode_port = self.add_in_port(
            "switch to train mode", control_type=ButtonControl
        )
        self.eval_port = self.add_in_port(
            "switch to eval mode", control_type=ButtonControl
        )

    def init_node(self):
        self.optimizer: torch.optim.Optimizer | None = None
        self.tracked_modules: set[nn.Module] = set()

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes("lr", "device")
        self.restore_controls("network name")

    def get_module_nodes(self) -> List[ModuleNode]:
        result: List[ModuleNode] = []
        for name in self.network_names.get_one_data().split(","):
            mn = self.ext.net.get_module_nodes(name)
            result += mn
        return result

    def getModules(self) -> List[nn.Module]:
        return [mn.get_module() for mn in self.get_module_nodes()]

    def check_modules_to_track_changed(self):
        current_modules = set(self.getModules())
        if current_modules != self.tracked_modules:
            self.tracked_modules = current_modules
            self.optimizer = torch.optim.Adam(
                [p for m in self.tracked_modules for p in m.parameters()],
                lr=self.lr.get(),
            )
            self.print("recreated optimizer, ", len(self.tracked_modules), " modules")

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.train_port:
            self.run(self.train_step, loss=edge.get_data())
            return

        if port == self.init_modules_port:
            self.run(self.init_modules)
        elif port == self.eval_port:
            self.run(self.eval_mode)
        elif port == self.train_mode_port:
            self.run(self.train_mode)
        port.get_data()  # deactivates the edge

    def init_modules(self):
        for mn in self.get_module_nodes():
            mn.create_module_and_update_name()

    def step(self):
        self.check_modules_to_track_changed()
        if self.tracked_modules == set():
            raise Exception("No modules to optimize")
        self.optimizer.step()

    def train_step(self, loss: torch.Tensor):
        self.check_modules_to_track_changed()
        if self.tracked_modules == set():
            return
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def eval_mode(self):
        for m in self.tracked_modules:
            m.eval()
            m.requires_grad_(False)

    def train_mode(self):
        for m in self.tracked_modules:
            m.train()
            m.requires_grad_(True)


class TrainNode(Node):
    ext: "GrapycalTorch"
    category = "torch/training"

    def build_node(self):
        self.label.set("Train")
        self.css_classes.append("fit-content")
        self.network_port = self.add_in_port(
            "network", control_type=OptionControl
        )
        self.loss_port = self.add_in_port("loss", 1)

    def init_node(self):
        self.network_name = self.network_port.default_control.value
        self.to_unlink = setup_net_name_ctrl(
            self.network_port.default_control,self.ext, multi=True, set_value=self.is_new
        )
        self.optimizing_modules: set[nn.Module] = set()
        self.optimizer_device = None

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.loss_port:
            self.run(self.train_step, loss=edge.get_data())
            return
        if port == self.network_port:
            self.label.set("Train " + self.network_name.get())

    def get_module_nodes(self) -> List[ModuleNode]:
        names = self.network_name.get()
        res = []
        for name in names.split(","):
            if self.ext.net.has_network(name):
                res += self.ext.net.get_module_nodes(name)
            else:
                raise Exception(f"Network {name} does not exist.")
        return res

    def get_modules(self) -> List[nn.Module]:
        return [mn.get_module() for mn in self.get_module_nodes()]

    def create_optimizer_if_needed(self, loss_device):
        if (
            self.optimizing_modules != set(self.get_modules())
            or self.optimizer_device != loss_device
        ):
            self.optimizing_modules = set(self.get_modules())
            self.optimizer = torch.optim.Adam(
                [p for m in self.optimizing_modules for p in m.parameters()]
            )
            print("optimizer recreated", len(self.optimizing_modules), " modules")
            self.optimizer_device = loss_device

    def train_step(self, loss: torch.Tensor):
        self.create_optimizer_if_needed(loss.device)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def destroy(self):
        self.to_unlink()
        return super().destroy()


class SaveNode(Node):
    ext: "GrapycalTorch"
    category = "torch/training"

    def build_node(self):
        self.label.set("Save Network")
        self.network_port = self.add_in_port(
            "network", control_type=OptionControl, options=["net a", "net b"]
        )
        self.path_port = self.add_in_port("file", control_type=TextControl)
        self.save_port = self.add_in_port("save", control_type=ButtonControl)

    def init_node(self):
        self.to_unlink = setup_net_name_ctrl(self.network_port.default_control, self.ext,set_value=self.is_new)
        self.network_name = self.network_port.default_control.value
        self.path = self.path_port.default_control.text

        if self.is_new:
            self.path.set("network.pt")

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.save_port:
            self.run(self.save)
            port.get_one_data()

    def save(self):
        network_name = self.network_name.get()
        path = self.path.get()
        self.ext.net.save_network(network_name, path)
        self.workspace.send_message_to_all(f"Saved {network_name} to {path}.")

    def destroy(self):
        self.to_unlink()
        return super().destroy()


class LoadNode(Node):
    ext: "GrapycalTorch"
    category = "torch/training"

    def build_node(self):
        self.label.set("Load Network")
        self.network_port = self.add_in_port(
            "network", control_type=OptionControl, options=["net a", "net b"]
        )
        self.path_port = self.add_in_port("file", control_type=TextControl)
        self.load_port = self.add_in_port("load", control_type=ButtonControl)

    def init_node(self):
        self.to_unlink = setup_net_name_ctrl(self.network_port.default_control, self.ext,set_value=self.is_new)
        self.network_name = self.network_port.default_control.value
        self.path = self.path_port.default_control.text

        if self.is_new:
            self.path.set("network.pt")

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.load_port:
            self.run(self.load)
            port.get_one_data()

    def load(self):
        network_name = self.network_name.get()
        path = self.path.get()
        try:
            self.ext.net.load_network(network_name, path, self)
        except Exception as e:
            self.print_exception(e,-1)
            return
        self.workspace.send_message_to_all(f"Loaded {network_name} from {path}.")

    def destroy(self):
        self.to_unlink()
        return super().destroy()
