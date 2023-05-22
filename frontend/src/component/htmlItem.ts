import { Null, print } from "../devUtils"
import { Action, Constructor, as, defined } from "../utils"
import { Component, IComponentable } from "./component"
import { Transform } from "./transform"

export class HtmlItem extends Component{
    static templateIdGenerator: number = 0;

    baseElement: Element;
    parent_slot: HTMLElement;
    slots: Map<string,HTMLElement> = new Map();
    parent_: HtmlItem;
    get parent(){return this.parent_;}
    children: HtmlItem[] = [];
    readonly templateChanged = new Action<[]>();
    templateId: string='';

    constructor(object:IComponentable, specifiedParentElement: HTMLElement = Null()){
        super(object);
        this.baseElement = Null();
        this.parent_ = Null();
        this.parent_slot = specifiedParentElement;
    }

    applyTemplate(template: string, order: "prepend"|"append" = "prepend"){
        // create element from template
        if (this.baseElement !== Null())
            this.parent_slot.removeChild(this.baseElement);

        const templateElement = document.createElement('template');
        templateElement.innerHTML = template;
        this.baseElement = defined(templateElement.content.firstElementChild);

        // annotate element with template id
        this.templateId = `template_${HtmlItem.templateIdGenerator++}`;
        for(let element of this.baseElement.querySelectorAll('*')){
            element.setAttribute('template_id',this.templateId);
        }

        if(order === "append")
            this.parent_slot?.appendChild(this.baseElement);
        else
            this.parent_slot?.prepend(this.baseElement);

        // search for elements that id = slot_name
        // if found, add to slots:
        this.slots = new Map();
        const slotElements = this.baseElement.querySelectorAll('[id^="slot_"]');

        for(let element of slotElements){
            const slotName = element.id.slice(5);
            this.addSlot(slotName, as(element,HTMLElement));
        }
        this.templateChanged.invoke();
    }

    private moveToSlot(slot: HTMLElement, order: "prepend"|"append" = "prepend"){
        if (this.baseElement !== Null()){
            this.parent_slot?.removeChild(this.baseElement);
            if(order === "append")
                slot.appendChild(this.baseElement);
            else
                slot.prepend(this.baseElement);
        }
        this.parent_slot = slot;
    }

    getHtmlEl(id: string): HTMLElement{
        //match id and template_id
        const element = this.baseElement.querySelector(`[template_id="${this.templateId}"]#${id}`);
        //const element = this.baseElement.querySelector(`#${id}`);
        //check baseElement
        if (this.baseElement.id === id)
            return as(this.baseElement,HTMLElement);
        if (element === null)
            throw new Error(`Element with id ${id} not found`);
        return as(element,HTMLElement);
    }

    getEl<T extends Element>(id: string,type?:Constructor<T>): T{
        const element = this.baseElement.querySelector(`#${id}`);
        //check baseElement
        if (this.baseElement.id === id)
            if(type === undefined){
                return this.baseElement as any;
            }else{
                return as(this.baseElement,type);
            }
        if (element === null)
            throw new Error(`Element with id ${id} not found`);
        if(type === undefined){
            return element as any;
        }else{
            return as(element,type);
        }
    }

    setParent(parent: HtmlItem, slot: string = 'default', order: "prepend"|"append"="prepend"): void{
        if (this.parent_ !== Null())
            this.parent_.children = this.parent_.children.filter(i => i !== this);
        this.moveToSlot(parent.getSlot(slot),order);
        this.parent_ = parent;
        parent.children.push(this);
    }

    moveToFront(){
        this.parent_slot?.appendChild(this.baseElement);
    }

    moveToBack(){
        this.parent_slot?.prepend(this.baseElement);
    }

    addSlot(name: string, element: HTMLElement){
        this.slots.set(name,element);
    }
    removeSlot(name: string){
        this.slots.delete(name);
    }
    getSlot(name: string): HTMLElement{
        const slot = this.slots.get(name);
        if (slot === undefined)
            throw new Error(`Slot ${name} not found`);
        return slot;
    }
    findTransformParent(): Transform|null{
        let i : HtmlItem = this.parent;
        while (i !== null){
            if (i.componentManager.hasComponent(Transform))
                return i.getComponent(Transform);
            i = i.parent;
        }
        return null;
    }
    findTransformChildren(): Transform[]{
        const transforms: Transform[] = [];
        for (let child of this.children){
            if (child.componentManager.hasComponent(Transform))
                transforms.push(child.getComponent(Transform));
            else
                transforms.push(...child.findTransformChildren());
        }
        return transforms;
    }

    get position(){
        if (this.hasComponent(Transform)){
            const transform = this.getComponent(Transform);
            return transform.worldPosition;
        }
        const rect = this.baseElement.getBoundingClientRect();
        return {x:rect.left+rect.width/2, y:rect.top+rect.height/2};
    }

    onDestroy(){
        this.parent_slot?.removeChild(this.baseElement);
    }
}
