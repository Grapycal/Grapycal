import { ComponentManager, IComponentable } from "../component/component"
import { HtmlItem } from "../component/htmlItem"
import { Linker } from "../component/linker"
import { print } from "../devUtils"
import { Node } from "../sobjects/node"

export class HierarchyNode implements IComponentable{
    readonly template: string = `
    <div class="hierarchy-node full-width">
        <span id="name" class="hierarchy-name"></span>
        <div id="indent" class="hierarchy-indent">
            <div id="slot_childnode" class="hierarchy-child-node-slot">
                
            </div>
            <div id="slot_leaf" class="hierarchy-leaf-slot">
                        
            </div>
        </div>
    </div>
    `;

    readonly componentManager = new ComponentManager();
    private readonly children = new Map<string,HierarchyNode>();
    private readonly leafs: HtmlItem[] = [];
    private readonly linker = new Linker(this);
    private expanded = true;

    readonly name: string;
    readonly path: string;
    readonly htmlItem: HtmlItem;
    
    constructor(name:string,path:string='',isRoot: boolean = false){
        this.name = name;
        this.path = path;
        this.htmlItem = new HtmlItem(this, document.body);
        this.htmlItem.applyTemplate(this.template);
        if(isRoot){
            //no padding slot_childnode and slot_leaf
            this.htmlItem.getHtmlEl('name').remove();
            this.htmlItem.getHtmlEl('indent').classList.remove('hierarchy-indent');
            this.htmlItem.baseElement.classList.remove('hierarchy-node');
        }
        if(!isRoot){
            this.htmlItem.getHtmlEl('name').innerText = name;
            this.linker.link2(this.htmlItem.getHtmlEl('name'),'mousedown',this.mouseDown);
            this.htmlItem.getHtmlEl('indent').style.display = 'block';
            for(let className of Node.getCssClassesFromCategory(path)){
                this.htmlItem.baseElement.classList.add(className);
            }
            if(path.lastIndexOf('/') === 0){
                this.htmlItem.getHtmlEl('name').classList.add('hierarchy-h1');
            }
        }
    }

    private addChild(name: string){
        let newChild = new HierarchyNode(name,this.path+'/'+name);
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
            this.htmlItem.getHtmlEl('name').innerText = this.name + ' >'
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

    clear(){
        this.children.forEach((child)=>{
            child.destroy();
        })
        this.children.clear();
        this.leafs.forEach((leaf)=>{
            leaf.componentManager.destroy();
        })
        this.leafs.splice(0,this.leafs.length);
    }

    destroy(){
        this.componentManager.destroy();
        for (let child of this.children.values()){
            child.destroy();
        }
        for (let leaf of this.leafs){
            leaf.componentManager.destroy();
        }
    }

    isEmpty(){
        return this.children.size === 0 && this.leafs.length === 0;
    }
}