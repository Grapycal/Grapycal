import requests
import yaml
import json

def get_not_installed_extensions() -> list[str]:
    '''
    Returns a list of available extensions that is not installed yet.
    '''
    data = yaml.safe_load(requests.get('https://github.com/eri24816/grapycal_data/raw/main/data.yaml').text)
    not_installed_extensions = []
    for name,extension_data in data['extensions'].items():
        not_installed_extensions.append(name)

    return not_installed_extensions

def get_package_metadata(package_name: str) -> dict:
    '''
    Returns the metadata of a package.
    '''
    data = json.loads(requests.get(f'https://pypi.org/pypi/{package_name}/json').text)
    return data