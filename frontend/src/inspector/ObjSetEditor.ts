import { ObjSetTopic} from "objectsync-client"
import { Componentable } from "../component/componentable"
import { as } from "../utils"
import { Workspace } from "../sobjects/workspace"
import { SelectionManager } from "../component/selectionManager"
import { Selectable } from "../component/selectable"
import { Edge } from "../sobjects/edge"
import { Node } from "../sobjects/node"
import { print } from "../devUtils"
import { Editor } from "./Editor"

export class ObjSetEditor extends Editor<ObjSetTopic<Node|Edge>> {

    get template() {
        return `
        <div class="attribute-editor flex-horiz stretch">
            <div id="attribute-name" class="attribute-name"></div>
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
    private attribute: ObjSetTopic<Node|Edge>;

    constructor(displayName: string, editorArgs: any, connectedAttributes: ObjSetTopic<Node|Edge>[]) {
        super()
        if(connectedAttributes.length != 1) return; // No support for multiple attributes
        this.attribute = connectedAttributes[0]
        this.selectionManager = Workspace.instance.functionalSelection
        this.button = as(this.htmlItem.getHtmlEl('input'), HTMLButtonElement)
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName
        this.linker.link2(this.button, 'click', this.selectPressed)
        this.componentManager.destroy
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
        Workspace.instance.selection.enabled = false
        this.selectionManager.enabled = true
        this.selectionManager.clearSelection()
        for(let obj of this.attribute.getValue()){
            if(obj instanceof Node || obj instanceof Edge){
                this.selectionManager.select(obj.functionalSelectable)
            }
        }
        this.link(this.selectionManager.onSelect,this.onSelect)
        this.link(this.selectionManager.onDeselect,this.onDeselect)
        this.link(this.attribute.onAppend,(obj: Node|Edge) => {this.selectionManager.select(obj.functionalSelectable)})
        this.link(this.attribute.onRemove,(obj: Node|Edge) => {this.selectionManager.deselect(obj.functionalSelectable)})

    }

    private endSelect() {
        this.unlink(this.selectionManager.onSelect)
        this.unlink(this.selectionManager.onDeselect)
        this.unlink(this.attribute.onAppend)
        this.unlink(this.attribute.onRemove)
        this.selectionManager.clearSelection()
        this.selectionManager.enabled = false
        Workspace.instance.selection.enabled = true
    }

    private onSelect(selectable: Selectable) {
        if(selectable.object instanceof Node || selectable.object instanceof Edge)
            this.attribute.append(selectable.object)
    }

    private onDeselect(selectable: Selectable) {
        if(selectable.object instanceof Node || selectable.object instanceof Edge)
            this.attribute.remove(selectable.object)
    }

    onDestroy(): void {
        if(this.selecting){
            this.endSelect()
        }   
    }
    
}
