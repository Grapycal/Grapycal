import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic, ObjectTopic} from 'objectsync-client'
import { Port } from './port'
import { HtmlItem } from '../component/htmlItem'
import { CompSObject } from './compSObject'
import { editor } from '../app'
import { Vector2, as } from '../utils'
import { Null, print } from '../devUtils'
import { Transform } from '../component/transform'
import { EventDispatcher } from '../component/eventDispatcher'
import { MouseOverDetector } from '../component/mouseOverDetector'

enum EdgeState {
    Idle,
    DraggingTail,
    DraggingHead,
}

export class Edge extends CompSObject {
    tail: ObjectTopic<Port> = this.getAttribute('tail', ObjectTopic<Port>)
    head: ObjectTopic<Port> = this.getAttribute('head', ObjectTopic<Port>)

    htmlItem: HtmlItem
    eventDispatcher: EventDispatcher
    transform: Transform
    path: SVGPathElement
    svg: SVGSVGElement

    state: EdgeState = EdgeState.Idle

    template = `
    <div id="base">
        <svg class="Edge" id="svg">
            <g>
                <path id="path" d=""  fill="none"></path>
            </g>
        </svg>
    </div>
    `

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        this.updateSVG = this.updateSVG.bind(this)
        
        // setup components
        this.htmlItem = new HtmlItem(this)
        this.htmlItem.applyTemplate(this.template)

        this.eventDispatcher = new EventDispatcher(this, this.htmlItem.getEl('path', SVGPathElement))
        this.eventDispatcher.onDragStart.add(this.onDragStart.bind(this))
        this.eventDispatcher.onDrag.add(this.onDrag.bind(this))
        this.eventDispatcher.onDragEnd.add(this.onDragEnd.bind(this))

        this.transform = new Transform(this, this.htmlItem.getHtmlEl('base'))
        this.transform.pivot = Vector2.zero
        this.transform.translation = Vector2.zero
        
        // link attributes to UI
        this.tail.onSet2.add((oldPort: Port,port: Port) => {
            if(oldPort) oldPort.moved.remove(this.updateSVG)
            if(!port) return
            this.updateSVG();
            port.moved.add(this.updateSVG)
        })
        this.head.onSet2.add((oldPort: Port,port: Port) => {
            if(oldPort) oldPort.moved.remove(this.updateSVG)
            if(!port) return
            this.updateSVG();
            port.moved.add(this.updateSVG)
        })
        this.parent?.onAddChild.add(this.updateSVG)
        this.parent?.onRemoveChild.add(this.updateSVG)
        this.path = this.htmlItem.getEl('path',SVGPathElement)
        this.svg = this.htmlItem.getEl('svg', SVGSVGElement)
    }


    onDestroy(): void {
        if(this.tail.getValue()) {
            this.tail.getValue().moved.remove(this.updateSVG)
        }
        if(this.head.getValue()) {
            this.head.getValue().moved.remove(this.updateSVG)
        }
        this.parent?.onAddChild.remove(this.updateSVG)
        this.parent?.onRemoveChild.remove(this.updateSVG)
        super.onDestroy()
    }

    protected onParentChangedFrom(oldValue: SObject): void {
        super.onParentChangedFrom(oldValue)
        oldValue.onAddChild.remove(this.updateSVG)
        oldValue.onRemoveChild.remove(this.updateSVG)
    }

    protected onParentChangedTo(newValue: SObject): void {
        super.onParentChangedTo(newValue)
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem) || editor.htmlItem)
        newValue.onAddChild.add(this.updateSVG)
        newValue.onRemoveChild.add(this.updateSVG)
    }

    private onDragStart(event: MouseEvent, mousePos: Vector2) {
        let maxR = 200
        let distToTail = this.tail.getValue().getComponent(Transform).worldCenter.distanceTo(mousePos)
        let distToHead = this.head.getValue().getComponent(Transform).worldCenter.distanceTo(mousePos)
        if(distToTail > maxR && distToHead > maxR)return;
        if(distToTail < distToHead) {
            this.state = EdgeState.DraggingTail
        }
        else {
            this.state = EdgeState.DraggingHead
        }
    }

    private onDrag(event: MouseEvent, mousePos: Vector2) {
        for(let object of MouseOverDetector.allObjects){
            if(object instanceof Port){
                if(this.state == EdgeState.DraggingTail){
                    if(object != this.tail.getValue() && !object.is_input){
                        this.tail.set(object)
                    }
                }
                else if(this.state == EdgeState.DraggingHead){
                    if(object != this.head.getValue() && object.is_input){
                        this.head.set(object)
                    }
                }
            }
        }
        if(this.state == EdgeState.DraggingTail || this.state == EdgeState.DraggingHead) {
            this.updateSVG()
        }
    }

    private onDragEnd(event: MouseEvent, mousePos: Vector2) {
        if(this.state == EdgeState.DraggingTail && 
            (this.tail.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.tail.getValue().getComponent(Transform).worldCenter) > 22*this.transform.getAbsoluteScale().x))
            {
                this.objectsync.destroyObject(this.id);
                this.tail.set(Null());
            }
        else if(this.state == EdgeState.DraggingHead &&
            (this.head.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.head.getValue().getComponent(Transform).worldCenter) > 22*this.transform.getAbsoluteScale().x))
            {
                this.objectsync.destroyObject(this.id);
                this.head.set(Null());
            }
        this.state = EdgeState.Idle
        this.updateSVG()
    }


    // Graphical stuff
    private updateSVG() {
        print('updateSVG',this.tail.getValue(),this.head.getValue())
        this.path.setAttribute('d', this.getSVGPath())
        // update bounding box of svg
        let bbox = this.svg.getBBox()
        this.svg.setAttribute("width", Math.max(bbox.width,300).toString());
        this.svg.setAttribute("height", Math.max(bbox.height,300).toString());
    }
    private getSVGPath(): string {
        let tail: Vector2
        let head: Vector2
        let tail_orientation: number
        let head_orientation: number

        if(this.state == EdgeState.DraggingTail && 
            (this.tail.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.tail.getValue().getComponent(Transform).worldCenter) > 22*this.transform.getAbsoluteScale().x)) {
            tail = this.transform.worldToLocal(this.eventDispatcher.mousePos)
            head = this.transform.worldToLocal(this.head.getValue().getComponent(Transform).worldCenter)
            tail_orientation = Math.atan2(head.y - tail.y, head.x - tail.x)
            head_orientation = this.head.getValue().orientation 
        }
        else if(this.state == EdgeState.DraggingHead &&
            (this.head.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.head.getValue().getComponent(Transform).worldCenter) > 22*this.transform.getAbsoluteScale().x)) {
            tail = this.transform.worldToLocal(this.tail.getValue().getComponent(Transform).worldCenter)
            head = this.transform.worldToLocal(this.eventDispatcher.mousePos)
            tail_orientation = this.tail.getValue().orientation
            head_orientation = Math.atan2(tail.y - head.y, tail.x - head.x)
        }else {
            if(!this.tail.getValue() || !this.head.getValue()) return ''
            tail = this.transform.worldToLocal(this.tail.getValue().getComponent(Transform).worldCenter)
            head = this.transform.worldToLocal(this.head.getValue().getComponent(Transform).worldCenter)
            tail_orientation = this.tail.getValue().orientation
            head_orientation = this.head.getValue().orientation
        }

        let dx = head.x - tail.x
        let dy = head.y - tail.y
        let d = Math.sqrt(dx*dx + dy*dy)
        let r = Math.min(200, d/2)
        if(isNaN(r) || isNaN(tail_orientation) || isNaN(head_orientation)) return ''
        let path = `M ${tail.x} ${tail.y} C ${tail.x + Math.cos(tail_orientation)*r} ${tail.y + Math.sin(tail_orientation)*r},
        ${head.x + Math.cos(head_orientation)*r} ${head.y+ Math.sin(head_orientation)*r}, ${head.x} ${head.y}`

        return path
    }

}