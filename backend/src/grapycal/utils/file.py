import os

def get_direct_sub_folders(path: str) -> list[str]:
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path,f))]