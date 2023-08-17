import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic, Action} from 'objectsync-client'
import { soundManager } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'
import { print } from '../devUtils'
import { Port } from './port'
import { glowDiv as glowDiv, glowText } from '../ui_utils/effects'
import { Vector2, as } from '../utils'
import { EventDispatcher } from '../component/eventDispatcher'
import { MouseOverDetector } from '../component/mouseOverDetector'
import { Sidebar } from './sidebar'
import { Editor } from './editor'
import { Selectable } from '../component/selectable'
import { Workspace } from './workspace'

export class ExposedAttributeInfo
{
    name:string
    display_name:string
    editor_args:any
}

export class Node extends CompSObject {

    public static getCssClassesFromCategory(category: string): string[]{
        let classes = []
        let str = 'cate'
        for(let subCat of category.split('/')){
            if(subCat == '') continue
            str += '-'+subCat
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

    private _isPreview: boolean
    get isPreview(): boolean {
        return this._isPreview
    }


    editor: Editor;
    htmlItem: HtmlItem = new HtmlItem(this);
    eventDispatcher: EventDispatcher = new EventDispatcher(this)
    transform: Transform = new Transform(this);
    selectable: Selectable;
    mouseOverDetector: MouseOverDetector
    
    public moved: Action<[]> = new Action();

    protected readonly templates: {[key: string]: string} = {
    normal: 
        `<div class="node normal-node">
            
            <div class="node-border-container">
                <div class="node-border">
                </div>
            </div>
            
            <div class="node-overlay"></div>
            <div class="node-content flex-vert space-between">
                <div id="label" class="node-label full-width"></div>
                <div class="flex-horiz space-between full-width">
                    <div id="slot_input_port" class="no-width flex-vert space-evenly center slot-input-port"></div>
                    <div id="slot_output_port" class="no-width flex-vert space-evenly center slot-output-port"></div>
                </div>
                <div id="slot_control" class="slot-control flex-vert space-between"> </div>
            </div>
        </div>`,
    simple:
        `<div class="node simple-node node-content">
            <div class="node-border-container">
                <div class="node-border">
                </div>
            </div>
            <div class="node-overlay"></div>
            <div id="label" class="node-label"></div>
            <div class=" flex-horiz space-between">
                <div id="slot_input_port" class="no-width flex-vert space-evenly slot-input-port"></div>
                <div id="slot_control"  class="slot-control"> </div>

                <div id="slot_output_port" class="no-width flex-vert space-evenly slot-output-port"></div>
            </div>
        </div>`,
    round:
        `<div class="node round-node flex-horiz space-between" >
            <div class="node-overlay"></div>
            <div id="slot_input_port" class="no-width flex-vert space-evenly slot-input-port"></div>
            <div class="full-width flex-vert space-evenly"> 
                <div id="label" class="center-align"></div>
            </div>
            <div id="slot_control" style="display:none"></div>
            
            <div id="slot_output_port" class="no-width flex-vert space-evenly slot-output-port"></div>
        </div>`,
    }

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        this.mouseOverDetector = new MouseOverDetector(this)

        this.link(this.eventDispatcher.onDoubleClick, () => {
            this.emit('double_click')
        })
    }

    protected onStart(): void {
        super.onStart()
        this.selectable = new Selectable(this, Workspace.instance.selection)
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

        // Configure components
        
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem))

        if(!this._isPreview){
            const [x, y] = this.translation.getValue().split(',').map(parseFloat)
            this.transform.translation=new Vector2(x, y)
            this.transform.draggable = true
            this.translation.onSet.add((translation: string) => {
                if(!this.eventDispatcher.isDragging){ // prevent the node from jumping when dragging
                    this.transform.translation=Vector2.fromString(translation)
                }
            })
            this.transform.translationChanged.add((x: number, y: number) => {
                this.translation.set(`${x},${y}`)
                this.htmlItem.moveToFront()
            })
            this.transform.dragged.add((delta:Vector2) => {
                if(!this.selectable.selected) this.selectable.click()
                this.objectsync.record(() => {
                    for(let selectable of this.selectable.selectedObjects){
                        if(selectable.object instanceof Node && selectable.object != this){
                            let node = selectable.object
                            node.transform.translate(delta)
                        }
                    }
                })
            })
        }

        if(this.isPreview){
            this.link(this.eventDispatcher.onDragStart, () => {
                //create a new node
                this.emit('spawn',{client_id:this.objectsync.clientId,translation:`${this.eventDispatcher.mousePos.x},${this.eventDispatcher.mousePos.y}`})
            })
        }
        
        this.link(this.selectable.onSelected, () => {
            this.htmlItem.baseElement.classList.add('selected')
        })

        this.link(this.selectable.onDeselected, () => {
            this.htmlItem.baseElement.classList.remove('selected')
        })  

        if(this.hasTag(`spawned_by_${this.objectsync.clientId}`))
        {
            this.removeTag(`spawned_by_${this.objectsync.clientId}`)
            this.selectable.click()
            this.transform.globalPosition = this.eventDispatcher.mousePos
            this.eventDispatcher.fakeOnMouseDown() //fake a mouse down to start dragging
        }

        if(this.isPreview){
            this.selectable.enabled = false
        }

        this.link(this.eventDispatcher.onMouseOver, () => {
            this.htmlItem.baseElement.classList.add('hover')
        })

        this.link(this.eventDispatcher.onMouseLeave, () => {
            this.htmlItem.baseElement.classList.remove('hover')
        })

        this.link(this.onAddChild,this.moved.invoke)
        this.link(this.onRemoveChild,this.moved.invoke)
        this.link(this.transform.onChange,this.moved.invoke)
    }

    onParentChangedTo(newParent: SObject): void {
        super.onParentChangedTo(newParent)
        if(newParent instanceof Sidebar){
            newParent.addItem(this.htmlItem, this.category.getValue())
            this.transform.enabled = false
        }
        else
            this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem))
        if(newParent instanceof Node){
            as(this.htmlItem.baseElement,HTMLDivElement).style.borderColor = 'transparent'
            glowDiv(as(this.htmlItem.baseElement, HTMLElement))
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
        }
    }

    public onDestroy(): void {
        super.onDestroy()
        if(this.parent instanceof Sidebar){
            this.parent.removeItem(this.htmlItem, this.category.getValue())
        }
    }
}