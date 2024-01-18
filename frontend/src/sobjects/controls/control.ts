import { SObject } from "objectsync-client"
import { CompSObject } from "../compSObject"
import { HtmlItem } from "../../component/htmlItem"
import { Node } from "../node"
import { as } from "../../utils"
import { ControlHost } from "./controlHost"

function asControlHost(object: SObject): ControlHost {
    //ordinary as() can't be used since interface doesn't have a constructor
    //so here we check the properties directly
    let typeErasedObject = object as unknown as ControlHost
    if (typeErasedObject.htmlItem !== undefined && typeErasedObject.ancestorNode !== undefined) {
        return typeErasedObject;
    }   
    if (typeErasedObject === null) {
        return null;
    }
    throw new Error(`Value ${object} is not instance of ControlHost`);
}

export class Control extends CompSObject {
    protected get node(): Node {
        return asControlHost(this.parent).ancestorNode;
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
        this.htmlItem.setParent(asControlHost(newParent).htmlItem,'control')
    }
}