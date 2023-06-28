import { IntTopic, StringTopic } from "objectsync-client"
import { Control } from "./control";
import { HtmlItem } from "../../component/htmlItem"
import { print } from "../../devUtils"

export class TextControl extends Control {
    
    textField: HTMLInputElement
    text = this.getAttribute("text", StringTopic)
    label = this.getAttribute("label", StringTopic)
    editable = this.getAttribute("editable", IntTopic)

    protected template = `
    <div class="control flex-horiz">
        <div class="label" id="label">Text</div>
        <input type="text" class="text-field full-width" id="text-field">
    </div>
    `

    protected onStart(): void {
        super.onStart()
        this.textField = this.htmlitem.getEl("text-field", HTMLInputElement)
        this.link(this.text.onSet, (text) => { this.textField.value = text })
        this.textField.addEventListener("input", (e) => {
            this.text.set(this.textField.value)
        })
        let labelEl = this.htmlitem.getEl("label")
        this.link(this.label.onSet, (label) => {
            labelEl.textContent = label
        })
        this.link(this.editable.onSet, (editable) => {
            this.textField.disabled = !editable
        })
    }

}