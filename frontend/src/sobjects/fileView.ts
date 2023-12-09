import { DictTopic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { HierarchyNode } from "../ui_utils/hierarchyNode"
import { InfoPopup } from "../ui_utils/infoPopup"
import { Vector2, stringToElement, textToHtml } from "../utils"
import { CompSObject } from "./compSObject"
import { Workspace } from "./workspace"
import { LIB_VERSION } from "../version"

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
        .file-item .file-name.file-workspace::before{
            content: '📄';
        }`
    }

    get baseElement(): HTMLElement {return this.htmlItem.baseElement as HTMLElement}

    private _mouseOver: boolean = false
    get mouseOver(): boolean {return this._mouseOver}
    constructor(name:string,type:string,onDbClicked:()=>void=()=>{}){
        super()
        const fileName = this.htmlItem.getHtmlElByClass('file-name')
        fileName.innerText = name
        fileName.classList.add(`file-${type}`)
        this.link2(this.baseElement,'dblclick',onDbClicked)
        this.link2(this.baseElement,'mouseenter',()=>{this._mouseOver = true})
        this.link2(this.baseElement,'mouseleave',()=>{this._mouseOver = false})
    }
}

export class FileView extends CompSObject{
    
    hierarchy :HierarchyNode
    metadataCache: Map<string,any> = new Map()
    infoPopup: InfoPopup
    lastMouseOver: FileViewItem

    // used to check if installed extensions are sufficent to open the selected workspace
    importedExtensionsTopic: DictTopic<string, any>
    avaliableExtensionsTopic: DictTopic<string, any>

    get installedExtensions (){return new Map([
            ...this.importedExtensionsTopic.getValue().entries(), 
            ...this.avaliableExtensionsTopic.getValue().entries()
        ])
    }

    protected onStart(): void {
        this.importedExtensionsTopic = this.objectsync.getTopic('imported_extensions',DictTopic<string,any>)
        this.avaliableExtensionsTopic = this.objectsync.getTopic('avaliable_extensions',DictTopic<string,any>)

        this.hierarchy = new HierarchyNode('','',true)
        this.hierarchy.htmlItem.setParentElement(document.getElementById('tab-file-view'))
        this.makeRequest('ls',{path:''},(response)=>{
            // format: [{name,is_dir}]
            for(let file of response){
                this.addFile(file)
            }
        })
        this.infoPopup = new InfoPopup()
        this.link2(this.infoPopup.baseDiv,'mouseleave',()=>{
            setTimeout(() => {
                this.hideIfNotMouseOver(this.lastMouseOver)
            }, 500);
        })
    }

    private openWorkspace(path: string){
        // check if installed extensions are sufficent to open the selected workspace
        const meta = this.metadataCache.get(path)
        const incompatibleExtensions = []
        if(meta.extensions && meta.extensions.length > 0)
            for(let ext of meta.extensions){
                if(!this.checkExtensionCompatibility(ext.name,ext.version)){
                    incompatibleExtensions.push(ext)
                }
            }
        if(incompatibleExtensions.length > 0){
            let message = `The following extensions are required to open this workspace but not installed:\n`
            for(let ext of incompatibleExtensions){
                message += `${ext.name} ${ext.version}\n`
            }
            message += `Open anyway?`
            if(!confirm(message)) return
        }

        Workspace.instance.openWorkspace(path)
    }

    private addFile(file:any){
        let item = new FileViewItem(file.name,file.type,()=>{this.openWorkspace(`${file.path}`)})
        this.link2(item.htmlItem.baseElement,'mouseenter',()=>{
            if(file.type == 'workspace' ) {
                if(this.metadataCache.has(file.path)){
                    this.showInfoPopup(item,file.path)
                }else{
                    this.makeRequest('get_workspace_metadata',{path:file.path},(response)=>{
                        this.metadataCache.set(file.path,response)
                        if(item.mouseOver)
                            this.showInfoPopup(item,file.path)
                    })
                }
            }
        })
        this.hierarchy.addLeaf(item)
    }

    private showInfoPopup(item:FileViewItem,path:any){
        

        const meta = this.metadataCache.get(path)


        this.lastMouseOver = item
        this.link2(item.htmlItem.baseElement,'mouseleave',()=>{
            setTimeout(() => {
                this.hideIfNotMouseOver(item)
            }, 500);
        })

        this.infoPopup.show()
        this.infoPopup.transform.translation = new Vector2(item.baseElement.getBoundingClientRect().right-80,item.baseElement.getBoundingClientRect().top)

        if (meta.name==undefined) {
            this.infoPopup.baseDiv.innerHTML = 'The workspace was saved before v0.9.0<br>and does not contain metadata.'
            return
        }

        // this.infoPopup.baseDiv.innerHTML = textToHtml(JSON.stringify(meta, null, 4))
        this.infoPopup.baseDiv.innerHTML = ''
        //title
        const title = stringToElement(`<h2>${meta.name}</h2>`)
        this.infoPopup.baseDiv.appendChild(title)
        this.infoPopup.baseDiv.appendChild(stringToElement(`<div>Requires:</div>`))
        //version
        const version = stringToElement(`<div>grapycal ${meta.version}</div>`)
        this.infoPopup.baseDiv.appendChild(version)
        if(this.compareVersions(LIB_VERSION,meta.version) < 0){
            version.classList.add('error')
            version.innerHTML += ` (installed: ${LIB_VERSION})`
        }else{
            version.classList.add('success')
        }
        //description
        //extensions
        if(meta.extensions && meta.extensions.length > 0)
            for(let ext of meta.extensions){
                const extension = stringToElement(`<div>${ext.name} ${ext.version}</div>`) as HTMLElement
                if(this.checkExtensionCompatibility(ext.name,ext.version)){
                    extension.classList.add('success')
                }else
                {
                    extension.classList.add('error')
                    extension.innerHTML += ` (installed: ${this.installedExtensions.get(ext.name)?.version||'none'})`
                }
                this.infoPopup.baseDiv.appendChild(extension)
            }

        //open button
        const openButton = stringToElement(`<button class="full-width">Open</button>`)
        this.link2(openButton,'click',()=>{
            this.openWorkspace(path)
        })
        this.infoPopup.baseDiv.appendChild(openButton)
    }

    private hideIfNotMouseOver(item:FileViewItem){
        if (this.lastMouseOver==item && !(this.infoPopup.mouseOver || this.lastMouseOver?.mouseOver)) {
            this.infoPopup.hide()
        }
    }

    private checkExtensionCompatibility(extensionName:string,minVersion:string){
        const extension = this.installedExtensions.get(extensionName)
        if(extension == undefined) return false
        return this.compareVersions(extension.version,minVersion) >= 0
    }

    private compareVersions(version1:string,version2:string){
        const v1 = version1.split('.')
        const v2 = version2.split('.')
        for(let i=0;i<v1.length;i++){
            if(parseInt(v1[i]) < parseInt(v2[i])) return -1
            if(parseInt(v1[i]) > parseInt(v2[i])) return 1
        }
        return 0
    }
}