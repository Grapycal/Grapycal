import { Null, print } from "../devUtils"
import { Action, as, defined } from "../utils"
import { Component, IComponentable } from "./component"
import { Transform } from "./transform"

export class HtmlItem extends Component{
    baseElement: HTMLElement;
    parent_slot: HTMLElement;
    slots: Map<string,HTMLElement> = new Map();
    parent_: HtmlItem;
    readonly templateChanged = new Action<[]>();

    get parent(){return this.parent_;}
    constructor(object:IComponentable, specifiedParentElement: HTMLElement = Null()){
        super(object);
        this.baseElement = Null();
        this.parent_ = Null();
        this.parent_slot = specifiedParentElement;
    }

    applyTemplate(template: string){
        // create element from template
        if (this.baseElement !== Null())
            this.parent_slot.removeChild(this.baseElement);

        const templateElement = document.createElement('template');
        templateElement.innerHTML = template;
        this.baseElement = as(templateElement.content.firstElementChild,HTMLElement);

        this.parent_slot?.appendChild(this.baseElement);

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

    private moveToSlot(slot: HTMLElement){
        if (this.baseElement !== Null()){
            this.parent_slot?.removeChild(this.baseElement);
            slot.appendChild(this.baseElement);
        }
        this.parent_slot = slot;
    }

    getById(id: string): HTMLElement{
        const element = this.baseElement.querySelector(`#${id}`);
        //check baseElement
        if (this.baseElement.id === id)
            return this.baseElement;
        if (element === null)
            throw new Error(`Element with id ${id} not found`);
        return as(element,HTMLElement);
    }

    setParent(parent: HtmlItem, slot: string = 'default'): void{
        this.moveToSlot(parent.getSlot(slot));
        this.parent_ = parent;
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
}
