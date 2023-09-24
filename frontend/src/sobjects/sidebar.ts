import { CompSObject } from './compSObject'
import { HtmlItem } from '../component/htmlItem'
import { HierarchyNode } from '../ui_utils/hierarchyNode'
import { Workspace } from './workspace'
import { as } from '../utils'

export class Sidebar extends CompSObject {
    private items: HtmlItem[] = []
    nodeLibrary: HierarchyNode = new HierarchyNode('', '',true);
    onStart() {
        let workspace = as(this.parent,Workspace)
        this.nodeLibrary.htmlItem.setParentElement(document.getElementsByClassName('sidebar-slot')[0])
    }

    addItem(htmlItem: HtmlItem, path: string) {
        this.nodeLibrary.addLeaf(htmlItem, path)
        this.items.push(htmlItem)
    }

    hasItem(htmlItem: HtmlItem) {
        return this.items.includes(htmlItem)
    }

    removeItem(htmlItem: HtmlItem, path: string) {
        this.nodeLibrary.removeLeaf(htmlItem, path)
        this.items.splice(this.items.indexOf(htmlItem), 1)
    }
    
}