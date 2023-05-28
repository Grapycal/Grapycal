import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic, ObjectTopic} from 'objectsync-client'
import { CompSObject } from './compSObject'
import { editor } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { HeirarchyNode } from '../ui_utils/hierarchyNode'

export class Sidebar extends CompSObject {
    nodeLibrary: HeirarchyNode = new HeirarchyNode('', true);
    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)
        this.nodeLibrary.htmlItem.setParent(editor.componentManager.getComponent(HtmlItem), 'sidebar')
        let test = new HtmlItem(this)
        test.applyTemplate(`
        <div>
            rsdfg
        </div>
        `)
        let test2 = new HtmlItem(this)
                test2.applyTemplate(`
                <div>
                    rsdfg
                </div>
                `)
        this.nodeLibrary.addLeaf(test, 'function/arithmetic/aaa')
        this.nodeLibrary.addLeaf(test2, 'function/arithmetic/bbb')
    }
}