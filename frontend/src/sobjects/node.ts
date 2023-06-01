import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic, ListTopic, ObjListTopic} from 'objectsync-client'
import { editor, soundManager } from '../app'
import { HtmlItem } from '../component/htmlItem'
import { Transform } from '../component/transform'
import { CompSObject } from './compSObject'
import { print } from '../devUtils'
import { Port } from './port'
import { glowDiv as glowDiv, glowText } from '../ui_utils/effects'
import { Vector2, as } from '../utils'
import { EventDispatcher } from '../component/eventDispatcher'
import { MouseOverDetector } from '../component/mouseOverDetector'
import { Sidebar } from './sideBar'

export class Node extends CompSObject {
    use_transform: GenericTopic<boolean> = this.getAttribute('use_transform', GenericTopic<boolean>)
    display_ports: GenericTopic<boolean> = this.getAttribute('display_ports', GenericTopic<boolean>)

    shape: StringTopic = this.getAttribute('shape', StringTopic) // round, block, frame
    output: StringTopic = this.getAttribute('output', StringTopic)
    label: StringTopic = this.getAttribute('label', StringTopic)
    label_offset: FloatTopic = this.getAttribute('label_offset', FloatTopic)
    translation: StringTopic = this.getAttribute('translation', StringTopic)
    primary_color: StringTopic = this.getAttribute('primary_color', StringTopic)
    category: StringTopic = this.getAttribute('category', StringTopic)

    private _isPreview: boolean
    get isPreview(): boolean {
        return this._isPreview
    }

    in_ports: ObjListTopic<Port> = this.getAttribute('in_ports', ObjListTopic<Port>)
    out_ports: ObjListTopic<Port> = this.getAttribute('out_ports', ObjListTopic<Port>)

    htmlItem: HtmlItem = new HtmlItem(this);
    eventDispatcher: EventDispatcher = new EventDispatcher(this)
    transform: Transform = new Transform(this);
    mouseOverDetector: MouseOverDetector

    protected readonly templates: {[key: string]: string} = {
    block: 
        `<div class="BlockNode flex-horiz space-between">
            <div id="slot_input_port" class="no-width flex-vert space-evenly"></div>
            <div class="NodeContent full-width flex-vert space-evenly">
                <div id="label" class="center" ></div>
                <div id="slot_default"> </div>
            </div>
            <div id="slot_output_port" class="no-width flex-vert space-evenly"></div>
        </div>`,
    round:
        `<div class="RoundNode flex-horiz space-between" >
            <div id="slot_input_port" class="no-width flex-vert space-evenly"></div>
            <div class="full-width flex-vert space-evenly"> 
                <div id="label" class="center" style="font-size:36px"></div>
            </div>
            <div id="slot_default" style="display:none"></div>
            <div id="slot_output_port" class="no-width flex-vert space-evenly"></div>
        </div>`,
    frame:
        `<div class="FrameNode flex-horiz space-between">
            <div id="slot_input_port" class="no-width flex-vert space-evenly"></div>
            <div class="NodeContent full-width flex-vert space-evenly"> 
                <div id="label" class="center DisplayNone"></div>
                <div id="slot_default"> </div>
            </div>
            <div id="slot_output_port" class="no-width flex-vert space-evenly"></div>
        </div>`,
    }

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)

        
        // Initialize UI

        this.mouseOverDetector = new MouseOverDetector(this)
        if(!this._isPreview) 

        this.link(this.eventDispatcher.onDoubleClick, () => {
            this.emit('double_click')
        })
    }

    protected onStart(): void {
        super.onStart()
        this._isPreview = this.parent instanceof Sidebar
        
        // Bind attributes to UI

        this.shape.onSet.add(this.reshape.bind(this))

        // this.link(this.use_transform.onSet, (use_transform: boolean) => {
        //     if(this.transform)
        //         this.transform.enabled = use_transform
        // })

        this.link(this.display_ports.onSet, (display_ports: boolean) => {
            if(this.htmlItem.getHtmlEl('slot_input_port'))
                if(display_ports){
                    this.htmlItem.getHtmlEl('slot_input_port').style.display = 'flex'
                    this.htmlItem.getHtmlEl('slot_output_port').style.display = 'flex'
                }else{
                    this.htmlItem.getHtmlEl('slot_input_port').style.display = 'none'
                    this.htmlItem.getHtmlEl('slot_output_port').style.display = 'none'
                }
        })

        this.in_ports.onInsert.add((port: Port) => {
            this.reshapePort(port)
        })

        this.out_ports.onInsert.add((port: Port) => {
            this.reshapePort(port)
        })

        this.link(this.label.onSet, (label: string) => {
            this.htmlItem.getHtmlEl('label').innerText = label
        })

        this.link(this.label_offset.onSet, (offset: number) => {
            let label_el = this.htmlItem.getHtmlEl('label')
            let font_size = parseFloat(label_el.style.fontSize.split('px')[0])
            
            label_el.style.marginTop = this.label_offset.getValue()*font_size + 'px'
        })

        this.link(this.primary_color.onSet, (color: string) => {
            this.htmlItem.getHtmlEl('label').style.color = color
            as(this.htmlItem.baseElement,HTMLDivElement).style.borderColor = color
            glowDiv(as(this.htmlItem.baseElement, HTMLElement))
            for(let div of this.htmlItem.baseElement.querySelectorAll('div')){
                glowText(div)
            }
        })

        this.link(this.category.onSet2, (oldCategory: string, newCategory: string) => {
            if(this.parent instanceof Sidebar){
                if(this.parent.hasItem(this.htmlItem))
                    this.parent.removeItem(this.htmlItem, oldCategory)
                this.parent.addItem(this.htmlItem, newCategory)
            }
        })

        // Configure components
        
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem) || editor.htmlItem)

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

    protected postStart(): void {
        super.postStart()
        for(const port of this.in_ports){
            this.reshapePort(port)
        }
        for(const port of this.out_ports){
            this.reshapePort(port)
        }
    }

    onParentChangedTo(newParent: SObject): void {
        super.onParentChangedTo(newParent)
        if(newParent instanceof Sidebar){
            newParent.addItem(this.htmlItem, this.category.getValue())
            this.transform.enabled = false
        }
        else
        this.htmlItem.setParent(this.getComponentInAncestors(HtmlItem) || editor.htmlItem)
        if(newParent instanceof Node){
            as(this.htmlItem.baseElement,HTMLDivElement).style.borderColor = 'transparent'
            glowDiv(as(this.htmlItem.baseElement, HTMLElement))
            this.transform.enabled = false
        }else{
            as(this.htmlItem.baseElement,HTMLDivElement).style.borderColor = this.primary_color.getValue()
            glowDiv(as(this.htmlItem.baseElement, HTMLElement))
            this.transform.enabled = this.use_transform.getValue()
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
        label_el.innerText = this.label.getValue()
        let font_size = parseFloat(label_el.style.fontSize.split('px')[0])

        label_el.style.marginTop = this.label_offset.getValue()*font_size + 'px'

        if(this._isPreview){
            this.htmlItem.baseElement.classList.add('NodePreview')
        }else{
            this.htmlItem.baseElement.classList.add('Node')
        }
        this.htmlItem.getHtmlEl('label').style.color = this.primary_color.getValue()
        as(this.htmlItem.baseElement,HTMLDivElement).style.borderColor = this.primary_color.getValue()
        glowDiv(as(this.htmlItem.baseElement, HTMLElement))
        //glow text
        for(let div of this.htmlItem.baseElement.querySelectorAll('div')){
            glowText(div)
        }
    }

    reshapePort(port:Port){
        if(this.shape.getValue() == 'block'){
            port.displayLabel = false
        }
        if(this.shape.getValue() == 'round'){
            port.displayLabel = false
        }
        if(this.shape.getValue() == 'frame'){
            port.displayLabel = false
        }
    }

    public onDestroy(): void {
        super.onDestroy()
        if(this.parent instanceof Sidebar){
            this.parent.removeItem(this.htmlItem, this.category.getValue())
        }
    }
}