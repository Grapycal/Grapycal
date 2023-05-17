import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic} from 'objectsync-client'
import { editor } from '../app'
import { HtmlHierarchyItem } from '../component/htmlHierarchyItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'

export class Node extends CompSObject {

    shape: StringTopic = this.getAttribute('shape', StringTopic) // round, block, blockNamed, hideBody
    output: StringTopic = this.getAttribute('output', StringTopic)
    label: StringTopic = this.getAttribute('label', StringTopic)
    pos: StringTopic = this.getAttribute('pos', StringTopic)
    is_preview: IntTopic = this.getAttribute('is_preview', IntTopic)
    
    _element = document.createElement('div')
    get element() {
        return this._element
    }

    htmlHierarchyItem: HtmlHierarchyItem = new HtmlHierarchyItem(this, this._element)
    transform: Transform;


    labelElement: HTMLElement = this._element.appendChild(document.createElement('div'))

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        // Create UI
        this.element.classList.add('Node')

        // Add Components
        this.transform = new Transform(this)

        // Bind attributes to UI
        this.shape.onSet.add(this.reshape.bind(this))
        this.label.onSet.add((label: string) => {
            this.labelElement.innerText = label
        })

        // Initialize UI
        this.reshape('block')
        this.transform.makeDraggable()
    }

    onParentChanged(oldValue: SObject | undefined, newValue: SObject): void {
        this.htmlHierarchyItem.setParent(this.getComponentInAncestors(HtmlHierarchyItem) || editor.htmlHierarchyItem)
    }

    reshape(shape: string) {
        
    }
}

export class TextNode extends Node {
}