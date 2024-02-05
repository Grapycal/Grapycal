
from grapycal import OptionControl
def setup_net_name_ctrl(control:OptionControl):
    from .manager import Manager as M
    def on_network_names_changed():
        control.options.set(M.net.get_network_names())
    M.net.on_network_names_changed += on_network_names_changed
    on_network_names_changed()

    existing_networks = M.net.get_network_names()
    if len(existing_networks) > 0:
        control.value.set(existing_networks[0])

    def unlink():
        M.net.on_network_names_changed -= on_network_names_changed
    return unlink