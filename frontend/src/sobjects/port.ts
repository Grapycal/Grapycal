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
import { IControlHost } from './controls/controlHost'

export class Port extends CompSObject implements IControlHost {

    display_name: StringTopic = this.getAttribute('display_name', StringTopic)
    is_input: IntTopic = this.getAttribute('is_input', IntTopic)
    max_edges: IntTopic = this.getAttribute('max_edges', IntTopic)
    default_control_display: string
    orientation: number=0;

    private node: Node = null;
    
    element = document.createElement('div')

    htmlItem: HtmlItem;
    get ancestorNode(): Node {
        return this.node;
    }
    eventDispatcher: EventDispatcher;

    moved: Action<[]> = new Action();

    set displayLabel(value: boolean) {
        if (value) {
            this.htmlItem.getHtmlEl('label').style.display = 'block'
        } else {
            this.htmlItem.getHtmlEl('label').style.display = 'none'
        }
    }

    // Called by Edge class
    private edges: Edge[] = []
    addEdge(edge: Edge): void {
        this.edges.push(edge)
        this.htmlItem.baseElement.classList.add('has-edge')
        this.updateAcceptsEdgeClass()
    }
    removeEdge(edge: Edge): void {
        this.edges.splice(this.edges.indexOf(edge), 1)
        if(this.edges.length === 0){
            this.htmlItem.baseElement.classList.remove('has-edge')
        }
        this.updateAcceptsEdgeClass()
    }

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

        this.eventDispatcher = new EventDispatcher(this,this.htmlItem.getHtmlEl('Hitbox'))
        this.link(this.eventDispatcher.onDragStart,this.generateEdge)

        new MouseOverDetector(this,this.htmlItem.getHtmlEl('Hitbox'))

        // Bind attributes to UI

        this.displayLabel = true
        
        // Initializing classes like this prevents UI from glitching (hopefully)
        this.htmlItem.baseElement.classList.add('control-takes-label')
        this.htmlItem.baseElement.classList.add('has-edge')

        this.link(this.display_name.onSet,(label: string) => {
            this.htmlItem.getHtmlEl('label').innerText = label
            //if(this.node)
                //this.node.setMinWidth( this.htmlItem.getHtmlEl('label').offsetWidth + 18) 
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
        this.link(this.max_edges.onSet,this.updateAcceptsEdgeClass)
        if(this.is_input.getValue()) {
            this.link(this.getAttribute('control_takes_label').onSet,(takes_label: number) => {
                if(takes_label) {
                    this.htmlItem.baseElement.classList.add('control-takes-label')
                } else {
                    this.htmlItem.baseElement.classList.remove('control-takes-label')
                }
            })
            if(this.getAttribute('control_takes_label').getValue()) {
                this.htmlItem.baseElement.classList.add('control-takes-label')
            } else {
                this.htmlItem.baseElement.classList.remove('control-takes-label')
            }
        }else{
            this.htmlItem.baseElement.classList.remove('control-takes-label')
        }
        if(this.edges.length === 0){
            this.htmlItem.baseElement.classList.remove('has-edge')
        }
        this.eventDispatcher.isDraggable = (e:MouseEvent)=>!(this.node.isPreview ||
                    !this.acceptsEdge() ||
                    e.buttons !== 1)
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
        //this.node.setMinWidth( this.htmlItem.getHtmlEl('label').offsetWidth + 18)
        this.moved.invoke()
    }



    public acceptsEdge(delta:number=0): boolean {
        if(this.node!=null && this.node.isPreview) return false
        if(this.max_edges.getValue() > this.edges.length+delta) return true
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

    private generateEdge(e:MouseEvent): void {
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

    private updateAcceptsEdgeClass(): void {
        if(this.acceptsEdge()){
            this.htmlItem.getHtmlEl('Knob').classList.add('accepts-edge')
        }
        else{
            this.htmlItem.getHtmlEl('Knob').classList.remove('accepts-edge')
        }
    }
}