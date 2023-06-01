import { ComponentManager, IComponentable } from "../component/component"
import { HtmlItem } from "../component/htmlItem"
import { Linker } from "../component/linker"
import { print } from "../devUtils"

export class HeirarchyNode implements IComponentable{
    readonly template: string = `
    <div class="HierarchyNode">
        <span id="name" class="HierarchyName"></span>
        <div id="indent" class="HierarchyIndent">
            <div id="slot_childnode" class="HierarchyChildNodeSlot">
                
            </div>
            <div id="slot_leaf" class="HierarchyLeafSlot">
                        
            </div>
        </div>
    </div>
    `;

    readonly componentManager = new ComponentManager();
    private readonly children = new Map<string,HeirarchyNode>();
    private readonly leafs: HtmlItem[] = [];
    private readonly linker = new Linker(this);
    private expanded = false;

    readonly name: string;
    readonly htmlItem: HtmlItem;
    
    constructor(name:string,isRoot: boolean = false){
        this.name = name;
        this.htmlItem = new HtmlItem(this, document.body);
        this.htmlItem.applyTemplate(this.template);
        if(!isRoot){
            this.htmlItem.getHtmlEl('name').innerText = name+' ...';
            this.linker.link2(this.htmlItem.baseElement,'mousedown',this.mouseDown);
        }
        if(isRoot){
            //no padding slot_childnode and slot_leaf
            this.htmlItem.getHtmlEl('name').remove();
            this.htmlItem.getHtmlEl('indent').classList.remove('HierarchyIndent');
            this.htmlItem.baseElement.classList.remove('HierarchyNode');
        }

        if(!isRoot){
            this.htmlItem.getHtmlEl('indent').style.display = 'none';
        }
    }

    private addChild(name: string){
        let newChild = new HeirarchyNode(name);
        this.children.set(name,newChild);
        newChild.htmlItem.setParent(this.htmlItem,'childnode')
    }

    private removeChild(name: string){
        let child = this.children.get(name);
        if(child){
            child.destroy();
            this.children.delete(name);
        }
    }

    private mouseDown(e: MouseEvent){
        e.stopPropagation();
        this.expanded = !this.expanded;
        if(this.expanded){
            this.htmlItem.getHtmlEl('name').innerText = this.name + ' ';
            this.htmlItem.getHtmlEl('indent').style.display = 'block';
        }else{
            this.htmlItem.getHtmlEl('name').innerText = this.name + ' ...'
            this.htmlItem.getHtmlEl('indent').style.display = 'none';
        }
    }

    addLeaf(leaf: HtmlItem,path: string[]|string){
        if(typeof path === 'string'){
            path = path.split('/')
        }
        if(path.length === 0 || path[0] === ''){
            leaf.setParent(this.htmlItem,'leaf')
            this.leafs.push(leaf);
        }else{
            let child = this.children.get(path[0]);
            if(!child){
                this.addChild(path[0]);
                child = this.children.get(path[0]);
            }
            child!.addLeaf(leaf,path.slice(1));
        }
    }

    removeLeaf(leaf: HtmlItem, path: string[]|string){
        if(typeof path === 'string'){
            path = path.split('/')
        }
        if(path.length === 0 || path[0] === ''){
            this.leafs.splice(this.leafs.indexOf(leaf),1);
        }else{
            let child = this.children.get(path[0])!;
            child.removeLeaf(leaf,path.slice(1));

            if(child.isEmpty()){
                this.removeChild(path[0]);
            }
        }
    }

    isEmpty(){
        return this.children.size === 0 && this.leafs.length === 0;
    }

    destroy(){
        this.componentManager.destroy();
        this.children.forEach((child)=>{
            child.destroy();
        })
    }
}