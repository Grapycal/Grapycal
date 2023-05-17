import { Null, print } from "../devUtils"
import { Component, IComponentable } from "./component"
import { Transform } from "./transform"

export class HtmlHierarchyItem extends Component{
    baseElement: HTMLElement;
    slots: Map<string,HTMLElement>;
    parent_: HtmlHierarchyItem;
    get parent(){return this.parent_;}
    constructor(object:IComponentable,baseElement: HTMLElement, slots: Map<string,HTMLElement>|HTMLElement|null = null){
        super(object);
        this.baseElement = baseElement;
        if (slots instanceof HTMLElement)
            this.slots = new Map([['',slots]]);
        else if (slots === null)
            this.slots = new Map();
        else
            this.slots = slots;
        this.parent_ = Null();
    }
    setParent(parent: HtmlHierarchyItem, slot: string = ''): void{
        parent.getSlot(slot).appendChild(this.baseElement);
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
        let i : HtmlHierarchyItem = this.parent;
        while (i !== null){
            if (i.componentManager.hasComponent(Transform))
                return i.getComponent(Transform);
            i = i.parent;
        }
        return null;
    }
}
