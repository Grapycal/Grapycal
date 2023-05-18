import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic} from 'objectsync-client'
import { editor } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'

export class Port extends CompSObject {

    name: StringTopic = this.getAttribute('name', StringTopic)
    is_input: IntTopic = this.getAttribute('is_input', IntTopic)
    
    element = document.createElement('div')

    htmlItem: HtmlItem;

    set displayLabel(value: boolean) {
        if (value) {
            this.htmlItem.getById('label').style.display = 'block'
        } else {
            this.htmlItem.getById('label').style.display = 'none'
        }
    }

    readonly template: string = `
    <div class="Port">
        <div class="Knob" id="Knob"></div>
        <div id="label">
        </div>
    </div>
    `

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        // Create UI

        // Add Components
        this.htmlItem = new HtmlItem(this)
        this.htmlItem.applyTemplate(this.template)

        let transform = new Transform(this,this.htmlItem.getById('Knob'))
        transform.pivot = {x: 0.5, y: 0}

        // Bind attributes to UI
        
        this.name.onSet.add((label: string) => {
            this.htmlItem.getById('label').innerText = label
        })

        this.is_input.onSet.add((is_input: number) => {
            this.isInputChanged(this.is_input.getValue())
        })
        // Initialize UI
    }

    onParentChanged(oldValue: SObject | undefined, newValue: SObject): void {
        super.onParentChanged(oldValue, newValue)
        this.isInputChanged(this.is_input.getValue())
    }

    private isInputChanged(is_input: number): void {
        if(is_input) {
            this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem)!, 'input_port')

            this.htmlItem.getById('Knob').classList.remove('OutPort')
            this.htmlItem.getById('Knob').classList.add('InPort')
        } else {
            this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem)!, 'output_port')
            this.htmlItem.getById('Knob').classList.remove('InPort')
            this.htmlItem.getById('Knob').classList.add('OutPort')
        }
    }
}

export class TextNode extends Node {
}