import { print } from "../devUtils"
import { Component, IComponentable } from "./component"

class MouseOverDetectorMaster{
    private static _instance: MouseOverDetectorMaster = null;
    static get instance(): MouseOverDetectorMaster{
        if(this._instance == null)
            this._instance = new MouseOverDetectorMaster();
        return this._instance;
    }

    private _objectsUnderMouse: IComponentable[] = [];
    private _elementsUnderMouse: Element[] = [];

    get objectsUnderMouse(): IComponentable[]{
        if(this.isDirty){
            this.check()
        }
        return this._objectsUnderMouse;
    }

    get elementsUnderMouse(): Element[]{
        if(this.isDirty){
            this.check()
        }
        return this._elementsUnderMouse;
    }
    private isDirty: boolean = false;
    private allObjects = new Map<Element,IComponentable>();
    private mousePos = {x: 0, y: 0};

    constructor(){
        document.addEventListener("mousemove", (event) => {
            this.isDirty = true; 
            this.mousePos = {x: event.clientX, y: event.clientY};
        });
    }
    
    private check(){
        let els = document.elementsFromPoint(this.mousePos.x, this.mousePos.y)
        this._objectsUnderMouse = els.map(el => this.allObjects.get(el)).filter(obj => obj != undefined).map(obj => obj!);
    }

    public add(object: IComponentable, element: Element){
        this.allObjects.set(element, object);
    }

    public remove(object: IComponentable){
        for(let [element, obj] of this.allObjects){
            if(obj == object){
                this.allObjects.delete(element);
                return;
            }
        }
    }
}

export class MouseOverDetector extends Component{

    static get objectsUnderMouse(): IComponentable[]{
        return MouseOverDetectorMaster.instance.objectsUnderMouse;
    }
    _eventElement: Element = null;
    get eventElement(): Element{
        return this._eventElement;
    }
    set eventElement(element: Element){
        if(this._eventElement != null)
            MouseOverDetectorMaster.instance.remove(this.object);
        this._eventElement = element;
        MouseOverDetectorMaster.instance.add(this.object, element);
    }
    constructor(object: IComponentable, eventElement: Element = null){
        super(object);
        if (eventElement != null)
            this.eventElement = eventElement;
    }
    onDestroy(){
        if(this._eventElement != null)
            MouseOverDetectorMaster.instance.remove(this.object);
    }
}