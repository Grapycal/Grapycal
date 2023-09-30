import { IntTopic, StringTopic } from "objectsync-client"
import { Control } from "./control"
import { print } from "../../devUtils"
import { BindInputBoxAndTopic } from "../../ui_utils/interaction"


export class TextControl extends Control {
    
    textField: HTMLInputElement
    text = this.getAttribute("text", StringTopic)
    label = this.getAttribute("label", StringTopic)
    editable = this.getAttribute("editable", IntTopic)

    protected template = `
    <div class="control flex-horiz">
        <div class="label" id="label">Text</div>
        <input type="text" class="control-text text-field full-height full-width" id="text-field">
    </div>
    `

    protected onStart(): void {
        super.onStart()
        this.textField = this.htmlItem.getEl("text-field", HTMLInputElement)
        this.textField.value = this.text.getValue()
        
        new BindInputBoxAndTopic(this,this.textField, this.text,this.objectsync,true)

        let labelEl = this.htmlItem.getEl("label")
        this.link(this.label.onSet, (label) => {
            labelEl.textContent = label
        })

        this.link(this.editable.onSet, (editable) => {
            this.textField.disabled = !editable
        })
    }

}