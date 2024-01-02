import { Componentable } from "../component/componentable"
import { HierarchyNode } from "../ui_utils/hierarchyNode"
import { stringToElement, textToHtml } from "../utils"
import { CompSObject } from "./compSObject"
import { Workspace } from "./workspace"
import { FileViewItem } from "./fileView"


export class ExamplesTab extends CompSObject{
    
    hierarchy :HierarchyNode

    protected onStart(): void {
        this.hierarchy = new HierarchyNode('','',true)
        this.hierarchy.htmlItem.setParentElement(document.getElementById('tab-file-view'))
        this.makeRequest('get',{path:''},(response)=>{
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