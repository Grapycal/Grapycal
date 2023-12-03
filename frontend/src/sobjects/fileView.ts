import { Componentable } from "../component/componentable"
import { HierarchyNode } from "../ui_utils/hierarchyNode"
import { stringToElement, textToHtml } from "../utils"
import { CompSObject } from "./compSObject"
import { Workspace } from "./workspace"

export class FileViewItem extends Componentable{
    protected get template(): string {return `
        <div class="file-item">
            <span class="file-name"></span>
            
        </div>
        `;
    }
    protected get style(): string {return ` 
        .file-item{
            display: flex;
            flex-direction: row;
            align-items: center;
            padding: 4px;
            cursor: pointer;
        }
        .file-item:hover{
            background-color: var(--z3);
        }
        .file-item .file-name{
            margin-left: 8px;
        }
        .file-item .file-name.file-dir::before{
            content: '📁';
        }
        .file-item .file-name.file-file::before{
            content: '📄';
        }`
    }

    constructor(name:string,isDir:boolean,onDbClicked:()=>void=()=>{}){
        super()
        const fileName = this.htmlItem.getHtmlElByClass('file-name')
        fileName.innerText = name
        if(isDir){
            fileName.classList.add('file-dir')
        }else{
            fileName.classList.add('file-file')
        }
        this.link2(fileName,'dblclick',onDbClicked)
    }
}

export class FileView extends CompSObject{
    
    hierarchy :HierarchyNode

    protected onStart(): void {
        this.hierarchy = new HierarchyNode('','',true)
        this.hierarchy.htmlItem.setParentElement(document.getElementById('tab-file-view'))
        this.makeRequest('ls',{path:''},(response)=>{
            // format: [{name,is_dir}]
            for(let file of response){
                let item = new FileViewItem(file.name,file.is_dir,()=>{this.openWorkspace(`${file.path}`)})
                this.hierarchy.addLeaf(item)
            }
        })
    }

    private openWorkspace(path: string){
        Workspace.instance.openWorkspace(path)
    }
}