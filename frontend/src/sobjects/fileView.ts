import { DictTopic, StringTopic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { HierarchyNode } from "../ui_utils/hierarchyNode"
import { InfoPopup } from "../ui_utils/infoPopup"
import { Vector2, stringToElement, textToHtml } from "../utils"
import { CompSObject } from "./compSObject"
import { Workspace } from "./workspace"
import { LIB_VERSION } from "../version"
import { HtmlItem } from "../component/htmlItem"
import { print } from "../devUtils"

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
    htmlItem: HtmlItem
    currentPath: string = '.'

    // used to check if installed extensions are sufficent to open the selected workspace
    importedExtensionsTopic: DictTopic<string, any>
    avaliableExtensionsTopic: DictTopic<string, any>

    get template(): string {return `
        <div>
            <h2 class="">
                <span class="tab-title">File View Name</span>
            </h2>
            folder: <span id="dir-path"></span>
            <div id="slot_default"></div>
        </div>
        `;
    }

    get installedExtensions (){return new Map([
            ...this.importedExtensionsTopic.getValue().entries(), 
            ...this.avaliableExtensionsTopic.getValue().entries()
        ])
    }

    protected onStart(): void {
        this.importedExtensionsTopic = this.objectsync.getTopic('imported_extensions',DictTopic<string,any>)
        this.avaliableExtensionsTopic = this.objectsync.getTopic('avaliable_extensions',DictTopic<string,any>)

        this.htmlItem = new HtmlItem(this,document.getElementById('tab-file-view'))
        this.htmlItem.applyTemplate(this.template,"append")
        this.getAttribute('name').onSet.add((value)=>{this.htmlItem.getHtmlElByClass('tab-title').innerText = value})
        this.hierarchy = new HierarchyNode('','',true)
        this.hierarchy.htmlItem.setParent(this.htmlItem,"default","append")
        this.changeDir('.')
        this.infoPopup = new InfoPopup()
        this.link2(this.infoPopup.baseDiv,'mouseleave',()=>{
            setTimeout(() => {
                this.hideIfNotMouseOver(this.lastMouseOver)
            }, 100);
        })
    }

    private itemDoubleClicked(info:any){
        if(info.type == 'workspace'){
            this.openWorkspace(info.path)
        }else if(info.type == 'dir'){
            this.changeDir(info.name)
        }
    }

    private openWorkspace(path: string){
        // check if installed extensions are sufficent to open the selected workspace
        path = this.currentPath+'/'+path
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

        this.makeRequest('open_workspace',{path:path})
    }

    private changeDir(path: string){
        if(path == '.'){
            path = path
        }else if(path == '..'){
            path = this.currentPath.split('/').slice(0,-1).join('/')
        }else{
            path = this.currentPath + '/' + path
        }

        this.makeRequest('ls',{path:path},(response)=>{
            this.hierarchy.clear()
            if(path != '.')
                this.addItem({name:'..',type:'dir'})
            for(let file of response){
                this.addItem(file)
            }
        })
        this.currentPath = path
        this.htmlItem.getHtmlEl('dir-path').innerHTML = (path=='.'? '[ root ]': textToHtml(path))
    }

    private addItem(info:any){
        let displayName = info.name
        //omit .grapycal extension
        if(info.type == 'workspace' && info.name.endsWith('.grapycal')){
            displayName = info.name.slice(0,-9)
            if(displayName.length > 27){
                displayName = displayName.slice(0,27)+'...'
            }
        }
        let item = new FileViewItem(displayName,info.type,()=>{this.itemDoubleClicked(info)})
        this.link2(item.htmlItem.baseElement,'mouseenter',()=>{
            if(info.type == 'workspace' ) {
                if(this.metadataCache.has(this.currentPath+'/'+info.path)){
                    this.showInfoPopup(item,this.currentPath+'/'+info.path)
                }else{
                    this.makeRequest('get_workspace_metadata',{path:this.currentPath+'/'+info.path},(response)=>{
                        this.metadataCache.set(this.currentPath+'/'+info.path,response)
                        if(item.mouseOver)
                            this.showInfoPopup(item,this.currentPath+'/'+info.path)
                    })
                }
            }
        })
        this.hierarchy.addLeaf(item)
    }

    private showInfoPopup(item:FileViewItem,path:any){
        

        const meta = this.metadataCache.get(path)
        const name = path.split('/').pop()

        this.lastMouseOver = item
        this.link2(item.htmlItem.baseElement,'mouseleave',()=>{
            setTimeout(() => {
                this.hideIfNotMouseOver(item)
            }, 100);
        })

        this.infoPopup.show()
        this.infoPopup.transform.translation = new Vector2(item.baseElement.getBoundingClientRect().right-80,item.baseElement.getBoundingClientRect().top)
        this.infoPopup.transform.updateUI()
        this.infoPopup.transform.backToScreen()

        if (meta.version==undefined) {
            this.infoPopup.baseDiv.innerHTML = 'The workspace was saved before v0.9.0<br>and does not contain metadata.'
            return
        }

        // this.infoPopup.baseDiv.innerHTML = textToHtml(JSON.stringify(meta, null, 4))
        this.infoPopup.baseDiv.innerHTML = ''
        //title
        const title = stringToElement(`<h3>${name}</h3>`)
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