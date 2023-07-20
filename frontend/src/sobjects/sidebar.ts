import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic, ObjectTopic} from 'objectsync-client'
import { CompSObject } from './compSObject'
import { HtmlItem } from '../component/htmlItem'
import { HeirarchyNode } from '../ui_utils/hierarchyNode'
import { Workspace } from './workspace'
import { as } from '../utils'

export class Sidebar extends CompSObject {
    private items: HtmlItem[] = []
    nodeLibrary: HeirarchyNode = new HeirarchyNode('', '',true);
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