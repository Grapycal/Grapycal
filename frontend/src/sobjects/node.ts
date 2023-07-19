import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic} from 'objectsync-client'
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

    private _isPreview: boolean
    get isPreview(): boolean {
        return this._isPreview
    }


    editor: Editor;
    htmlItem: HtmlItem = new HtmlItem(this);
    eventDispatcher: EventDispatcher = new EventDispatcher(this)
    transform: Transform = new Transform(this);
    mouseOverDetector: MouseOverDetector

    protected readonly templates: {[key: string]: string} = {
    normal: 
        `<div class="node normal-node flex-vert space-between">
        
            <div id="label" class="node-label"></div>
            <div class="flex-horiz space-between full-width">
                <div id="slot_input_port" class="no-width flex-vert space-evenly center slot-input-port"></div>
                <div id="slot_output_port" class="no-width flex-vert space-evenly center slot-output-port"></div>
            </div>
            <div id="slot_control" class="slot-control flex-vert space-between"> </div>
        </div>`,
    simple:
        `<div class="node simple-node flex-horiz space-between">
            <div id="label" class="node-label"></div>
            <div id="slot_input_port" class="no-width flex-vert space-evenly slot-input-port"></div>
            <div id="slot_control"  class="slot-control"> </div>

            <div id="slot_output_port" class="no-width flex-vert space-evenly slot-output-port"></div>
        </div>`,
    round:
        `<div class="node round-node flex-horiz space-between" >
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
        this.htmlItem.baseElement.classList.add
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
                const [x, y] = translation.split(',').map(parseFloat)
                this.transform.translation=new Vector2(x, y)
            })
            this.transform.translationChanged.add((x: number, y: number) => {
                this.translation.set(`${x},${y}`)
                this.htmlItem.moveToFront()
            })
        }

        if(this.isPreview){
            this.link(this.eventDispatcher.onDragStart, () => {
                //create a new node
                this.emit('spawn',{client_id:this.objectsync.clientId,translation:`${this.eventDispatcher.mousePos.x},${this.eventDispatcher.mousePos.y}`})
            })
        }

        if(this.hasTag(`spawned_by_${this.objectsync.clientId}`))
        {
            this.removeTag(`spawned_by_${this.objectsync.clientId}`)
            this.transform.globalPosition = this.eventDispatcher.mousePos
            this.eventDispatcher.fakeOnMouseDown() //fake a mouse down to start dragging
        }
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