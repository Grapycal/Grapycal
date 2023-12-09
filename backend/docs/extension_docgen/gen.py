import argparse
from typing import List
from grapycal.extension.extension import Extension
from collections import defaultdict
import re

def capilalizeFirstLetter(s:str):
    return s[0].upper() + s[1:]

class Scanner:
    def __init__(self,rst:str) -> None:
        self.rst = rst
        self.lines:List[str] = rst.split('\n')
        for i in range(len(self.lines)):
            if self.lines[i].strip():
                break
        else:
            self.lines = []
            return
        self.lines = self.lines[i:]
        self.process()

    def process(self):
        '''change 
        - values:
          to 
        - **values**:
        '''
        for i in range(len(self.lines)):
            line = self.lines[i]
            # make ^(\s*)-(\s*)(\w+): bold
            line = re.sub(r'(\s*)-(\s*)(\w+):',r'\1- **\3**:',line)
            # make ^(\s*):(\w+): start with capital letter
            line = re.sub(r'(\s*):(\w+):',lambda x: x.group(1) + ':' + x.group(2).capitalize() + ':',line)
            self.lines[i] = line

                

    def get_block(self,keyword):
        result = []
        for i, line in enumerate(self.lines):
            if keyword in line:
                block_indent = len(line) - len(line.lstrip())
                result.append(line[block_indent:])
                break
        else:
            return ''

        for i in range(i+1, len(self.lines)):
            print(self.lines[i])
            if not self.lines[i].strip():
                continue
            line_indent = len(self.lines[i]) - len(self.lines[i].lstrip())
            if line_indent <= block_indent:
                break
            result.append(self.lines[i][block_indent:])

        return '\n'.join(result)
    
    def get_unindent(self):
        min_indent = min([len(line) - len(line.lstrip()) for line in self.lines if line.strip()])
        result = []
        for line in self.lines:
            result.append(line[min_indent:])
        return '\n'.join(result)
    

parser = argparse.ArgumentParser(description='Generate extension documentation')
parser.add_argument('--extension', '-e', type=str, help='name of the extension')
parser.add_argument('--out', '-o', type=str, help='output file',default='backend/docs/extension_docgen/generated.rst')

args = parser.parse_args()

name = args.extension
out = args.out

ext = Extension(name)

node_types =  ext.node_types_without_extension_name.values()

# categorize with category

categories = defaultdict(list)

for node_type in node_types:
    category = node_type.category
    categories[category].append(node_type)

# generate rst

# try to load the old rst and preserve the part above [generator please start from below]
try:
    with open(out,'r') as f:
        rst = f.read()
        # search for .. [generator please start from below] and remove everything below it
        rst = re.sub(r'\.\. \[generator please start from below\].*','.. [generator please start from below]\n',rst,flags=re.DOTALL)
except:
    rst = f'''
{ext.name}
==================
'''

# sort categories
def sort_key(category):
    return category[1][0].get_def_order()
categories = sorted(categories.items(),key=sort_key)

for category, node_types in categories:
    print(category)
    rst += f'''
{capilalizeFirstLetter(category)}
------------------
'''
#   .. |addition image| image:: ./node_imgs/addition.jpg
#       :height: 1.5em

#   |addition image| Addition
    node_types = sorted(node_types,key=lambda x:x.get_def_order())
    for node_type in node_types:
        name = re.sub(r'Node$','',node_type.__name__)
        name_lower = name.lower()
        rst += f'''

{name}
~~~~~~~~~~~~~~~~~~~

.. image:: ./node_imgs/{name_lower}.jpg
    :width: 10em
    :align: right
    :alt: [{name} image]

'''
        if not node_type.__doc__:
            continue
        scanner = Scanner(node_type.__doc__)

        rst += scanner.get_unindent()
#         rst += f'''
# .. container:: clearer

#     .. image :: https://i.imgur.com/46USmE3.png
#         :height: 0px

# '''

        rst += '\n|\n'

with open(out,'w') as f:
    f.write(rst)

#copy ./node_imgs to out_dir
import shutil,os
here = os.path.dirname(os.path.abspath(__file__))
node_imgs = os.path.join(here,'node_imgs')
shutil.copytree(node_imgs,os.path.join(os.path.dirname(out),'node_imgs'),dirs_exist_ok=True)