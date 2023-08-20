import { Action, FloatTopic, IntTopic, ListTopic, StringTopic, Topic } from "objectsync-client"
import { ComponentManager, IComponentable } from "../component/component"
import { Componentable } from "../component/componentable"
import { HtmlItem } from "../component/htmlItem"
import { ExposedAttributeInfo, Node } from "../sobjects/node"
import { as } from "../utils"
import { HeirarchyNode as HierarchyNode } from "./hierarchyNode"
import { Linker } from "../component/linker"
import { Workspace } from "../sobjects/workspace"
import { print } from "../devUtils"

function object_equal(a:any,b:any){
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
        'float':FloatEditor
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



class TextEditor implements IComponentable{
    readonly template: string = `
    <div class="attribute-editor flex-horiz stretch">
        <div id="attribute-name"></div>
        <input id="input" type="text" class="text-editor">
    </div>
    `;

    readonly componentManager = new ComponentManager();
    readonly htmlItem: HtmlItem;
    readonly input: HTMLInputElement;
    readonly linker = new Linker(this);
    readonly connectedAttributes: Topic<any>[];
    private locked = false;

    constructor(displayName:string,editorArgs:any,connectedAttributes: Topic<any>[]){
        this.connectedAttributes = connectedAttributes;
        this.htmlItem = new HtmlItem(this);
        this.htmlItem.applyTemplate(this.template);
        this.input = as(this.htmlItem.getHtmlEl('input'), HTMLInputElement);
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName;
        for (let attr of connectedAttributes) {
            attr = as(attr,StringTopic);
            this.linker.link(attr.onSet, this.updateValue);
        }
        this.linker.link2(this.input,'input',this.inputChanged);
        this.updateValue();
    }

    private updateValue () {
        if(this.locked) return;
        let value:string = null;
        for(let attr of this.connectedAttributes){
            if(value === null){
                value = attr.getValue();
            }else{
                if(value !== attr.getValue()){
                    value = null;
                    break;
                }
            }
        }
        if(value === null){
            this.input.value = '';
            this.input.placeholder = 'multiple values';
        }else{
            this.input.value = value;
        }
    }

    private inputChanged(){
        this.locked = true;
        Workspace.instance.record(() => {
            for(let attr of this.connectedAttributes){
                attr = as(attr,StringTopic);
                attr.set(this.input.value);
            }
        });
        this.locked = false;
    }
}

class ListEditor extends Componentable{

    get template(){ 
        return `
        <div class="attribute-editor flex-horiz stretch">
            <div id="attribute-name"></div>
            <div class="container">
                <div class="container" id="slot_container"></div>
                <div class="container horiz">
                    <input id="input" type="text" class="grow">
                    <button id="add-button" class="button center-align">+</button>
                </div>
            </div>
        </div>
    `}

    get style(): string { 
        return super.style + `
        .container{
            display: flex;
            flex-direction: column;
            align-items: stretch;
            flex-grow: 1;
            margin: 4px 10px;
            min-width: 0px;
        }
        .horiz{
            flex-direction: row;
        }
        
        .button{
            height: 20px;
            line-height: 0px;
        }
    `}

    private readonly container: HTMLDivElement;
    private readonly addButton: HTMLButtonElement;
    private readonly addInput: HTMLInputElement;
    private readonly connectedAttributes: ListTopic<any>[];
    private readonly items: Set<ListEditorItem> = new Set();
    private locked = false;

    constructor(displayName:string,editorArgs:any,connectedAttributes: Topic<any>[]){
        super();
        print(connectedAttributes.length)
        this.connectedAttributes = [];
        for(let attr of connectedAttributes){
            this.connectedAttributes.push(as(attr,ListTopic));
        }

        this.container = as(this.htmlItem.getHtmlEl('slot_container'), HTMLDivElement);
        this.addInput = as(this.htmlItem.getHtmlEl('input'), HTMLInputElement);
        this.addButton = as(this.htmlItem.getHtmlEl('add-button'), HTMLButtonElement);

        this.linker.link2(this.addInput,'keydown',(e:KeyboardEvent) => {
            if(e.key === 'Enter'){
                this.addHandler();
            }
        });
        this.linker.link2(this.addButton,'click',this.addHandler);

        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName;

        for (let attr of connectedAttributes) {
            this.linker.link(attr.onSet, this.updateValue);
        }

        this.updateValue();
    }

    private updateValue() {
        if(this.locked) return;
        let value:any[] = null;
        for(let attr of this.connectedAttributes){
            if(value === null){
                value = attr.getValue();
            }else{
                if(!object_equal(value,attr.getValue())){
                    value = null;
                    break;
                }
            }
        }

        // First destroy all items (Sorry, performance)
        for(let item of this.items.values()){
            item.destroy();
        }
        this.items.clear();

        if(value === null){
            this.container.innerText = 'multiple values';

        }else{
            this.container.innerText = '';
            let pos = 0;
            for(let itemText of value){
                let itemComponent = new ListEditorItem(itemText,pos++);
                this.linker.link(itemComponent.deleteClicked,this.deleteHandler);
                this.items.add(itemComponent);
                itemComponent.htmlItem.setParent(this.htmlItem,'container');
            }
        }
    }

    private addHandler(){
        let text = this.addInput.value;
        if(text === '') return;
        this.addInput.value = '';
        this.locked = true;
        Workspace.instance.record(() => {
            for(let attr of this.connectedAttributes){
                attr.insert(text);
            }
        });
        this.locked = false;
    }

    private deleteHandler(item:ListEditorItem){
        this.locked = true;
        Workspace.instance.record(() => {
            for(let attr of this.connectedAttributes){
                attr.pop(item.position);
            }
        });
        this.items.delete(item);
        
        this.locked = false;
    }
}

class ListEditorItem extends Componentable{

    get template(){ 
        return `
        <div class="item flex-horiz stretch">
            <div id="list-editor-item-text"class="text"></div>
            <button id="list-editor-item-delete" class="button center-align">-</button>
        </div>
        `
    }

    get style(): string { 
        return super.style + `
        .item{
            margin: 2px 0px;
            border: 1px outset #373737;
            flex-grow: 1;
            background-color: #181818;
            min-width: 0px;
        }
        .text{
            flex-grow: 1;
            margin-left: 5px;
            min-width: 0px; /* prevent too large width when overflow*/
            overflow: hidden;
        }
        .button{
            height: 20px;
            line-height: 0px;
        }
   ` }

    readonly text: string;
    readonly position: number;

    readonly textDiv: HTMLDivElement;
    public readonly deleteButton: HTMLButtonElement;

    public readonly deleteClicked = new Action<[ListEditorItem]>();

    constructor(text:string,position:number){
        super();
        this.text = text;
        this.position = position;
        this.textDiv = as(this.htmlItem.getHtmlEl('list-editor-item-text'),HTMLDivElement);
        this.deleteButton = as(this.htmlItem.getHtmlEl('list-editor-item-delete'),HTMLButtonElement);
        this.textDiv.innerText = text;
        this.linker.link2(this.deleteButton,'click',this.deleteClickedHandler);
    }

    private deleteClickedHandler(){
        this.destroy()
        this.deleteClicked.invoke(this);
    }
}

class IntEditor extends Componentable{

    get template(){ 
        return `
        <div class="attribute-editor flex-horiz stretch">
            <div id="attribute-name"></div>
            <input id="input" type="number" class="text-editor">
        </div>
        `
    }

    get style(): string { 
        return super.style + `
        .text-editor{
            width: 100px;
        }
    `}

    readonly input: HTMLInputElement;
    readonly connectedAttributes: Topic<any>[];
    private locked = false;

    constructor(displayName:string,editorArgs:any,connectedAttributes: Topic<any>[]){
        super();
        this.connectedAttributes = connectedAttributes;
        this.input = as(this.htmlItem.getHtmlEl('input'), HTMLInputElement);
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName;
        for (let attr of connectedAttributes) {
            attr = as(attr,IntTopic);
            this.linker.link(attr.onSet, this.updateValue);
        }
        this.linker.link2(this.input,'input',this.inputChanged);
        this.updateValue();
    }

    private updateValue () {
        if(this.locked) return;
        let value:number = null;
        for(let attr of this.connectedAttributes){
            if(value === null){
                value = attr.getValue();
            }else{
                if(value !== attr.getValue()){
                    value = null;
                    break;
                }
            }
        }
        if(value === null){
            this.input.value = '';
            this.input.placeholder = 'multiple values';
        }else{
            this.input.value = value.toString();
        }
    }

    private inputChanged(){
        this.locked = true;
        Workspace.instance.record(() => {
            for(let attr of this.connectedAttributes){
                attr = as(attr,IntTopic);
                attr.set(Number.parseInt(this.input.value));
            }
        });
        this.locked = false;
    }
}

class FloatEditor extends Componentable{

    get template(){ 
        return `
        <div class="attribute-editor flex-horiz stretch">
            <div id="attribute-name"></div>
            <input id="input" type="number" class="text-editor">
        </div>
        `
    }

    get style(): string { 
        return super.style + `
        .text-editor{
            width: 100px;
        }
    `}

    readonly input: HTMLInputElement;
    readonly connectedAttributes: Topic<any>[];
    private locked = false;

    constructor(displayName:string,editorArgs:any,connectedAttributes: Topic<any>[]){
        super();
        this.connectedAttributes = connectedAttributes;
        this.input = as(this.htmlItem.getHtmlEl('input'), HTMLInputElement);
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName;
        for (let attr of connectedAttributes) {
            attr = as(attr,FloatTopic);
            this.linker.link(attr.onSet, this.updateValue);
        }
        this.linker.link2(this.input,'input',this.inputChanged);
        this.updateValue();
    }

    private updateValue () {
        if(this.locked) return;
        let value:number = null;
        for(let attr of this.connectedAttributes){
            if(value === null){
                value = attr.getValue();
            }else{
                if(value !== attr.getValue()){
                    value = null;
                    break;
                }
            }
        }
        if(value === null){
            this.input.value = '';
            this.input.placeholder = 'multiple values';
        }else{
            this.input.value = value.toString();
        }
    }

    private inputChanged(){
        this.locked = true;
        Workspace.instance.record(() => {
            for(let attr of this.connectedAttributes){
                attr = as(attr,FloatTopic);
                attr.set(Number.parseFloat(this.input.value));
            }
        });
        this.locked = false;
    }
}