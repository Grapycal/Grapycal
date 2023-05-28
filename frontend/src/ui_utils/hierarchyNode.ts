import { ComponentManager, IComponentable } from "../component/component"
import { HtmlItem } from "../component/htmlItem"
import { Linker } from "../component/linker"
import { print } from "../devUtils"

export class HeirarchyNode implements IComponentable{
    readonly template: string = `
    <div class="HierarchyNode">
        <span id="name"></span>
        <div id="slot_childnode" class="HierarchyChildNodeSlot">
            
        </div>
        <div id="slot_leaf" class="HierarchyLeafSlot">
                    
        </div>
    </div>
    `;

    readonly componentManager = new ComponentManager();
    private readonly children = new Map<string,HeirarchyNode>();
    private readonly linker = new Linker(this);
    private expanded = false;

    readonly name: string;
    readonly htmlItem: HtmlItem;
    
    constructor(name:string,isRoot: boolean = false){
        this.name = name;
        this.htmlItem = new HtmlItem(this, document.body);
        this.htmlItem.applyTemplate(this.template);
        this.htmlItem.getHtmlEl('name').innerText = name;
        if(isRoot){
            //no padding slot_childnode and slot_leaf
            this.htmlItem.getHtmlEl('slot_childnode').style.paddingLeft = '0px';
            this.htmlItem.getHtmlEl('slot_leaf').style.paddingLeft = '0px';
        }
        this.linker.link2(this.htmlItem.getHtmlEl('name'),'mousedown',this.collapseOrExpand);

        if(!isRoot){
            this.htmlItem.getHtmlEl('slot_childnode').style.display = 'none';
            this.htmlItem.getHtmlEl('slot_leaf').style.display = 'none';
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

    private collapseOrExpand(){
        print(this.htmlItem)
        this.expanded = !this.expanded;
        if(this.expanded){
            this.htmlItem.getHtmlEl('slot_childnode').style.display = 'block';
            this.htmlItem.getHtmlEl('slot_leaf').style.display = 'block';
        }else{
            this.htmlItem.getHtmlEl('slot_childnode').style.display = 'none';
            this.htmlItem.getHtmlEl('slot_leaf').style.display = 'none';
        }
    }

    addLeaf(leaf: HtmlItem,path: string[]|string){
        if(typeof path === 'string'){
            path = path.split('/')
        }
        if(path.length === 0){
            leaf.setParent(this.htmlItem,'leaf')
        }else{
            let child = this.children.get(path[0]);
            if(!child){
                this.addChild(path[0]);
                child = this.children.get(path[0]);
            }
            child!.addLeaf(leaf,path.slice(1));
        }
    }

    destroy(){
        this.componentManager.destroy();
        this.children.forEach((child)=>{
            child.destroy();
        })
    }
}