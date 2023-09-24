import { EventTopic, Topic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { as } from "../utils"

export class ButtonEditor extends Componentable {

    get template() {
        return `
        <div class="attribute-editor flex-horiz stretch">
            <button id="btn" type="button" class="btn grow"></button>
        </div>
        `
    }

    get style(): string {
        return super.style + `
        .btn{
            
        }
    `
    }

    readonly button: HTMLButtonElement
    readonly connectedAttributes: EventTopic[] = []
    private locked = false;

    constructor(displayName: string, editorArgs: any, connectedAttributes: Topic<any>[]) {
        super()
        //this.connectedAttributes = connectedAttributes
        for(let attr of connectedAttributes){
            this.connectedAttributes.push(as(attr,EventTopic))
        }
        this.button = as(this.htmlItem.getHtmlEl('btn'), HTMLButtonElement)
        this.button.innerText = displayName
        this.linker.link2(this.button, 'click', this.buttonClicked)
    }

    private buttonClicked() {
        for(let attr of this.connectedAttributes){
            attr.emit()
        }
    }

}
