import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic} from 'objectsync-client'
import { editor } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'
import { Node } from './node'
import { Null, print } from '../devUtils'
import { Action, Vector2, as } from '../utils'
import { MouseOverDetector } from '../component/mouseOverDetector'
import { EventDispatcher } from '../component/eventDispatcher'
import { Edge } from './edge'

export class Port extends CompSObject {

    name: StringTopic = this.getAttribute('name', StringTopic)
    is_input: IntTopic = this.getAttribute('is_input', IntTopic)
    orientation: number=0;

    private node: Node = Null();
    
    element = document.createElement('div')

    htmlItem: HtmlItem;

    moved: Action<[]> = new Action();

    set displayLabel(value: boolean) {
        if (value) {
            this.htmlItem.getHtmlEl('label').style.display = 'block'
        } else {
            this.htmlItem.getHtmlEl('label').style.display = 'none'
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

        let transform = new Transform(this,this.htmlItem.getHtmlEl('Knob'))
        transform.pivot = new Vector2(0.5,0)

        let eventDispatcher = new EventDispatcher(this,this.htmlItem.getHtmlEl('Knob'))
        eventDispatcher.onDragStart.add(this.generateEdge.bind(this))

        new MouseOverDetector(this,this.htmlItem.getHtmlEl('Knob'))

        // Bind attributes to UI
        
        this.name.onSet.add((label: string) => {
            this.htmlItem.getHtmlEl('label').innerText = label
        })

        this.is_input.onSet.add((is_input: number) => {
            if(is_input) {
                this.orientation = Math.PI
            }else{
                this.orientation = 0
            }
            this.isInputChanged(this.is_input.getValue())
        })
        // Initialize UI
    }

    // onParentChangedTp(oldValue: CompSObject | undefined, newValue: CompSObject| undefined): void {
    //     super.onParentChangedTp(oldValue, newValue)
    //     this.isInputChanged(this.is_input.getValue())
    //     this.node = as(newValue, Node);
    //     oldValue?.getComponent(Transform).onChange.remove(this.moved.invoke.bind(this.moved))
    //     this.node.getComponent(Transform).onChange.add(this.moved.invoke.bind(this.moved))
    //     this.moved.invoke()
    // }


    protected onParentChangedFrom(oldValue: CompSObject): void {
        super.onParentChangedFrom(oldValue)
        this.isInputChanged(this.is_input.getValue())
        oldValue.getComponent(Transform).onChange.remove(this.moved.invoke.bind(this.moved))
    }

    protected onParentChangedTo(newValue: CompSObject): void {
        super.onParentChangedTo(newValue)
        this.isInputChanged(this.is_input.getValue())
        this.node = as(newValue, Node);
        this.node.getComponent(Transform).onChange.add(this.moved.invoke.bind(this.moved))
        this.moved.invoke()
    }

    private isInputChanged(is_input: number): void {
        if(is_input) {
            this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem)!, 'input_port')
            this.htmlItem.getHtmlEl('Knob').classList.remove('OutPort')
            this.htmlItem.getHtmlEl('Knob').classList.add('InPort')
        } else {
            this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem)!, 'output_port')
            this.htmlItem.getHtmlEl('Knob').classList.remove('InPort')
            this.htmlItem.getHtmlEl('Knob').classList.add('OutPort')
        }
        this.moved.invoke()
    }

    private generateEdge(): void {
        this.objectsync.clearPretendedChanges()
        this.objectsync.record((() => {
            let newEdge = as(this.objectsync.createObject('Edge', this.parent.parent.id),Edge)
            newEdge.tail.set(this)
            newEdge.head.set(this.node.in_ports.getValue()[0])
            print('new edge',newEdge)
        }),true)
    }
}