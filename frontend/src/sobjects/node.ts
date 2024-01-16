import {ObjectSyncClient, SObject, StringTopic, FloatTopic, ListTopic, ObjListTopic, Action, IntTopic, SetTopic} from 'objectsync-client'
import { fetchWithCache, soundManager } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Space, Transform } from '../component/transform'
import { CompSObject } from './compSObject'
import { print } from '../devUtils'
import { Port } from './port'
import { bloomDiv as bloomDiv, glowText } from '../ui_utils/effects'
import { Vector2, as } from '../utils'
import { EventDispatcher, GlobalEventDispatcher } from '../component/eventDispatcher'
import { MouseOverDetector } from '../component/mouseOverDetector'
import { Sidebar } from './sidebar'
import { Editor } from './editor'
import { Selectable } from '../component/selectable'
import { Workspace } from './workspace'
import { ErrorPopup } from '../ui_utils/errorPopup'
import { ExposedAttributeInfo } from '../inspector/inspector'
import { ControlHost } from './controls/controlHost'
 
export class Node extends CompSObject implements ControlHost {
    errorPopup: ErrorPopup;
    public static getCssClassesFromCategory(category: string): string[]{
        let classes = []
        let str = 'cate'
        for(let subCat of category.split('/')){
            if(subCat == '') continue
            str += '-'+subCat.replace(/[^a-zA-Z0-9]/g,'-')
            classes.push(str)
        }
        return classes
    }

    shape: StringTopic = this.getAttribute('shape', StringTopic) // normal, simple, round
    label: StringTopic = this.getAttribute('label', StringTopic)
    label_offset: FloatTopic = this.getAttribute('label_offset', FloatTopic)
    translation: StringTopic = this.getAttribute('translation', StringTopic)
    category: StringTopic = this.getAttribute('category', StringTopic)
    in_ports: ObjListTopic<Port> = this.getAttribute('in_ports', ObjListTopic<Port>)
    out_ports: ObjListTopic<Port> = this.getAttribute('out_ports', ObjListTopic<Port>)
    exposed_attributes: ListTopic<ExposedAttributeInfo> = this.getAttribute('exposed_attributes', ListTopic<ExposedAttributeInfo>)
    type_topic: StringTopic = this.getAttribute('type', StringTopic)
    output: ListTopic<[string,string]> = this.getAttribute('output', ListTopic<[string,string]>)
    running: IntTopic = this.getAttribute('running', IntTopic)
    css_classes: SetTopic = this.getAttribute('css_classes', SetTopic)
    icon_path: StringTopic = this.getAttribute('icon_path', StringTopic)
    
    private _isPreview: boolean
    get isPreview(): boolean {
        return this._isPreview
    }


    editor: Editor;
    ancestorNode: Node = this;
    htmlItem: HtmlItem = new HtmlItem(this);
    eventDispatcher: EventDispatcher = new EventDispatcher(this)
    transform: Transform = null
    selectable: Selectable;
    functionalSelectable: Selectable;
    mouseOverDetector: MouseOverDetector

    dragEndCorrection: Vector2 = new Vector2(0,0)

    private draggingTargetPos: Vector2 = new Vector2(0,0)
    
    public moved: Action<[]> = new Action();

    protected readonly templates: {[key: string]: string} = {
    normal: 
        `<div class="node normal-node" id="slot_default">
            
            
            <div class="node-selection"></div>
            <div class="node-label full-width">
                <div id="label"></div>
            </div>

            <div class="node-border-container">
                <div class="node-border" id="node-border">
                </div>
            </div>
            <div class=" flex-vert space-between main-section">
                <div id="slot_input_port" class=" flex-vert space-evenly slot-input-port"></div>
                <div id="slot_control" class="slot-control flex-vert space-between"></div>
                <div id="slot_output_port" class=" flex-vert space-evenly slot-output-port"></div>
            </div>
        </div>`,
    simple:
        `<div class="node simple-node" id="slot_default">
            <div class="node-border-container">
                <div class="node-border"id="node-border">
                </div>
            </div>
            <div class="node-selection"></div>
            
            <div class="flex-horiz stretch-align space-between">
                <div id="slot_input_port" class=" flex-vert justify-start slot-input-port"></div>

                <div class="full-width flex-vert space-evenly">
                    <div class="node-label full-width flex-horiz">
                        <div id="label"></div>
                    </div>
                    <div id="slot_control"  class="slot-control main-section"></div>
                </div>

                <div id="slot_output_port" class=" flex-vert justify-start slot-output-port"></div>
            </div>
        </div>`,
    round:
        `<div class="node round-node " id="slot_default">
            <div class="node-border-container">
                <div class="node-border"id="node-border">
                </div>
            </div>
            <div class="node-selection"></div>
            <div class="flex-horiz node-content">
                <div id="slot_input_port" class=" flex-vert space-evenly slot-input-port"></div>
                <div class="full-width flex-vert space-evenly node-label"> 
                    <div id="label" class="center-align"></div>
                </div>
                <div id="slot_control" style="display:none"></div>
                
                <div id="slot_output_port" class=" flex-vert space-evenly slot-output-port"></div>
            </div>
        </div>`,
    }

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        this.mouseOverDetector = new MouseOverDetector(this)

        this.link(this.eventDispatcher.onDoubleClick, () => {
            this.emit('double_click')
        })
        this.errorPopup = new ErrorPopup(this)

    }

    protected onStart(): void {
        super.onStart()
        this.selectable = new Selectable(this, Workspace.instance.selection)
        this.functionalSelectable = new Selectable(this, Workspace.instance.functionalSelection)
        this._isPreview = this.parent instanceof Sidebar

        this.editor = this.isPreview? null : this.parent as Editor
        
        // Bind attributes to UI

        this.shape.onSet.add(this.reshape.bind(this))

        this.link(this.label.onSet, (label: string) => {
            this.htmlItem.getHtmlEl('label').innerText = label
        })

        this.link(this.label_offset.onSet, (offset: number) => {
            let label_el = this.htmlItem.getHtmlEl('label')
            label_el.style.marginTop = offset + 'em'
        })

        for(let className of Node.getCssClassesFromCategory(this.category.getValue())){
            this.htmlItem.baseElement.classList.add(className)
        }

        this.link(this.category.onSet2, (oldCategory: string, newCategory: string) => {
            if(this.parent instanceof Sidebar){
                if(this.parent.hasItem(this.htmlItem))
                    this.parent.removeItem(this.htmlItem, oldCategory)
                this.parent.addItem(this.htmlItem, newCategory)
            }
            for(let className of Node.getCssClassesFromCategory(oldCategory)){
                this.htmlItem.baseElement.classList.remove(className)
            }
            for(let className of Node.getCssClassesFromCategory(newCategory)){
                this.htmlItem.baseElement.classList.add(className)
            }
        })

        this.link(this.running.onSet2, (_:number,running: number) => {
            if(running == 0)
                this.htmlItem.baseElement.classList.add('running')
            else{
                this.htmlItem.baseElement.classList.add('running')
                let tmp =  running
                setTimeout(() => {
                    try{
                    if( tmp == this.running.getValue())
                        this.htmlItem.baseElement.classList.remove('running')
                    }catch(e){}
                }, 200); //delay of chatrooom sending buffer is 200ms
            }
        })

        if (this.running.getValue() == 0) this.htmlItem.baseElement.classList.add('running')

        this.link(this.output.onInsert, ([type, value]: [string, string]) => {
                if(type == 'error'){
                this.objectsync.doAfterTransitionFinish(() => { 
                    // Sometimes onInsert is invoked by reverted preview change.
                    if(this.output.getValue().length == 0) return
                    this.errorPopup.set('Error',value)
                    this.errorPopup.show()
                    })
                }
        })


        // Configure components
        
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem))

        // Before setting up the transform, we need to add classes to the element then call updateUI so the shape is correct
        
        this.link(this.css_classes.onAppend, (className: string) => {
            this.htmlItem.baseElement.classList.add(className)
        })
        
        this.link(this.css_classes.onRemove, (className: string) => {
            this.htmlItem.baseElement.classList.remove(className)
        })
        
        for(let className of this.css_classes.getValue()){
            this.htmlItem.baseElement.classList.add(className)
        }
        
        // Setup the transform

        if (!this.isPreview){
            this.transform = new Transform(this,null,true)
            this.transform.updateUI()
            this.transform.pivot = new Vector2(0,0)
        
            this.translation.onSet.add((translation: string) => {
                if(!this.eventDispatcher.isDragging){ // prevent the node from jumping when dragging
                    let v = Vector2.fromString(translation);
                    if(!Number.isNaN(v.x) && !Number.isNaN(v.y))
                        this.transform.translation=Vector2.fromString(translation)
                }
            })

            this.link(this.eventDispatcher.onMouseDown, (e: MouseEvent) => {
                // pass the event to the editor to box select
                if(e.ctrlKey){
                    this.eventDispatcher.forwardEvent()
                    return
                }
            })

            this.eventDispatcher.onDragStart.add((e: MouseEvent,pos: Vector2) => {
                this.draggingTargetPos = this.transform.translation
                this.htmlItem.baseElement.classList.add('dragging')
            })

            this.eventDispatcher.onDrag.add((e: MouseEvent,newPos: Vector2,oldPos: Vector2) => {
                // pass the event to the editor to box select
                if(e.ctrlKey){
                    this.eventDispatcher.forwardEvent()
                    return
                }
                if(!this.selectable.selectionManager.enabled && !this.selectable.selected) return;
                if(!this.selectable.selected) this.selectable.click()

                let delta = this.transform.worldToLocalDisplacement(newPos.sub(oldPos))
                let snappedDelta = delta
                if(!GlobalEventDispatcher.instance.isKeyDown('Alt')){
                    this.draggingTargetPos = this.draggingTargetPos.add(delta)
                    const snap = 17
                    let snapped = new Vector2(
                        Math.round(this.draggingTargetPos.x/snap)*snap,
                        Math.round(this.draggingTargetPos.y/snap)*snap
                    )
                    const delta2 = snapped.sub(this.draggingTargetPos)
                    this.dragEndCorrection = delta2.mulScalar(0.1)
                    snapped = snapped.sub(delta2.mulScalar(0.1))
                    snappedDelta = snapped.sub(this.transform.translation)
                }

                for(let selectable of this.selectable.selectedObjects){
                    if(selectable.object instanceof Node){
                        let node = selectable.object
                        node.transform.translate(snappedDelta,Space.Local)
                        node.htmlItem.moveToFront()
                    }
                }
            })
            this.eventDispatcher.onDragEnd.add((e: Event,pos: Vector2) => {
                this.objectsync.record(() => {
                    for(let selectable of this.selectable.selectedObjects){
                        if(selectable.object instanceof Node){
                            let node = selectable.object
                            node.transform.translate(this.dragEndCorrection,Space.Local)
                            node.translation.set(node.transform.translation.toString())
                        }
                    }
                })
                this.htmlItem.baseElement.classList.remove('dragging')
            })
        }

        if(this.isPreview){
            this.link(this.eventDispatcher.onDragStart, () => {
                //create a new node
                this.emit('spawn',{client_id:this.objectsync.clientId}) 
            })
        }
        
        this.link(this.selectable.onSelected, () => {
            this.htmlItem.baseElement.classList.add('selected')
        })

        this.link(this.selectable.onDeselected, () => {
            this.htmlItem.baseElement.classList.remove('selected')
        })  

        this.link(this.functionalSelectable.onSelected, () => {
            this.htmlItem.baseElement.classList.add('functional-selected')
        })

        this.link(this.functionalSelectable.onDeselected, () => {
            this.htmlItem.baseElement.classList.remove('functional-selected')
        })

        if(this.hasTag(`spawned_by_${this.objectsync.clientId}`))
        {
            this.removeTag(`spawned_by_${this.objectsync.clientId}`)
            this.selectable.click()
            let pivot = this.transform.pivot
            this.transform.globalPosition = this.eventDispatcher.mousePos.add(pivot.mul(this.transform.size)).add(this.transform.size.mulScalar(-0.5))
            this.eventDispatcher.fakeOnMouseDown() //fake a mouse down to start dragging
        }

        if(this.hasTag(`pasted_by_${this.objectsync.clientId}`))
        {
            this.removeTag(`pasted_by_${this.objectsync.clientId}`)
            this.selectable.click()
        }

        if(this.isPreview){
            this.selectable.enabled = false
            this.functionalSelectable.enabled = false
        }

        this.link(this.eventDispatcher.onMouseOver, () => {
            this.htmlItem.baseElement.classList.add('hover')
        })

        this.link(this.eventDispatcher.onMouseLeave, () => {
            this.htmlItem.baseElement.classList.remove('hover')
        })

        this.link(this.onAddChild,this.moved.invoke)
        this.link(this.onRemoveChild,this.moved.invoke)
        if(!this.isPreview){
            this.link(this.transform.onChange,this.moved.invoke)
            this.transform.updateUI() // This line is necessary to make edges spawning in this frame to be connected to the node
        }
        //set background image
        if(this.icon_path.getValue() != ''){
            this.setIcon(this.icon_path.getValue())
        }
        // setTimeout(() => {
        //     let border = this.htmlItem.getHtmlEl('node-border')
        //     bloomDiv(border,this.htmlItem.baseElement as HTMLElement)

        // }, 0);
    }

    setIcon(path: string){
        fetchWithCache('svg/list.txt')
        .then(list => {
            if(list.replaceAll('\r','').split('\n').indexOf(path) != -1){
                this.setIconFromSvg(`svg/${path}.svg`)
            }
        })
    }

    setIconFromSvg(path: string){
        const base = (this.htmlItem.getElByClass('node-label') as HTMLDivElement)
        // load svg from url
        // the reason not using img tag is because its tint color cannot be changed by css
        fetchWithCache(path)
        .then(svg => {
            let t = document.createElement('template')
            t.innerHTML = svg
            let svgEl = null;
            for(let child of t.content.childNodes){
                if(child instanceof SVGElement){
                    svgEl = child
                    break
                }
            }
            if(svgEl == null) return
            base.prepend(svgEl)
            for(let dec of svgEl.querySelectorAll('path,rect,g')){
                (dec as HTMLElement).style.fill = ''
                dec.setAttribute('fill','')
            }
            svgEl.classList.add('node-icon')
            this.moved.invoke()
        })   
    }

    onParentChangedTo(newParent: SObject): void {
        super.onParentChangedTo(newParent)
        if(newParent instanceof Sidebar){
            newParent.addItem(this.htmlItem, this.category.getValue())
            if(!this.isPreview)
                this.transform.enabled = false
        }
        else{
            this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem))
            this.errorPopup.htmlItem.setParent(this.htmlItem.parent)
        }
        if(newParent instanceof Node){
            as(this.htmlItem.baseElement,HTMLDivElement).style.borderColor = 'transparent'
            if(!this.isPreview)
                this.transform.enabled = false
        }
    }

    reshape(shape: string) {
        this.htmlItem.applyTemplate(this.templates[shape])
        this.eventDispatcher.setEventElement(as(this.htmlItem.baseElement, HTMLElement))
        this.mouseOverDetector.eventElement = this.htmlItem.baseElement
        
        this.link2(this.htmlItem.baseElement,'mousedown', () => {
            soundManager.playClick()
        })
        
        let label_el = this.htmlItem.getHtmlEl('label')
        label_el.style.marginTop = this.label_offset.getValue() + 'em'

        if(this._isPreview){
            this.htmlItem.baseElement.classList.add('node-preview')
            const node_types_topic = Workspace.instance.nodeTypesTopic
            let nodeTypeDescription = node_types_topic.getValue().get(this.type_topic.getValue()).description
            this.htmlItem.baseElement.setAttribute('title', nodeTypeDescription)

        }

        if(shape == 'round'){
            this.htmlItem.baseElement.classList.add('round-node');
            (this.htmlItem.baseElement as HTMLElement).style.minWidth = 'unset'
        }else{
            (this.htmlItem.baseElement as HTMLElement).style.minWidth = this.minWidth + 'px'
        }
    }

    private minWidth: number = 0;

    public setMinWidth(width: number): void {
        if(width < this.minWidth) return
        this.minWidth = width;
        if(this.shape.getValue() != 'round')
            (this.htmlItem.baseElement as HTMLElement).style.minWidth = width + 'px'
    }

    public onDestroy(): void {
        super.onDestroy()
        if(this.parent instanceof Sidebar){
            this.parent.removeItem(this.htmlItem, this.category.getValue())
        }
        this.errorPopup.destroy()
    }
}