import { ObjectSyncClient } from "objectsync-client"
import { CompSObject } from "../sobjects/compSObject"
import { ExposedAttributeInfo, Inspector } from "../inspector/inspector"
import { HtmlItem } from "../component/htmlItem"
import { Sidebar } from "../sobjects/sidebar"

export class Settings extends CompSObject{
    inspector: Inspector = new Inspector()

    protected onStart(): void {
        this.inspector.htmlItem.setParentElement(document.getElementById('tab-settings'))
        let info = new ExposedAttributeInfo()
        info.name = "parent_id/0_1"
        info.editor_args = {'type':'text'}
        info.display_name = "parent_id/0_1"
        this.inspector.update(new Map([['ty',[info]]]))
    }
    
}