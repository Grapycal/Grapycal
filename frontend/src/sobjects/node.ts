import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic} from 'objectsync-client'
import { editor } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'
import { print } from '../devUtils'
import { Port } from './port'
import { glowDiv as glowDiv, glowText } from '../ui_utils/effects'
import { as } from '../utils'

export class Node extends CompSObject {

    shape: StringTopic = this.getAttribute('shape', StringTopic) // round, block, blockNamed, hideBody
    output: StringTopic = this.getAttribute('output', StringTopic)
    label: StringTopic = this.getAttribute('label', StringTopic)
    translation: StringTopic = this.getAttribute('translation', StringTopic)
    is_preview: IntTopic = this.getAttribute('is_preview', IntTopic)

    in_ports: ObjListTopic<Port> = this.getAttribute('in_ports', ObjListTopic<Port>)
    out_ports: ObjListTopic<Port> = this.getAttribute('out_ports', ObjListTopic<Port>)
    
    element = document.createElement('div')

    htmlItem: HtmlItem;
    transform: Transform;

    readonly templates: {[key: string]: string} = {
    block: 
    `<div class="Node flex-horiz space-between" style="min-width:150px;">
        <div id="slot_input_port" class="no-width flex-vert space-evenly"></div>
        <div class="full-width flex-vert space-evenly"> 
            <div id="label" class="center" ></div>
        </div>
        <div id="slot_output_port" class="no-width flex-vert space-evenly"></div>
    </div>`,
    }

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        // Add Components
        this.htmlItem = new HtmlItem(this)
        this.transform = new Transform(this)

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

        this.in_ports.onInsert.add((port: SObject) => {
            this.reshapePort(as(port,Port))
        })

        this.out_ports.onInsert.add((port: SObject) => {
            this.reshapePort(as(port,Port))
        })

        // Initialize UI

        this.reshape('block')
        this.transform.draggable = true
    }

    onParentChanged(oldValue: SObject | undefined, newValue: SObject): void {
        super.onParentChanged(oldValue, newValue)
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem) || editor.htmlItem)
    }

    reshape(shape: string) {
        this.htmlItem.applyTemplate(this.templates[shape])
        glowDiv(this.htmlItem.baseElement)
        //glow text
        for(let div of this.htmlItem.baseElement.querySelectorAll('div')){
            glowText(div)
        }
        for(const port of this.in_ports){
            this.reshapePort(port)
        }
    }

    reshapePort(port:Port){
        if(this.shape.getValue() == 'block'){
            port.displayLabel = false
        }
    }
}

export class TextNode extends Node {
}