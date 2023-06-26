import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic, ObjectTopic} from 'objectsync-client'
import { Port } from './port'
import { HtmlItem } from '../component/htmlItem'
import { CompSObject } from './compSObject'
import { editor, soundManager } from '../app'
import { Vector2, as } from '../utils'
import { print } from '../devUtils'
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
    <div id="base" style="position:absolute;width:1px;height:1px">
        <svg class="edge" id="svg">
            <g>
                <path id="path" d=""  fill="none"></path>
            </g>
        </svg>
    </div>
    `
    base: HTMLDivElement

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        this.updateSVG = this.updateSVG.bind(this)
        this.onDrag = this.onDrag.bind(this)
        this.onDragEndWhileCreating = this.onDragEndWhileCreating.bind(this)
        
        // setup components
        this.htmlItem = new HtmlItem(this)
        this.htmlItem.applyTemplate(this.template)

        this.eventDispatcher = new EventDispatcher(this, this.htmlItem.getEl('path', SVGPathElement))
        this.link(this.eventDispatcher.onDragStart,this.onDragStart)
        this.link(this.eventDispatcher.onDrag,this.onDrag)
        this.link(this.eventDispatcher.onDragEnd,this.onDragEnd)

        this.transform = new Transform(this, this.htmlItem.getHtmlEl('base'))
        this.transform.pivot = Vector2.zero
        this.transform.translation = Vector2.zero
        
        this.path = this.htmlItem.getEl('path',SVGPathElement)
        this.base = this.htmlItem.getEl('base',HTMLDivElement)
        this.svg = this.htmlItem.getEl('svg', SVGSVGElement)

        this.svg.style.width = "auto"
        this.svg.style.height = "auto"
        this.base.style.width = "1px"
        this.base.style.height = "1px"
        this.svg.style.position = 'absolute'

        this.link2(this.htmlItem.baseElement,'mousedown', () => {
            soundManager.playClick() // why not working?
        })

    }

    protected onStart(): void {
        super.onStart()
        // link attributes to UI
        this.link(this.tail.onSet2,(oldPort: Port,_) => {
            if(!oldPort) return
            oldPort.moved.remove(this.updateSVG)
            oldPort.edges.splice(oldPort.edges.indexOf(this),1) // JS bad
        })
        this.link(this.tail.onSet,(newPort: Port) =>{
            if(!newPort) return
            setTimeout(() => { // wait for next frame so the port is positioned correctly
                try{ // sometimes the edge is destroyed before this is called
                    this.updateSVG();
                }catch(e){}
            }, 0);
            newPort.moved.add(this.updateSVG)
            newPort.edges.push(this)
        })
        this.link(this.head.onSet2,(oldPort: Port,_) => {
            if(!oldPort) return
            oldPort.moved.remove(this.updateSVG)
            oldPort.edges.splice(oldPort.edges.indexOf(this),1)
        })
        this.link(this.head.onSet,(newPort: Port) =>{
            if(!newPort) return
            setTimeout(() => {
                try{
                    this.updateSVG();
                }catch(e){}
            }, 0);
            newPort.moved.add(this.updateSVG)
            newPort.edges.push(this)
        })

        if(this.hasTag('CreatingDragTail')) this.state = EdgeState.DraggingTail
        if(this.hasTag('CreatingDragHead')) this.state = EdgeState.DraggingHead
        if(this.hasTag('CreatingDragTail')||this.hasTag('CreatingDragHead')){
            this.link(this.eventDispatcher.onMove,this.onDrag)
            this.link(this.eventDispatcher.onMouseUp,this.onDragEndWhileCreating)
        }
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
        this.head.getValue()?.edges.splice(this.head.getValue()?.edges.indexOf(this),1)
        this.tail.getValue()?.edges.splice(this.tail.getValue()?.edges.indexOf(this),1)
        super.onDestroy()
    }
    
    protected onParentChangedTo(newValue: SObject): void {
        super.onParentChangedTo(newValue)
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem) || editor.htmlItem)
    }

    private onDragStart(event: MouseEvent, mousePos: Vector2) {
        let maxR = 200
        let distToTail = this.tail.getValue().getComponent(Transform).worldCenter.distanceTo(mousePos)
        let distToHead = this.head.getValue().getComponent(Transform).worldCenter.distanceTo(mousePos)
        //if(distToTail > maxR && distToHead > maxR)return;
        if(distToTail < distToHead) {
            this.state = EdgeState.DraggingTail
        }
        else {
            this.state = EdgeState.DraggingHead
        }
    }

    private onDrag(event: MouseEvent, mousePos: Vector2) {
        for(let object of MouseOverDetector.objectsUnderMouse){
            if(object instanceof Port){
                let port = object
                if(this.state == EdgeState.DraggingTail){
                    if(object != this.tail.getValue() && !port.is_input.getValue() && port.acceptsEdge()){
                        this.objectsync.record(() => {
                            this.tail.set(port)
                        },true)
                        break;
                    }
                }
                else if(this.state == EdgeState.DraggingHead){
                    if(port != this.head.getValue() && port.is_input.getValue() && port.acceptsEdge()){
                        this.objectsync.record(() => {
                            this.head.set(port)
                        },true)
                        break;
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
            (this.tail.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.tail.getValue().getComponent(Transform).worldCenter) > 15*this.transform.getAbsoluteScale().x))
            {
                this.objectsync.clearPretendedChanges();
                this.objectsync.destroyObject(this.id);
            }
        else if(this.state == EdgeState.DraggingHead &&
            (this.head.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.head.getValue().getComponent(Transform).worldCenter) > 15*this.transform.getAbsoluteScale().x))
            {
                this.objectsync.clearPretendedChanges();
                this.objectsync.destroyObject(this.id);
            }
        else {
            // make the change of port permanent
            if (this.state == EdgeState.DraggingTail) {
                let newTail = this.tail.getValue()
                this.objectsync.clearPretendedChanges();
                this.tail.set(newTail)
                this.updateSVG()
            }
            else if (this.state == EdgeState.DraggingHead) {
                let newHead = this.head.getValue()
                this.objectsync.clearPretendedChanges();
                this.head.set(newHead)
                this.updateSVG()
            }
        }
        this.state = EdgeState.Idle
    }

    private onDragEndWhileCreating(){

        if(this.state == EdgeState.DraggingTail && 
            (this.tail.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.tail.getValue().getComponent(Transform).worldCenter) > 15*this.transform.getAbsoluteScale().x))
            {
                this.objectsync.clearPretendedChanges();
            }
        else if(this.state == EdgeState.DraggingHead &&
            (this.head.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.head.getValue().getComponent(Transform).worldCenter) > 15*this.transform.getAbsoluteScale().x))
            {
                this.objectsync.clearPretendedChanges();
            }
        else {
            // make the change of port permanent
            if (this.state == EdgeState.DraggingTail) {
                let tail = this.tail.getValue()
                let head = this.head.getValue()
                let parentID = this.parent.id
                this.objectsync.clearPretendedChanges();
                this.objectsync.record(() => {
                    let newEdge = as(this.objectsync.createObject('Edge',parentID),Edge )
                    newEdge.tail.set(tail)
                    newEdge.head.set(head)
                })
            }
            else if (this.state == EdgeState.DraggingHead) {
                let tail = this.tail.getValue()
                let head = this.head.getValue()
                let parentID = this.parent.id
                this.objectsync.clearPretendedChanges();
                this.objectsync.record(() => {
                    let newEdge = as(this.objectsync.createObject('Edge',parentID),Edge)
                    newEdge.tail.set(tail)
                    newEdge.head.set(head)
                })
            }
        }
    }


    // Graphical stuff
    private updateSVG() {
        this.path.setAttribute('d', this.getSVGPath())
    }
    private getSVGPath(): string {
        let tail: Vector2
        let head: Vector2
        let tail_orientation: number
        let head_orientation: number

        if(
            this.state == EdgeState.DraggingTail && 
            this.head.getValue() != null &&
            (this.tail.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.tail.getValue().getComponent(Transform).worldCenter) > 15*this.transform.getAbsoluteScale().x)) {
            tail = this.transform.worldToLocal(this.eventDispatcher.mousePos)
            head = this.transform.worldToLocal(this.head.getValue().getComponent(Transform).worldCenter)
            //tail_orientation = Math.atan2(head.y - tail.y, head.x - tail.x)
            tail_orientation = 0
            head_orientation = this.head.getValue().orientation 
        }
        else if(
            this.state == EdgeState.DraggingHead &&
            this.tail.getValue() != null &&
            (this.head.getValue() == null || this.eventDispatcher.mousePos.distanceTo(this.head.getValue().getComponent(Transform).worldCenter) > 15*this.transform.getAbsoluteScale().x)) {
            tail = this.transform.worldToLocal(this.tail.getValue().getComponent(Transform).worldCenter)
            head = this.transform.worldToLocal(this.eventDispatcher.mousePos)
            tail_orientation = this.tail.getValue().orientation
            //head_orientation = Math.atan2(tail.y - head.y, tail.x - head.x)
            head_orientation = Math.PI
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
        let r = Math.min(50, d/3)
        if(isNaN(r) || isNaN(tail_orientation) || isNaN(head_orientation)) return ''
        let path = `M ${tail.x} ${tail.y} C ${tail.x + Math.cos(tail_orientation)*r} ${tail.y + Math.sin(tail_orientation)*r},
        ${head.x + Math.cos(head_orientation)*r} ${head.y+ Math.sin(head_orientation)*r}, ${head.x} ${head.y}`

        return path
    }
}