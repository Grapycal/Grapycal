import { IntTopic, ObjSetTopic, SetTopic, Topic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { as } from "../utils"
import { Workspace } from "../sobjects/workspace"
import { SelectionManager } from "../component/selectionManager"
import { Selectable } from "../component/selectable"
import { Edge } from "../sobjects/edge"
import { Node } from "../sobjects/node"

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
    private selecting = false;
    private selectionManager: SelectionManager
    private attribute: ObjSetTopic;

    constructor(displayName: string, editorArgs: any, connectedAttributes: ObjSetTopic[]) {
        super()
        if(connectedAttributes.length != 1) return; // No support for multiple attributes
        this.attribute = connectedAttributes[0]
        this.selectionManager = Workspace.instance.functionalSelection
        this.button = as(this.htmlItem.getHtmlEl('input'), HTMLButtonElement)
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName
        this.linker.link(this.attribute.onSet,this.updateValue)
        this.linker.link2(this.button, 'click', this.selectPressed)
        this.initMarkers()
    }

    private initMarkers() {
        for(let obj of this.attribute.getValue()){
            if(obj instanceof Node){


    private updateValue() {
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
        if(this.selecting){
            this.selecting = false
            this.endSelect()
            this.button.innerText = 'Select'
        }else{
            this.selecting = true
            this.startSelect()
            this.button.innerText = 'End Select'
        }
    }

    private startSelect() {

    }

    private endSelect() {
        
    }

    private objectClicked(selectable:Selectable) {
        let obj = selectable.object
        if(!(obj instanceof Node || obj instanceof Edge)) return;
        if(this.attribute.has(obj)){
            this.attribute.remove(obj)
        }else{
            this.attribute.append(obj)
        }
    }
}
