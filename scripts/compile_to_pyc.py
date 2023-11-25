import compileall
import os
import re
import sys


def compile_package(src, dst):
    compileall.compile_dir(src, force=True,ddir=dst,quiet=True)
    # this will compile all .py files in src and distribute them in local __pycache__ folders

    # collect all .pyc files in src
    file_map = []
    for root, dirs, files in os.walk(src):
        for file in files:
            if file.endswith('.pyc'):
                # remove trailing __pycache__ from root
                root_without_postfix = root[:-len('__pycache__')]
                # remove src from root
                root_without_prefix = root_without_postfix[len(src):]
                # add dst to root
                root_with_dst = dst + root_without_prefix
                # remove .cpython-x.pyc from file
                file_without_postfix = re.sub(r'\.cpython-\d+\.pyc$', '', file)
                # add .pyc to file
                file_with_prefix = file_without_postfix + '.pyc'
                # add file to list
                file_map.append([os.path.join(root,file),os.path.join(root_with_dst, file_with_prefix)])

    # remove content of dst if exists
    import shutil
    if os.path.exists(dst):
        shutil.rmtree(dst)
    # copy all .pyc files to dst
    for src_file, dst_file in file_map:
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        os.rename(src_file, dst_file)

    # also the src/__init__.py  should be copied to dst/__init__.py

    shutil.copyfile(os.path.join(src,'__init__.py'),os.path.join(dst,'__init__.py'))
    if os.path.exists(os.path.join(src,'__main__.py')):
        shutil.copyfile(os.path.join(src,'__main__.py'),os.path.join(dst,'__main__.py'))
        
if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    compile_package(src, dst)