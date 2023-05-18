import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic} from 'objectsync-client'
import { editor } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'

export class Node extends CompSObject {

    shape: StringTopic = this.getAttribute('shape', StringTopic) // round, block, blockNamed, hideBody
    output: StringTopic = this.getAttribute('output', StringTopic)
    label: StringTopic = this.getAttribute('label', StringTopic)
    translation: StringTopic = this.getAttribute('translation', StringTopic)
    is_preview: IntTopic = this.getAttribute('is_preview', IntTopic)
    in_ports: ListTopic = this.getAttribute('in_ports', ListTopic)
    
    element = document.createElement('div')

    htmlItem: HtmlItem;
    transform: Transform;

    template: string = `
    <div class="Node">
        <div id="label">

        </div>
        <div id="slot_default">
    </div>
    `

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        // Add Components
        this.htmlItem = new HtmlItem(this)
        this.transform = new Transform(this)
        this.htmlItem.applyTemplate(this.template)

        // Bind attributes to UI
        this.shape.onSet.add(this.reshape.bind(this))
        this.label.onSet.add((label: string) => {
            this.htmlItem.getById('label').innerText = label
        })
        this.translation.onSet.add((translation: string) => {
            const [x, y] = translation.split(',').map(parseFloat)
            this.transform.translation={x:x, y:y}
        })
        this.transform.translationChanged.add((x: number, y: number) => {
            this.translation.set(`${x},${y}`)
        })

        // Initialize UI
        this.reshape('block')
        this.transform.draggable = true
    }

    onParentChanged(oldValue: SObject | undefined, newValue: SObject): void {
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem) || editor.htmlItem)
        console.log('set parent', this.htmlItem.parent)
    }

    reshape(shape: string) {
        
    }
}

export class TextNode extends Node {
}