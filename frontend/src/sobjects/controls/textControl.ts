import { StringTopic } from "objectsync-client"
import { Control } from "./control";
import { HtmlItem } from "../../component/htmlItem"
import { print } from "../../devUtils"

export class TextControl extends Control {
    text = this.getAttribute("text", StringTopic)
    textField: HTMLInputElement

    protected template = `
    <div class="control">
        <input type="text" class="text-field" id="text-field">
    </div>
    `

    protected onStart(): void {
        print("TextControl.onStart")
        super.onStart()
        this.textField = this.htmlitem.getEl("text-field", HTMLInputElement)
        this.link(this.text.onSet, (text) => { this.textField.value = text })
        this.textField.addEventListener("input", (e) => {
            this.text.set(this.textField.value)
        })
    }

}