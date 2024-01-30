
from grapycal import OptionControl
def link_control_with_network_names(control:OptionControl):
    from .manager import Manager as M
    def on_network_names_changed():
        control.options.set(M.net.get_network_names())
    M.net.on_network_names_changed += on_network_names_changed
    on_network_names_changed()
    def unlink():
        M.net.on_network_names_changed -= on_network_names_changed
    return unlink