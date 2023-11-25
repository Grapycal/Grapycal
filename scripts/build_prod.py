# packs up the app into dist/ 
import os
import shutil
import subprocess
from compile_to_pyc import compile_package

dist = 'production/dist'

if os.path.exists(dist):
    shutil.rmtree(dist)
os.makedirs(dist)
compile_package('backend/src/grapycal', f'{dist}/grapycal')

# all packages in ./extensions/ will be compiled to dist/

for extention_name in os.listdir('extensions'):
    # skip files
    if not os.path.isdir(f'extensions/{extention_name}'):
        continue
    # find the real package root. can be at ., ./<package_name> or ./src/<package_name>
    for package_root in [f'{extention_name}', f'{extention_name}/{extention_name}', f'{extention_name}/src/{extention_name}']:
        if os.path.exists(f'extensions/{package_root}/__init__.py'):
            break
    else:
        print(f'folder {extention_name} is not a extention')
        continue

    src = f'extensions/{package_root}'
    dst = f'{dist}/{extention_name}'

    compile_package(src,dst)
    print(f'compiled extention {src} to {dst}')

# copy frontend/dist to dist\grapycal\webpage

npm = subprocess.Popen(['npm.cmd', 'run', 'build'], cwd='frontend')
npm.wait()

shutil.copytree('frontend/dist', f'{dist}/grapycal/webpage', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))

# copy resources/* to dist

for file in os.listdir('production/resources'):
    shutil.copyfile(f'production/resources/{file}', f'{dist}/{file}')