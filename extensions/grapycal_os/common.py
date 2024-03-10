from grapycal import TextControl, ButtonControl, Edge, InputPort, Node, StringTopic
import subprocess
import os

WINDOWS = os.name == 'nt'

class CommandNode(Node):
    category = 'system'

    def build_node(self):
        self.label.set('Command')
        self.shape.set('normal')
        self.css_classes.append('fit-content')
        self.command_port = self.add_in_port('command', control_type=TextControl)
        self.cwd_port = self.add_in_port('cwd', control_type=TextControl, text='.')
        self.run_port = self.add_in_port('trigger', control_type=ButtonControl)
        self.stdout_port = self.add_out_port('stdout')
        self.stderr_port = self.add_out_port('stderr')

        self.environment = self.add_attribute('environment',StringTopic,editor_type='options',options=['default','git bash'])

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.run_port:
            self.run(self.task)
        
    def task(self):
        command = self.command_port.get_one_data()
        cwd = self.cwd_port.get_one_data()
        environment = self.environment.get()
        commands = [command]
        if environment == 'git bash' and WINDOWS:
            commands.insert(0, 'C:\\Program Files\\Git\\bin\\bash.exe')
            commands.insert(1, '-c')
        result = subprocess.run(commands, shell=True, capture_output=True, text=True,cwd=cwd)
        self.stdout_port.push_data(result.stdout)
        if result.stderr:
            self.stderr_port.push_data(result.stderr)
            self.print_exception(Exception(result.stderr))