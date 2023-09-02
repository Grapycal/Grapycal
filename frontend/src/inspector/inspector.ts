import { Topic } from "objectsync-client"
import { ComponentManager, IComponentable } from "../component/component"
import { HtmlItem } from "../component/htmlItem"
import { ExposedAttributeInfo, Node } from "../sobjects/node"
import { as } from "../utils"
import { HierarchyNode } from "../ui_utils/hierarchyNode"
import { Linker } from "../component/linker"
import { Workspace } from "../sobjects/workspace"
import { TextEditor } from "./TextEditor"
import { ListEditor } from "./ListEditor"
import { IntEditor } from "./IntEditor"
import { FloatEditor } from "./FloatEditor"
import { ObjSetEditor } from "./ObjSetEditor"

export function object_equal(a:any,b:any){
    return JSON.stringify(a) === JSON.stringify(b);
}
export class Inspector implements IComponentable{
    componentManager = new ComponentManager();
    htmlItem: HtmlItem;
    linker = new Linker(this);
    hierarchy: HierarchyNode;
    nodes: Node[] = []

    nameEditorMap: {[key:string]:any}={
        'text':TextEditor,
        'list':ListEditor,
        'int':IntEditor,
        'float':FloatEditor,
        'objSet':ObjSetEditor
    }

    template = `
    <div class="full-height flex-vert">
        <div id="node_info">
            <div id="node_type"></div>
            <div id="extension_name"></div>
            <div id="node_description"></div>
        </div>
        <hr>
        <div id="slot_attributes_hierarchy"></div>
        <hr>
        <div id="output_display"></div>
        
    </div>
    `;
    nodeTypeDiv: HTMLElement;
    extensionNameDiv: HTMLElement;
    nodeDescriptionDiv: HTMLElement;
    outputDisplayDiv: HTMLElement;

    constructor(){
        this.htmlItem = new HtmlItem(this,document.getElementById('slot_inspector'),this.template);
        this.hierarchy = new HierarchyNode('', '',true);
        this.hierarchy.htmlItem.setParent(this.htmlItem,'attributes_hierarchy');
        this.nodeTypeDiv = this.htmlItem.getHtmlEl('node_type');
        this.extensionNameDiv = this.htmlItem.getHtmlEl('extension_name');
        this.nodeDescriptionDiv = this.htmlItem.getHtmlEl('node_description');
        this.outputDisplayDiv = this.htmlItem.getHtmlEl('output_display');
        this.outputDisplayDiv.style.bottom = '0px';
        as(this.htmlItem.baseElement,HTMLElement).style.display = 'none';
        as(this.htmlItem.baseElement,HTMLElement).style.alignItems = 'stretch'
    }

    addNode(node: Node){
        this.nodes.push(node);
        this.updateContent();
    }

    removeNode(node: Node){
        let index = this.nodes.indexOf(node);
        if(index === -1) throw new Error('node not found');
        this.nodes.splice(index,1);
        this.updateContent();
    }

    private updateContent(){
        this.updateNodeInfo();
        this.updateHierarchy();
    }

    private updateNodeInfo(){
        
        this.outputDisplayDiv.innerText = '';

        if(this.nodes.length === 0){
            as(this.htmlItem.baseElement,HTMLElement).style.display = 'none';
            return;
        }else{
            as(this.htmlItem.baseElement,HTMLElement).style.display = 'flex';
        }
        this.linker.unlink(this.addOutput)
        if(this.nodes.length === 1){
            let fullType = this.nodes[0].type_topic.getValue();
            let type = fullType.split('.')[1];
            let extensionName = fullType.split('.')[0];
            this.nodeTypeDiv.innerText = type;
            this.extensionNameDiv.innerText = extensionName;
            
            let outputAttribute = this.nodes[0].output;
            for(let item of outputAttribute.getValue()){
                this.addOutput(item);
            }
            this.linker.link(outputAttribute.onInsert,this.addOutput);
            
            return;
        }

        let nodeTypeString = '';
        for(let node of this.nodes){
            nodeTypeString += node.type_topic.getValue().split('.')[1] + ', ';
        }
        nodeTypeString = nodeTypeString.slice(0,-2);
        this.nodeTypeDiv.innerText = nodeTypeString;
        this.extensionNameDiv.innerText = '';
    }

    private addOutput(item:[string,string]){
        let [type,content] = item;
        if(content === '') return;

        //replace space
        content = content.replace(/ /g,'\u00a0');

        let span = document.createElement('span');
        span.classList.add('output-item');
        span.innerText = content;
        if (type === 'error'){
            span.classList.add('error');
        }else{
            span.classList.add('output');
        }
        this.outputDisplayDiv.appendChild(span);
    }

    private updateHierarchy(){
        this.hierarchy.clear();
        
        // group by display_name
        let exposedAttributes = new Map<string,ExposedAttributeInfo[]>();
        for(let node of this.nodes){
            for(let info of node.exposed_attributes.getValue()){
                if(!exposedAttributes.has(info.display_name)){
                    exposedAttributes.set(info.display_name,[]);
                }
                exposedAttributes.get(info.display_name).push(info);
            }
        }

        // add groups to hierarchy
        for(const [name,infos] of exposedAttributes){
            let comparingEditorArgs = infos[0].editor_args;
            let accept = true;
            if(infos.length !== this.nodes.length){
                accept = false;
            }
            for(let info of infos){
                if(!object_equal(info.editor_args,comparingEditorArgs)){
                    accept = false;
                    break;
                }
            }
            if(accept){
                let connectedAttributes : Topic<any>[] = [];
                for(let info of infos){
                    connectedAttributes.push(Workspace.instance.getObjectSync().getTopic(info.name));
                }
                let editorArgs = infos[0].editor_args;
                let displayName = infos[0].display_name;
                let editor = new this.nameEditorMap[editorArgs.type](displayName,editorArgs,connectedAttributes);
                this.hierarchy.addLeaf(editor.htmlItem,'');
            }
        }
    }
}



