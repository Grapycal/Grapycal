import { StringTopic, Topic } from "objectsync-client"
import { ComponentManager, IComponentable } from "../component/component"
import { HtmlItem } from "../component/htmlItem"
import { as } from "../utils"
import { Linker } from "../component/linker"
import { Workspace } from "../sobjects/workspace"

export class TextEditor implements IComponentable {
    readonly template: string = `
    <div class="attribute-editor flex-horiz stretch">
        <div id="attribute-name"></div>
        <input id="input" type="text" class="text-editor">
    </div>
    `;

    readonly componentManager = new ComponentManager();
    readonly htmlItem: HtmlItem
    readonly input: HTMLInputElement
    readonly linker = new Linker(this);
    readonly connectedAttributes: Topic<any>[]
    private locked = false;

    constructor(displayName: string, editorArgs: any, connectedAttributes: Topic<any>[]) {
        this.connectedAttributes = connectedAttributes
        this.htmlItem = new HtmlItem(this)
        this.htmlItem.applyTemplate(this.template)
        this.input = as(this.htmlItem.getHtmlEl('input'), HTMLInputElement)
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName
        for (let attr of connectedAttributes) {
            attr = as(attr, StringTopic)
            this.linker.link(attr.onSet, this.updateValue)
        }
        this.linker.link2(this.input, 'input', this.inputChanged)
        this.updateValue()
    }

    private updateValue() {
        if (this.locked) return
        let value: string = null
        for (let attr of this.connectedAttributes) {
            if (value === null) {
                value = attr.getValue()
            } else {
                if (value !== attr.getValue()) {
                    value = null
                    break
                }
            }
        }
        if (value === null) {
            this.input.value = ''
            this.input.placeholder = 'multiple values'
        } else {
            this.input.value = value
        }
    }

    private inputChanged() {
        this.locked = true
        Workspace.instance.record(() => {
            for (let attr of this.connectedAttributes) {
                attr = as(attr, StringTopic)
                attr.set(this.input.value)
            }
        })
        this.locked = false
    }
}
