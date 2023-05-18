import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic} from 'objectsync-client'
import { editor } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'

export class Port extends CompSObject {

    name: StringTopic = this.getAttribute('name', StringTopic)
    
    element = document.createElement('div')

    htmlItem: HtmlItem;
    transform: Transform;

    readonly template: string = `
    <div class="Port">
        <div id="label">
        </div>
    </div>
    `

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        // Create UI
        this.element.classList.add('Port')

        // Add Components
        this.htmlItem = new HtmlItem(this)
        this.htmlItem.applyTemplate(this.template)
        this.transform = new Transform(this)

        // Bind attributes to UI
        
        this.name.onSet.add((label: string) => {
            this.htmlItem.getById('label').innerText = label
        })

        // Initialize UI
    }

    onParentChanged(oldValue: SObject | undefined, newValue: SObject): void {
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem) || editor.htmlItem)
    }
}

export class TextNode extends Node {
}