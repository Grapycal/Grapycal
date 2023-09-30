import { SObject } from "objectsync-client"
import { CompSObject } from "../compSObject"
import { HtmlItem } from "../../component/htmlItem"
import { Node } from "../node"
import { as } from "../../utils"

export class Control extends CompSObject {
    protected get node(): Node {
        return as(this.parent,Node)
    }
    protected template = `
    <div class="control">
        this is a control
    </div>
    `
    protected css = ``
    htmlItem: HtmlItem
    protected onStart(): void {
        super.onStart();
        this.htmlItem=new HtmlItem(this,null,this.template,this.css)
    }
    
    onParentChangedTo(newParent: SObject): void {
        super.onParentChangedTo(newParent)
        this.htmlItem.setParent(as(newParent,Node).htmlItem,'control')
    }
}