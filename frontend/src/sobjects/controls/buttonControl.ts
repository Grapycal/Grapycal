import { StringTopic } from "objectsync-client"
import { Control } from "./control";
import { print } from "../../devUtils"

export class ButtonControl extends Control {
    
    button: HTMLInputElement
    label = this.getAttribute("label", StringTopic)

    protected template = `
    <div class="control flex-horiz">
        <button class="control-button full-height full-width" id="button"></button>
    </div>
    `

    protected onStart(): void {
        super.onStart()
        this.button = this.htmlItem.getEl("button")
        this.link(this.label.onSet, (label) => {
            this.button.textContent = label
        })
        this.button.addEventListener("click", (e) => {
            this.emit("click")
        })
    }

}