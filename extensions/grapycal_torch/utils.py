
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

from typing import Iterable


def find_next_valid_name(name:str, invalids:Iterable[str]):
    # base -> base(1) -> base(2) -> ...
    
    if name == '':
        return name
    if name not in invalids:
        return name
    
    # separate base and number
    base = name
    number = 1
    if '(' in name and name[-1] == ')':
        base = name[:name.rfind('(')]
        number = name[name.rfind('(')+1:-1]
        try:
            number = int(number)
        except:
            base = name
            number = 1

    while True:
        new_name = f'{base}({number})'
        if new_name not in invalids:
            return new_name
        number += 1
