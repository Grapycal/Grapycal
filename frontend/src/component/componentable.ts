import { EventDispatcher } from "./eventDispatcher"
import { HtmlItem } from "./htmlItem"
import { Linker } from "./linker"
import { IComponentable, ComponentManager } from "./component"
import { addCssToDocument, addPrefixToCssClasses, addPrefixToHtmlClasses, getStaticField as getStatic } from "../utils"


export class Componentable implements IComponentable {
    // This class has the common components by default, providing a convenient starting point for defining a componentable class.

    // Using static is a workaround to allow overriding the field in derived classes before super() is called.
    // The default value is an empty div because HtmlItem requires at least one element in the template.
    protected static template: string = '<div></div>';
    protected static style: string = '';
    private static styleAdded = false;

    readonly htmlItem: HtmlItem
    readonly componentManager = new ComponentManager();
    readonly linker: Linker
    readonly eventDispatcher: EventDispatcher

    constructor() {
        
        // let prefix = this.constructor.name;
        // let styleWithPrefix = addPrefixToCssClasses(getStatic(this, 'style'),prefix)
        // let templateEl = document.createElement('template')
        // templateEl.innerHTML = getStatic(this, 'template')
        // addPrefixToHtmlClasses(templateEl,prefix)

        // if (!Componentable.styleAdded && getStatic(this, 'style')!='') {
        //     Componentable.styleAdded = true;
        //     addCssToDocument(styleWithPrefix)
        // }
        // this.htmlItem = new HtmlItem(this, null, templateEl)
        this.htmlItem = new HtmlItem(this, null, getStatic(this, 'template'))
        this.linker = new Linker(this)
        this.eventDispatcher = new EventDispatcher(this)
    }

    destroy(): void {
        this.componentManager.destroy()
    }

}
