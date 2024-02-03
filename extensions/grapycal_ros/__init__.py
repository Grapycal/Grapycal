import enum
import io
import json
from typing import Any, Dict, List
from grapycal import Node, Edge, InputPort, TextControl, ButtonControl, IntTopic, FunctionNode, SetTopic, StringTopic, ListTopic, DictTopic
from grapycal.core.workspace import Workspace
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.controls.imageControl import ImageControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from objectsync.sobject import SObjectSerialized
import websockets
from websockets.sync.client import connect


class RosbridgeNode(Node):
    class Status(enum.Enum):
        NOT_CONNECTED = 0
        CONNECTING = 1
        CONNECTED = 2
        DISCONNECTING = 3

    category = 'ros'

    def build_node(self):
        self.label.set('Rosbridge')
        self.url = self.add_text_control('localhost:9090','ws://',name='url')
        self.connect_btn = self.add_button_control('Connect',name='connect')
        self.send_port = self.add_in_port('send')
        self.recv_port = self.add_out_port('recv')
        self.subs_info = self.add_attribute('subs_info', DictTopic, {}, editor_type='dict',key_options=['aaa0','aab'],value_options=['vads,asde'],key_strict=True) # internal use only. data: {'name':str,'type':str}
        self.subsciptions = self.add_attribute('subsciptions', ListTopic, [], editor_type='list') # for user to manipulate
        self.subscription_type = self.add_attribute('subscription type', StringTopic, 'std_msgs/String',editor_type='options',
            options=['std_msgs/String','std_msgs/Int32','std_msgs/Float32','std_msgs/Bool','sensor_msgs/Image',
            'sensor_msgs/msg/JointState'
            ])
        
    def init_node(self):
        self.status = RosbridgeNode.Status.NOT_CONNECTED
        self.connect_btn.on_click += self.connect_clicked
        self.connect_btn.label.set('Connect')

        def link_subsciptions_to_subs_info():
            self.subsciptions.on_insert.add_auto(lambda topic_name,_: self.subs_info.add(topic_name, self.subscription_type.get()))
            self.subsciptions.on_pop.add_auto(lambda topic_name,_: self.subs_info.pop(topic_name))
        self._server.do_after_transition(link_subsciptions_to_subs_info)

        self.subs_info.on_add.add_auto(self.on_subscription_add1)
        self.subs_info.on_add += self.on_subscription_add2
        self.subs_info.on_remove.add_auto(self.on_subscription_remove1)
        self.subs_info.on_remove += self.on_subscription_remove2

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('url')
        self.restore_attributes('subs_info','subscription type','subsciptions')

    def on_subscription_add1(self, topic_name,_):
        self.add_out_port(topic_name)

    def on_subscription_add2(self, topic_name, topic_type):
        if self.status != RosbridgeNode.Status.CONNECTED:
            return
        self.send(json.dumps({
            'op': 'subscribe',
            'topic': topic_name,
            'type': topic_type
        }))

    def on_subscription_remove1(self, topic_name):
        self.remove_out_port(topic_name)

    def on_subscription_remove2(self, topic_name):
        if self.status != RosbridgeNode.Status.CONNECTED:
            return
        self.send(json.dumps({
            'op': 'unsubscribe',
            'topic': topic_name,
        }))

    def connect_clicked(self):
        if self.status == RosbridgeNode.Status.CONNECTED:
            self.status = RosbridgeNode.Status.DISCONNECTING
            self.connect_btn.label.set('Disonnecting...')
            self.run(self.disconnect)
        elif self.status == RosbridgeNode.Status.NOT_CONNECTED:
            self.status = RosbridgeNode.Status.CONNECTING
            self.connect_btn.label.set('Connecting...')
            self.run(self.connect)
        else:
            return

    def connect(self):
        self.ws = connect('ws://'+self.url.get())
        self.connect_btn.label.set('Disconnect')
        self.url.editable.set(False)
        self.status = RosbridgeNode.Status.CONNECTED
        self.workspace.clock.on_tick += self.on_tick

        for topic_name,topic_type in self.subs_info.get().items():
            self.send(json.dumps({
                'op': 'subscribe',
                'topic': topic_name,
                'type': topic_type
            }))

    def disconnect(self):
        self.ws.close()
        self.workspace.clock.on_tick -= self.on_tick
        self.url.editable.set(True)
        self.status = RosbridgeNode.Status.NOT_CONNECTED
        self.connect_btn.label.set('Connect')
        

    def on_tick(self):
        if self.status != RosbridgeNode.Status.CONNECTED:
            return
        msgs = []
        while True:
            try:
                # The 0.00001 (instead of 0) is required to recieve multiple messages in one tick.
                # Maybe it's a bug of websockets.
                msg = self.ws.recv(0.00001)
            except TimeoutError:
                break
            except Exception as e:
                self.connection_error(e)
                break
            msgs.append(msg)
            
        for msg in msgs:
            self.on_recv_msg(msg)
        
    def on_recv_msg(self, msg_str: str):
        self.recv_port.push_data(msg_str)
        self.flash_running_indicator()

        msg = json.loads(msg_str)
        if msg['op'] == 'publish':
            topic_name = msg['topic']
            if self.has_out_port(topic_name):
                self.get_out_port(topic_name).push_data(msg['msg'])

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.send_port:
            if self.status != RosbridgeNode.Status.CONNECTED:
                return
            msg = edge.get_data()
            if not isinstance(msg, str):
                msg = json.dumps(msg)
            self.ws.send(msg)
            
    def send(self, msg: str):
        if self.status != RosbridgeNode.Status.CONNECTED:
            raise Exception('Not connected')
        try:
            self.ws.send(msg)
        except Exception as e:
            self.connection_error(e)
            return
            
    def connection_error(self,e:Exception):
        self.disconnect()
        self.print_exception(e)

    def destroy(self) -> SObjectSerialized:
        if self.status == RosbridgeNode.Status.CONNECTED:
            self.disconnect()
        return super().destroy()

class CounterNode(Node):
    category = 'demo'

    def build_node(self):
        self.text = self.add_text_control('0')
        self.button = self.add_button_control('Add')
        self.i = self.add_attribute('count', IntTopic, 0)

    def init_node(self):
        self.button.on_click += self.button_clicked

    def button_clicked(self):
        self.i.set(self.i.get() + 1)
        self.text.set(str(self.i.get()))

# class TestNode2(Node):
#     category = 'test'
#     def build(self):
#         self.add_out_port('out')
#         self.shape.set('simple')
#         self.label.set('ROS Topic')
        
#         self.add_control(TextControl)

# class TestNode3(Node):
#     category = 'test/1/1'
#     def build(self):
#         self.shape.set('round')
#         self.add_in_port('in')
#         self.label.set('<-')
#         self.add_control(TextControl).text.set('<-')

class AdditionNode(FunctionNode):
    '''
    Adds a set of numbers together.
    '''
    category = 'function/math'

    inputs = ['numbers']
    max_in_degree = [None]
    outputs = ['sum']

    def calculate(self, data: List[Any]):
        return sum(data)