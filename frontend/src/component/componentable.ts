import { EventDispatcher } from "./eventDispatcher"
import { HtmlItem } from "./htmlItem"
import { Linker } from "./linker"
import { IComponentable, ComponentManager } from "./component"
import { print } from "../devUtils"


export class Componentable implements IComponentable {
    // This class has the common components by default, providing a convenient starting point for defining an IComponentable class.

    // The default value is an empty div because HtmlItem requires at least one element in the template.
    protected get template(): string { return '<div></div>' }
    protected get style(): string { return '' }
    readonly htmlItem: HtmlItem
    readonly componentManager = new ComponentManager()
    protected readonly linker: Linker
    protected readonly link
    protected readonly link2
    protected readonly unlink
    protected readonly unlink2
    readonly eventDispatcher: EventDispatcher

    constructor() {
        let templateEl = document.createElement('template')
        templateEl.innerHTML = this.template
        
        this.htmlItem = new HtmlItem(this, null, templateEl, this.style)
        this.linker = new Linker(this)
        this.link = this.linker.link.bind(this.linker)
        this.link2 = this.linker.link2.bind(this.linker)
        this.unlink = this.linker.unlink.bind(this.linker)
        this.unlink2 = this.linker.unlink2.bind(this.linker)
        this.eventDispatcher = new EventDispatcher(this)

        this.componentManager.onDestroy.add(this.onDestroy.bind(this))
    }

    destroy(): void {
        this.componentManager.destroy()
    }

    onDestroy(): void {
    }

}
