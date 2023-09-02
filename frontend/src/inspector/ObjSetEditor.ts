import { IntTopic, SetTopic, Topic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { as } from "../utils"
import { Workspace } from "../sobjects/workspace"

export class ObjSetEditor extends Componentable {

    get template() {
        return `
        <div class="attribute-editor flex-horiz stretch">
            <div id="attribute-name"></div>
            <button id="input" type="button" class="grow btn">Select</button>
        </div>
        `
    }

    get style(): string {
        return super.style + `
        .text-editor{
            width: 100px;
        }
        .btn{
            font-size:inherit;
        }
    `
    }

    readonly button: HTMLButtonElement
    readonly connectedAttributes: Topic<any>[]
    private locked = false;

    constructor(displayName: string, editorArgs: any, connectedAttributes: Topic<any>[]) {
        super()
        this.connectedAttributes = connectedAttributes
        this.button = as(this.htmlItem.getHtmlEl('input'), HTMLButtonElement)
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName
        for (let attr of connectedAttributes) {
            attr = as(attr, SetTopic)
            this.linker.link(attr.onSet, this.updateValue)
        }
        this.linker.link2(this.button, 'click', this.selectPressed)
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
    }

    private selectPressed() {
    }
}
