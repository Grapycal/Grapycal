import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic, ObjectTopic} from 'objectsync-client'
import { Port } from './port'
import { HtmlItem } from '../component/htmlItem'
import { CompSObject } from './compSObject'
import { soundManager } from '../app'
import { Vector2, as } from '../utils'
import { print } from '../devUtils'
import { Transform } from '../component/transform'
import { EventDispatcher } from '../component/eventDispatcher'
import { MouseOverDetector } from '../component/mouseOverDetector'
import { Editor } from './editor'
import { Selectable } from '../component/selectable'
import { Workspace } from './workspace'

enum EdgeState {
    Idle,
    DraggingTail,
    DraggingHead,
}

export class Edge extends CompSObject {
    tail: ObjectTopic<Port> = this.getAttribute('tail', ObjectTopic<Port>)
    head: ObjectTopic<Port> = this.getAttribute('head', ObjectTopic<Port>)

    editor: Editor
    htmlItem: HtmlItem
    eventDispatcher: EventDispatcher
    transform: Transform
    selectable: Selectable
    path: SVGPathElement
    path_hit_box: SVGPathElement
    svg: SVGSVGElement

    state: EdgeState = EdgeState.Idle

    template = `
    <div id="base" style="position:absolute;width:1px;height:1px">
        <svg class="edge" id="svg">
            <g>
                <path class="edge-path" id="path" d=""  fill="none"></path>
                <path class="edge-path-hit-box" id="path_hit_box" d=""  fill="none"></path>
            </g>
        </svg>
    </div>
    `
    base: HTMLDivElement

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        this.editor = this.parent as Editor

        this.updateSVG = this.updateSVG.bind(this)
        this.onDrag = this.onDrag.bind(this)
        this.onDragEndWhileCreating = this.onDragEndWhileCreating.bind(this)
        
        // setup components
        this.htmlItem = new HtmlItem(this)
        this.htmlItem.applyTemplate(this.template)

        this.eventDispatcher = new EventDispatcher(this, this.htmlItem.getEl('path_hit_box', SVGPathElement))

        this.transform = new Transform(this, this.htmlItem.getHtmlEl('base'))
        this.transform.pivot = Vector2.zero
        this.transform.translation = Vector2.zero

        
        this.path = this.htmlItem.getEl('path',SVGPathElement)
        this.path_hit_box = this.htmlItem.getEl('path_hit_box',SVGPathElement)
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
        
        this.selectable = new Selectable(this, Workspace.instance.selection)
        const onPortChanged = ((oldPort:Port,newPort:Port) =>{
            if(oldPort){
                oldPort.moved.remove(this.updateSVG)
                oldPort.edges.splice(oldPort.edges.indexOf(this),1)
            }
            if(newPort){
                this.updateSVG()
                
                newPort.moved.add(this.updateSVG)
                newPort.edges.push(this)
            }
        }).bind(this)

        // link attributes to UI
        onPortChanged(null,this.tail.getValue())
        onPortChanged(null,this.head.getValue())
        this.link(this.tail.onSet2,onPortChanged)
        this.link(this.head.onSet2,onPortChanged)

        if(this.hasTag('CreatingDragTail')) this.state = EdgeState.DraggingTail
        if(this.hasTag('CreatingDragHead')) this.state = EdgeState.DraggingHead
        if(this.hasTag('CreatingDragTail')||this.hasTag('CreatingDragHead')){
            this.link(this.eventDispatcher.onMoveGlobal,this.onDrag)
            this.link(this.eventDispatcher.onMouseUpGlobal,this.onDragEndWhileCreating)
        }else{
            
            this.link(this.eventDispatcher.onDragStart,this.onDragStart)
            this.link(this.eventDispatcher.onDrag,this.onDrag)
            this.link(this.eventDispatcher.onDragEnd,this.onDragEnd)
            this.link(this.eventDispatcher.onMouseOver,() => {
                this.svg.classList.add('hover')
            })
            this.link(this.eventDispatcher.onMouseLeave,() => {
                this.svg.classList.remove('hover')
            })
        }

        this.link(this.selectable.onSelected, () => {
            this.svg.classList.add('selected')
        })

        this.link(this.selectable.onDeselected, () => {
            this.svg.classList.remove('selected')
        })
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
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem) || this.editor.htmlItem) //>????????????
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
            let tail = this.tail.getValue()
            let head = this.head.getValue()
            as(this.parent,Editor).createEdge(tail.id,head.id)
            this.objectsync.clearPretendedChanges();
        }
    }


    // Graphical stuff
    private updateSVG() {
        setTimeout(() => {
            try{
                this.path.setAttribute('d', this.getSVGPath())
                this.path_hit_box.setAttribute('d', this.getSVGPath())
            }catch(e){}
        }, 0);
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