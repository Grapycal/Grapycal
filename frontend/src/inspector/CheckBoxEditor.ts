import { IntTopic, Topic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { as } from "../utils"
import { Workspace } from "../sobjects/workspace"
import { inputFinished } from "../ui_utils/interaction"
import { Editor } from "./Editor"

export class CheckBoxEditor extends Editor<SetTopic> {

    get template() {
        return `
        <div class="attribute-editor flex-horiz stretch">
            <div id="attribute-name" class="attribute-name"></div>
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
    private locked = false;

    constructor(displayName: string, editorArgs: any, connectedAttributes: SetTopic[]) {
        super()
        this.connectedAttributes = connectedAttributes as SetTopic[]
        this.input = as(this.htmlItem.getHtmlEl('input'), HTMLInputElement)
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName
        for (let attr of connectedAttributes) {
            attr = as(attr, IntTopic)
            this.linker.link(attr.onSet, this.updateValue)
        }
        this.linker.link(inputFinished(this.input),this.inputFinished)
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

    private inputFinished() {
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
