import { EventDispatcher } from "./eventDispatcher"
import { HtmlItem } from "./htmlItem"
import { Linker } from "./linker"
import { IComponentable, ComponentManager } from "./component"
import { addCssToDocument, addPrefixToCssClasses, addPrefixToHtmlClasses} from "../utils"
import { print } from "../devUtils"


export class Componentable implements IComponentable {
    // This class has the common components by default, providing a convenient starting point for defining an IComponentable class.

    // The default value is an empty div because HtmlItem requires at least one element in the template.
    protected get template(): string { return '<div></div>' }
    protected get style(): string { return '' }
    private static styleAdded = new Set<string>()

    readonly htmlItem: HtmlItem
    readonly componentManager = new ComponentManager()
    protected readonly linker: Linker
    protected readonly link
    protected readonly link2
    protected readonly unlink
    readonly eventDispatcher: EventDispatcher

    constructor() {
        let prefix = this.constructor.name;
        let styleWithPrefix = addPrefixToCssClasses(this.style,prefix)
        let templateEl = document.createElement('template')
        templateEl.innerHTML = this.template
        addPrefixToHtmlClasses(templateEl,prefix)

        if (!Componentable.styleAdded.has(this.constructor.name) && this.style!='') {
            Componentable.styleAdded.add(this.constructor.name)
            addCssToDocument(styleWithPrefix)
        }
        
        this.htmlItem = new HtmlItem(this, null, templateEl)
        this.linker = new Linker(this)
        this.link = this.linker.link.bind(this.linker)
        this.link2 = this.linker.link2.bind(this.linker)
        this.unlink = this.linker.unlink.bind(this.linker)
        this.eventDispatcher = new EventDispatcher(this)

        this.componentManager.onDestroy.add(this.onDestroy.bind(this))
    }

    destroy(): void {
        this.componentManager.destroy()
    }

    onDestroy(): void {
    }

}
