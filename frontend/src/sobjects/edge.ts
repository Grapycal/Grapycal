import {ObjectSyncClient, SObject, StringTopic, ObjectTopic, IntTopic} from 'objectsync-client'
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
    labelTopic: StringTopic = this.getAttribute('label', StringTopic)
    data_ready: IntTopic = this.getAttribute('data_ready', IntTopic)

    editor: Editor
    htmlItem: HtmlItem
    eventDispatcher: EventDispatcher
    transform: Transform
    selectable: Selectable
    functionalSelectable: Selectable;
    path: SVGPathElement
    path_hit_box: SVGPathElement
    svg: SVGSVGElement
    label: HTMLDivElement

    state: EdgeState = EdgeState.Idle

    template = `
    <div id="base" style="position:absolute;width:1px;height:1px">
        <div class="edge-label" id="label"></div>
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

        this.label = this.htmlItem.getEl('label',HTMLDivElement)

        this.link2(this.htmlItem.baseElement,'mousedown', () => {
            soundManager.playClick() // why not working?
        })

    }

    protected onStart(): void {
        super.onStart()
        
        this.selectable = new Selectable(this, Workspace.instance.selection)
        this.functionalSelectable = new Selectable(this, Workspace.instance.functionalSelection)

        // link attributes to UI

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
        onPortChanged(null,this.tail.getValue())
        onPortChanged(null,this.head.getValue())
        this.link(this.tail.onSet2,onPortChanged)
        this.link(this.head.onSet2,onPortChanged)

        this.link(this.selectable.onSelected, () => {
            this.svg.classList.add('selected')
        })

        this.link(this.selectable.onDeselected, () => {
            this.svg.classList.remove('selected')
        })
        this.link(this.functionalSelectable.onSelected, () => {
            this.svg.classList.add('functional-selected')
        })
        this.link(this.functionalSelectable.onDeselected, () => {
            this.svg.classList.remove('functional-selected')
        })
        this.link(this.labelTopic.onSet, () => {
            this.label.innerText = this.labelTopic.getValue()
        })

        this.link(this.data_ready.onSet2, (_:number,data_ready: number) => {
            if(data_ready == 0)
                this.svg.classList.add('data-ready')
            else{
                this.svg.classList.add('data-ready')
                let tmp =  data_ready
                setTimeout(() => {
                    try{
                    if(tmp == this.data_ready.getValue())
                        this.svg.classList.remove('data-ready')
                    }catch{}
                }, 200); //delay of chatrooom sending buffer is 200ms
            }
        })
        if(this.data_ready.getValue() == 0) this.svg.classList.add('data-ready')

        this.updateSVG()
    }

    onDestroy(): void {
        if(this.tail.getValue()) {
            this.tail.getValue().moved.remove(this.updateSVG)
        }
        if(this.head.getValue()) {
            this.head.getValue().moved.remove(this.updateSVG)
        }
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
            (this.tail.getValue() == null || !MouseOverDetector.objectsUnderMouse.includes(this.tail.getValue())))
            {
                this.objectsync.clearPretendedChanges();
                this.objectsync.destroyObject(this.id);
            }
        else if(this.state == EdgeState.DraggingHead &&
            (this.head.getValue() == null || !MouseOverDetector.objectsUnderMouse.includes(this.head.getValue())))
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
            (this.tail.getValue() == null || !MouseOverDetector.objectsUnderMouse.includes(this.tail.getValue())))
            {
                this.objectsync.clearPretendedChanges();
            }
        else if(this.state == EdgeState.DraggingHead &&
            (this.head.getValue() == null || !MouseOverDetector.objectsUnderMouse.includes(this.head.getValue())))
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
        this._updateSVG()
        setTimeout(() => {
            try{
                this._updateSVG()
            }catch(e){}
        }, 0);
    }

    private _updateSVG() {
        let path = this.getSVGPath()
        if(path==null)return//no change
        this.path.setAttribute('d', path)
        this.path_hit_box.setAttribute('d', path)
        let worldCenter = new Vector2(
            (this.path.getBoundingClientRect().left + this.path.getBoundingClientRect().right)/2,
            (this.path.getBoundingClientRect().top + this.path.getBoundingClientRect().bottom)/2
        )
        let localCenter = this.transform.worldToLocal(worldCenter)
        this.label.style.left = localCenter.x + 'px'
        this.label.style.top = localCenter.y + 'px'
        this.label.style.width = this.pathResult.length + 'px'
        let angle = this.pathResult.tangent.angle()
        if (angle > Math.PI/2) angle -= Math.PI
        if (angle < -Math.PI/2) angle += Math.PI
        this.label.style.transform = `translate(-50%,-50%) rotate(${angle}rad) translate(0,50%)`
    }

    pathParam = {
        tail:new Vector2(NaN,NaN),
        head:new Vector2(NaN,NaN),
        tail_orientation:-1,
        head_orientation:-1
    }

    pathResult = {
        tangent:new Vector2(NaN,NaN),
        normal:new Vector2(NaN,NaN),
        length:NaN
    }

    private getSVGPath(): string {
        let tail: Vector2
        let head: Vector2
        let tail_orientation: number
        let head_orientation: number

        if(
            this.state == EdgeState.DraggingTail && 
            this.head.getValue() != null &&
            (this.tail.getValue() == null || !MouseOverDetector.objectsUnderMouse.includes(this.tail.getValue()))){
            tail = this.transform.worldToLocal(this.eventDispatcher.mousePos)
            head = this.transform.worldToLocal(this.head.getValue().getComponent(Transform).worldCenter)
            //tail_orientation = Math.atan2(head.y - tail.y, head.x - tail.x)
            tail_orientation = 0
            head_orientation = this.head.getValue().orientation 
        }
        else if(
            this.state == EdgeState.DraggingHead &&
            this.tail.getValue() != null &&
            (this.head.getValue() == null || !MouseOverDetector.objectsUnderMouse.includes(this.head.getValue()))) {
            tail = this.transform.worldToLocal(this.tail.getValue().getComponent(Transform).worldCenter)
            head = this.transform.worldToLocal(this.eventDispatcher.mousePos)
            tail_orientation = this.tail.getValue().orientation
            //head_orientation = Math.atan2(tail.y - head.y, tail.x - head.x)
            head_orientation = Math.PI
        }else {
            if(!this.tail.getValue() || !this.head.getValue()) {throw Error;return null}
            tail = this.transform.worldToLocal(this.tail.getValue().getComponent(Transform).worldCenter)
            head = this.transform.worldToLocal(this.head.getValue().getComponent(Transform).worldCenter)
            tail_orientation = this.tail.getValue().orientation
            head_orientation = this.head.getValue().orientation
        }

        if(tail.equals(this.pathParam.tail) && 
            head.equals(this.pathParam.head) && 
            tail_orientation == this.pathParam.tail_orientation &&
            head_orientation == this.pathParam.head_orientation
        )return null // no change

        this.pathParam = {tail,head,tail_orientation,head_orientation}

        let dx = head.x - tail.x
        let dy = head.y - tail.y
        let d = Math.sqrt(dx*dx + dy*dy)
        let r = Math.min(50, d/3)
        if(isNaN(r) || isNaN(tail_orientation) || isNaN(head_orientation)) throw new Error('NaN')
        let mp1 = new Vector2(tail.x + Math.cos(tail_orientation)*r, tail.y + Math.sin(tail_orientation)*r)
        let mp2 = new Vector2(head.x + Math.cos(head_orientation)*r, head.y + Math.sin(head_orientation)*r)
        let path = `M ${tail.x} ${tail.y} C ${mp1.x} ${mp1.y} ${mp2.x} ${mp2.y} ${head.x} ${head.y}`

        this.pathResult = {
            tangent:mp2.add(head).sub(mp1.add(tail)).normalized(),
            normal:mp2.add(head).sub(mp1.add(tail)).normalized().rotate(Math.PI/2),
            length:d
        }

        // let dx = head.x - tail.x
        // let dy = head.y - tail.y
        // let d = Math.sqrt(dx*dx + dy*dy)
        // let r = Math.min(50, d/2)
        // if(isNaN(r) || isNaN(tail_orientation) || isNaN(head_orientation)) throw new Error('NaN')
        // let mp1 = new Vector2(tail.x + Math.cos(tail_orientation)*r, tail.y + Math.sin(tail_orientation)*r)
        // let mp2 = new Vector2(head.x + Math.cos(head_orientation)*r, head.y + Math.sin(head_orientation)*r)
        // let direction = mp2.sub(mp1).normalize()
        // r = Math.min(r,mp1.sub(mp2).length/2)
        // let arcp1 = mp1.add(direction.mulScalar(r))
        // let arcp2 = mp2.sub(direction.mulScalar(r))
        // let a = arcp1.sub(tail).length/2
        // let radius = a*r*1/(Math.sqrt(r**2-a**2))
        // if(isNaN(radius) || direction.dot(head.sub(tail))<0) radius = 0
        // print(tail_orientation,direction.angle())
        // let path = `M ${tail.x} ${tail.y} A ${radius} ${radius} 0 0 ${direction.rotate(tail_orientation).angle()>0 ? 1 : 0} ${arcp1.x} ${arcp1.y} L ${arcp2.x} ${arcp2.y} A ${radius} ${radius} 0 0 ${direction.rotate(head_orientation).angle()>0 ? 1 : 0} ${head.x} ${head.y}`
        // let tangent = mp2.add(head).sub(mp1.add(tail)).normalize()
        // this.pathResult = {
        //     tangent:tangent,
        //     normal:tangent.rotate(Math.PI/2),
        //     length:d
        // }
        


        // let delta = head.sub(tail)
        // let tangent1 = Vector2.fromPolar(1,tail_orientation)
        // let tangent2 = Vector2.fromPolar(1,head_orientation)
        // let normal1 = tangent1.rotate(Math.PI/2)
        // let normal2 = tangent2.rotate(Math.PI/2)

        // let maxR = Math.min(
        //     delta.length/4/Math.sin(Vector2.angle(normal1,delta)),
        //     delta.length/4/Math.sin(Vector2.angle(normal2,delta))
        // )

        // const r = Math.min(20, Math.abs(maxR))

        // const flip = (Vector2.angle(tangent1,head.sub(tail))>0 ? 1 : -1)

        // let c1 = tail.add(normal1.mulScalar(r*flip))
        // let c2 = head.add(normal2.mulScalar(r*flip))

        // let m = c1.add(c2).mulScalar(0.5)
        // let centerToM = c1.sub(m)
        // let d = centerToM.length
        // let commonTangentDir= centerToM.rotate(Math.asin(r/d)*flip).normalized()
        
        // let ct1 = m.add(commonTangentDir.mulScalar((d*d-r*r)**0.5))
        // let ct2 = m.sub(commonTangentDir.mulScalar((d*d-r*r)**0.5))
        // let path = `M ${tail.x} ${tail.y} A ${r} ${r} 0 0 ${flip==1?1:0} ${ct1.x} ${ct1.y} L ${ct2.x} ${ct2.y} A ${r} ${r} 0 0 ${flip==1?0:1} ${head.x} ${head.y}`

        // let tangent = commonTangentDir
        // this.pathResult = {
        //     tangent:tangent,
        //     normal:tangent.rotate(Math.PI/2),
        //     length:head.sub(tail).length
        // }
        
        return path
    }
}