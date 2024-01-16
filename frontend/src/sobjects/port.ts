import {ObjectSyncClient, StringTopic, IntTopic} from 'objectsync-client'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'
import { Node } from './node'
import { print } from '../devUtils'
import { Action, Vector2, as } from '../utils'
import { MouseOverDetector } from '../component/mouseOverDetector'
import { EventDispatcher } from '../component/eventDispatcher'
import { Edge } from './edge'
import { ControlHost } from './controls/controlHost'

export class Port extends CompSObject implements ControlHost {

    display_name: StringTopic = this.getAttribute('display_name', StringTopic)
    is_input: IntTopic = this.getAttribute('is_input', IntTopic)
    max_edges: IntTopic = this.getAttribute('max_edges', IntTopic)
    use_default: IntTopic = this.getAttribute('use_default', IntTopic)
    default_control_display: string
    orientation: number=0;

    private node: Node = null;
    
    element = document.createElement('div')

    htmlItem: HtmlItem;
    get ancestorNode(): Node {
        return this.node;
    }

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
    <div class="port">

        <div class="port-label" id="label"></div>
        <div class="slot-control" id="slot_control"></div>
        <div class="port-knob" id="Knob">
            <div class="port-knob-hitbox" id="Hitbox"></div>
        </div>

    </div>
    `

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        // Add Components
        this.htmlItem = new HtmlItem(this)
        this.htmlItem.applyTemplate(this.template)

        let transform = new Transform(this,this.htmlItem.getHtmlEl('Knob'))
        transform.pivot = new Vector2(0,0)

        let eventDispatcher = new EventDispatcher(this,this.htmlItem.getHtmlEl('Hitbox'))
        this.link(eventDispatcher.onDragStart,this.generateEdge.bind(this))

        new MouseOverDetector(this,this.htmlItem.getHtmlEl('Hitbox'))

        // Bind attributes to UI

        this.displayLabel = true
        
        this.link(this.display_name.onSet,(label: string) => {
            this.htmlItem.getHtmlEl('label').innerText = label
            if(this.node)
                this.node.setMinWidth( this.htmlItem.getHtmlEl('label').offsetWidth + 18) 
        })

        this.default_control_display = this.htmlItem.getHtmlEl('slot_control').style.display
        this.link(this.use_default.onSet,(use_default: number) => {
            if(use_default) {
                this.htmlItem.getHtmlEl('slot_control').style.display = this.default_control_display
            } else {
                this.htmlItem.getHtmlEl('slot_control').style.display = 'none'
            }
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
            as(oldValue,Node).moved.remove(this.moved.invoke)
    }

    protected onParentChangedTo(newValue: CompSObject): void {
        super.onParentChangedTo(newValue)
        this.isInputChanged(this.is_input.getValue())
        this.node = as(newValue, Node);
        if(this.node.hasComponent(Transform))
            this.node.moved.add(this.moved.invoke)
        this.node.setMinWidth( this.htmlItem.getHtmlEl('label').offsetWidth + 18)
        this.moved.invoke()
    }



    public get acceptsEdge(): boolean {
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
        if(!this.acceptsEdge)
            return;
        this.objectsync.clearPretendedChanges()
        this.objectsync.record((() => {
            let newEdge = as(this.objectsync.createObject('Edge', this.parent.parent.id),Edge)
            if(this.is_input.getValue()){
                newEdge.addTag('CreatingDragTail')
                newEdge.head.set(this)
                newEdge.data_ready.set(123)
            }
            else{
                newEdge.addTag('CreatingDragHead')
                newEdge.tail.set(this)
                newEdge.data_ready.set(123)
            }
        }),true)
    }
}