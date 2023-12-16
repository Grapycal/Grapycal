import asyncio
import aiohttp
import yaml
import json

async def get_remote_extensions() -> list[dict]:
    '''
    Returns a list of available extensions that is not installed yet.
    '''
    try:
        async with aiohttp.request('GET','https://github.com/Grapycal/grapycal_data/raw/main/data.yaml') as response:
            data = yaml.safe_load(await response.text())
    except Exception as e :
        print('Error while fetching data.yaml from github. Maybe no internet connection?')
        return []


    not_installed_extensions = []
    async def task(name):
        metadata = await get_package_metadata(name)
        version = metadata['info']['version'] if 'version' in metadata['info'] else '0.0.0'
        not_installed_extensions.append({
            'name': name,
            'version': version,
        })
    coros = [task(name) for name,extension_data in data['extensions'].items()]
    await asyncio.gather(*coros)

    return not_installed_extensions

async def get_package_metadata(package_name: str) -> dict:
    '''
    Returns the metadata of a package.
    '''
    async with aiohttp.request('GET',f'https://pypi.org/pypi/{package_name}/json') as response:
        data = json.loads(await response.text())
    return data