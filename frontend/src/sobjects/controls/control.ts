import { SObject } from "objectsync-client"
import { CompSObject } from "../compSObject"
import { HtmlItem } from "../../component/htmlItem"
import { Node } from "../node"
import { as } from "../../utils"

export class Control extends CompSObject {
    htmlitem = new HtmlItem(this)
    protected get node(): Node {
        return as(this.parent,Node)
    }
    protected template = `
    <div class="control">
        this is a control
    </div>
    `
    protected onStart(): void {
        super.onStart();
        this.htmlitem.applyTemplate(this.template)
    }
    
    onParentChangedTo(newParent: SObject): void {
        super.onParentChangedTo(newParent)
        this.htmlitem.setParent(as(newParent,Node).htmlItem,'control')
    }
}