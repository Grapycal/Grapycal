
from grapycal import OptionControl
def setup_net_name_ctrl(control:OptionControl,multi=False,set_value=True):
    from .manager import Manager as M
    def on_network_names_changed():
        existing_networks = M.net.get_network_names()
        options = []
        if not multi:
            options = existing_networks
        else:
            limit = 64
            for n in range(1,len(existing_networks)+1):
                # all combinations of n names
                import itertools
                for c in itertools.combinations(existing_networks,n):
                    options.append(','.join(c))
                if len(options) > limit:
                    break
        control.options.set(options)
    M.net.on_network_names_changed += on_network_names_changed
    on_network_names_changed()

    existing_networks = M.net.get_network_names()
    if len(existing_networks) > 0 and set_value:
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
