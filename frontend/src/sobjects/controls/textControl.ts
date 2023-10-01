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

    protected css: string = `
        .label{
            min-width: 20px;
        }
    `

    protected onStart(): void {
        super.onStart()
        this.textField = this.htmlItem.getEl("text-field", HTMLInputElement)
        this.textField.value = this.text.getValue()
        
        new BindInputBoxAndTopic(this,this.textField, this.text,this.objectsync,true)

        let labelEl = this.htmlItem.getEl("label", HTMLDivElement)
        this.link(this.label.onSet, (label) => {
            if (label == '') {
                labelEl.style.display = 'none'
                return
            }
            //replace spaces with non-breaking spaces
            label = label.replace(/ /g, "\u00a0")

            labelEl.innerHTML = label
        })

        this.link(this.editable.onSet, (editable) => {
            this.textField.disabled = !editable
        })
    }

}