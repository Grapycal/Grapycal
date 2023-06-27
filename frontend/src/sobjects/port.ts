import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic} from 'objectsync-client'
import { editor } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'
import { Node } from './node'
import { print } from '../devUtils'
import { Action, Vector2, as } from '../utils'
import { MouseOverDetector } from '../component/mouseOverDetector'
import { EventDispatcher } from '../component/eventDispatcher'
import { Edge } from './edge'

export class Port extends CompSObject {

    name: StringTopic = this.getAttribute('name', StringTopic)
    is_input: IntTopic = this.getAttribute('is_input', IntTopic)
    max_edges: IntTopic = this.getAttribute('max_edges', IntTopic)
    orientation: number=0;

    private node: Node = null;
    
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

    // Managed by Edge class
    public edges: Edge[] = []

    readonly template: string = `
    <div class="Port">
        <div class="port-knob" id="Knob">
            <div class="port-label" id="label">
            </div>
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
        transform.pivot = new Vector2(0,0)

        let eventDispatcher = new EventDispatcher(this,this.htmlItem.getHtmlEl('Knob'))
        this.link(eventDispatcher.onDragStart,this.generateEdge.bind(this))

        new MouseOverDetector(this,this.htmlItem.getHtmlEl('Knob'))

        // Bind attributes to UI

        this.displayLabel = false
        
        this.link(this.name.onSet,(label: string) => {
            this.htmlItem.getHtmlEl('label').innerText = label
        })
    }

    protected onStart(): void {
        super.onStart()
        this.link(this.is_input.onSet,(is_input: number) => {
            if(is_input) {
                this.orientation = Math.PI
            }else{
                this.orientation = 0
            }
            this.isInputChanged(this.is_input.getValue())
        })
    }


    protected onParentChangedFrom(oldValue: CompSObject): void {
        super.onParentChangedFrom(oldValue)
        this.isInputChanged(this.is_input.getValue())
        if(oldValue.hasComponent(Transform))
            oldValue.getComponent(Transform).onChange.remove(this.moved.invoke.bind(this.moved))
    }

    protected onParentChangedTo(newValue: CompSObject): void {
        super.onParentChangedTo(newValue)
        this.isInputChanged(this.is_input.getValue())
        this.node = as(newValue, Node);
        if(this.node.hasComponent(Transform))
            this.node.getComponent(Transform).onChange.add(this.moved.invoke.bind(this.moved))
        this.moved.invoke()
    }



    public acceptsEdge(): boolean {
        if(this.max_edges.getValue() > this.edges.length) return true
        return false
    }

    private isInputChanged(is_input: number): void {
        if(is_input) {
            this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem)!, 'input_port')
            this.htmlItem.getHtmlEl('Knob').classList.remove('out-port')
            this.htmlItem.getHtmlEl('Knob').classList.add('in-port')
        } else {
            this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem)!, 'output_port')
            this.htmlItem.getHtmlEl('Knob').classList.remove('in-port')
            this.htmlItem.getHtmlEl('Knob').classList.add('out-port')
        }
        this.moved.invoke()
    }

    private generateEdge(): void {
        if(this.node.isPreview)
            return;
        this.objectsync.clearPretendedChanges()
        this.objectsync.record((() => {
            let newEdge = as(this.objectsync.createObject('Edge', this.parent.parent.id),Edge)
            if(this.is_input.getValue()){
                newEdge.addTag('CreatingDragTail')
                newEdge.head.set(this)
            }
            else{
                newEdge.addTag('CreatingDragHead')
                newEdge.tail.set(this)
            }
        }),true)
    }
}