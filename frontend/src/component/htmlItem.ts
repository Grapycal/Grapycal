import { print } from "../devUtils"
import { Action, Constructor, Vector2, as, defined } from "../utils"
import { Component, IComponentable } from "./component"
import { Transform } from "./transform"

function addPrefixToHtmlClasses(html: Element, prefix: string): void{
    let target:Element|DocumentFragment = html;
    if(html instanceof HTMLTemplateElement)
        target = html.content;
    target.querySelectorAll('[class]').forEach(element => {
        const classList = element.classList;
        classList.forEach(className => {
            // The original class is preserved. For example, .class becomes .class .prefix-class
            // The original class is used by the theme css.
            classList.add(`${prefix}-${className}`);
        });
    });
}

function addCssToDocument(css:string){
    var style = document.createElement('style')
    style.innerHTML = css
    document.head.prepend(style) // allow overriding by theme css
}

function addPrefixToCssClasses(css: string, prefix: string): string{
    return css.replace(/\.([a-zA-Z0-9_-]+)[ ]*\{/g, (match, className) => {
        return `.${prefix}-${className}{`;
    });
}

export class HtmlItem extends Component{
    private static styleAdded = new Set<string>()

    static templateIdGenerator: number = 0;

    baseElement: Element;
    parent_slot: Element;
    slots: Map<string,HTMLElement> = new Map();
    parent_: HtmlItem;
    get parent(){return this.parent_;}
    children: {item:HtmlItem,slotName:string,order:'append'|'prepend'}[] = [];
    readonly templateChanged = new Action<[]>();
    templateId: string='';
    private useCss: boolean = false;

    constructor(object:IComponentable, specifiedParentElement: HTMLElement = null, template: string|HTMLTemplateElement = null,
        css = ''
        ){
        super(object);
        this.baseElement = null;
        this.parent_ = null;
        this.parent_slot = specifiedParentElement;

        if(css !== ''){
            if (!HtmlItem.styleAdded.has(object.constructor.name)) {
                HtmlItem.styleAdded.add(object.constructor.name)

                css = addPrefixToCssClasses(css, this.object.constructor.name);
                addCssToDocument(css);
            }
            this.useCss = true;
        }

        if(template !== null)
            this.applyTemplate(template);
    }

    applyTemplate(template: string|HTMLTemplateElement, order: "prepend"|"append" = "prepend"){
        // create element from template
        if (this.baseElement !== null)
            this.parent_slot.removeChild(this.baseElement);

        let templateElement: HTMLTemplateElement;
        if(typeof template === 'string'){
            templateElement = document.createElement('template');
            templateElement.innerHTML = template;
        }else{
            templateElement = template;
        }

        if(this.useCss){
            addPrefixToHtmlClasses(templateElement, this.object.constructor.name);
        }

        this.baseElement = defined(templateElement.content.firstElementChild);

        //turn off autocomplete
        for(let element of this.baseElement.querySelectorAll('input,textarea')){
            element.setAttribute('autocomplete','off');
        }

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
        const slotElements = this.baseElement.querySelectorAll('[id^="slot_"]')
        if(this.baseElement.id.startsWith('slot_')){
            const slotName = this.baseElement.id.slice(5);
            this.addSlot(slotName, as(this.baseElement,HTMLElement));
        }

        for(let element of slotElements){
            const slotName = element.id.slice(5);
            this.addSlot(slotName, as(element,HTMLElement));
        }
        
        // move children to slots
        for(let child of this.children){
            if(child.item.baseElement===null) continue;
            const slot = this.slots.get(child.slotName);
            if(slot === undefined)
                throw new Error(`Slot ${child.slotName} not found`);
            if(order === "append")
                slot.appendChild(child.item.baseElement);
            else
                slot.prepend(child.item.baseElement);
        }
        
        this.templateChanged.invoke();
    }

    addChild(child: HtmlItem,slotName: string, order: "prepend"|"append" = "prepend"){
        const slot = this.slots.get(slotName);
        if(slot === undefined)
            throw new Error(`Slot ${slotName} not found`);

        if(child.baseElement===null) return slot;
        if(order === "append")
            slot.appendChild(child.baseElement);
        else
            slot.prepend(child.baseElement);
        this.children.push({item:child,slotName:slotName,order:order});
        return slot;
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

    getHtmlElByClass(className: string): HTMLElement{
        //match class and template_id
        const element = this.baseElement.querySelector(`[template_id="${this.templateId}"].${className}`);
        //const element = this.baseElement.querySelector(`.${className}`);
        //check baseElement
        if (this.baseElement.classList.contains(className))
            return as(this.baseElement,HTMLElement);
        if (element === null)
            throw new Error(`Element with class ${className} not found`);
        return as(element,HTMLElement);
    }

    getElByClass<T extends Element>(className: string,type?:Constructor<T>): T{
        //match class and template_id
        const element = this.baseElement.querySelector(`[template_id="${this.templateId}"].${className}`);
        //const element = this.baseElement.querySelector(`.${className}`);
        //check baseElement
        if (this.baseElement.classList.contains(className))
            if(type === undefined){
                return this.baseElement as any;
            }else{
                return as(this.baseElement,type);
            }
        if (element === null)
            throw new Error(`Element with class ${className} not found`);
        if(type === undefined){
            return element as any;
        }else{
            return as(element,type);
        }
    }



    setParent(parent: HtmlItem, slot: string = 'default', order: "prepend"|"append"="append"): void{
        if (this.parent_ === parent) return;
        this.parent_ = parent;
        this.parent_slot = parent.addChild(this,slot,order);
    }

    setParentElement(parent: Element): void{
        if (this.parent_slot === parent) return;
        this.parent_slot = parent;
        this.parent_slot.appendChild(this.baseElement);
    }

    moveToFront(){
        if (this.parent_slot === null) return;
        if (this.parent_slot.lastElementChild === this.baseElement) return;
        this.parent_slot.appendChild(this.baseElement);
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
            if (child.item.componentManager.hasComponent(Transform))
                transforms.push(child.item.getComponent(Transform));
            else
                transforms.push(...child.item.findTransformChildren());
        }
        return transforms;
    }

    get position(){
        if (this.hasComponent(Transform)){
            const transform = this.getComponent(Transform);
            return transform.worldPosition;
        }
        const rect = this.baseElement.getBoundingClientRect();
        return new Vector2(rect.left+rect.width/2, rect.top+rect.height/2)
    }

    onDestroy(){
        this.parent_slot?.removeChild(this.baseElement);
    }
}
