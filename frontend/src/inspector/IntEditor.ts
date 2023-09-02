import { IntTopic, Topic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { as } from "../utils"
import { Workspace } from "../sobjects/workspace"

export class IntEditor extends Componentable {

    get template() {
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
    `
    }

    readonly input: HTMLInputElement
    readonly connectedAttributes: Topic<any>[]
    private locked = false;

    constructor(displayName: string, editorArgs: any, connectedAttributes: Topic<any>[]) {
        super()
        this.connectedAttributes = connectedAttributes
        this.input = as(this.htmlItem.getHtmlEl('input'), HTMLInputElement)
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName
        for (let attr of connectedAttributes) {
            attr = as(attr, IntTopic)
            this.linker.link(attr.onSet, this.updateValue)
        }
        this.linker.link2(this.input, 'input', this.inputChanged)
        this.updateValue()
    }

    private updateValue() {
        if (this.locked) return
        let value: number = null
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
            this.input.value = value.toString()
        }
    }

    private inputChanged() {
        this.locked = true
        Workspace.instance.record(() => {
            for (let attr of this.connectedAttributes) {
                attr = as(attr, IntTopic)
                attr.set(Number.parseInt(this.input.value))
            }
        })
        this.locked = false
    }
}
