import { Null, print } from "../devUtils"
import { Component, IComponentable } from "./component"

class MouseOverDetectorMaster{
    private static _instance: MouseOverDetectorMaster = Null();
    static get instance(): MouseOverDetectorMaster{
        if(this._instance == Null())
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
        // https://stackoverflow.com/questions/21051084/javascript-know-all-the-elements-under-your-mouse-pointer-multiple-z-axis-laye
        
        let stack = [], el: Element | null;
        do {
            el = document.elementFromPoint(this.mousePos.x, this.mousePos.y);
            if(el == null) break;
            stack.push(el);
            el.classList.add('pointerEventsNone');
        }while(el.tagName !== 'HTML');
    
        // clean up
        for(var i  = 0; i < stack.length; i += 1)
            stack[i].classList.remove('pointerEventsNone');
    
        this._elementsUnderMouse = stack.map(el => el);
        this._objectsUnderMouse = this._elementsUnderMouse.map(el => this.allObjects.get(el)).filter(obj => obj != undefined).map(obj => obj!);
        this.isDirty = false;
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
    _eventElement: Element = Null();
    get eventElement(): Element{
        return this._eventElement;
    }
    set eventElement(element: Element){
        if(this._eventElement != Null())
            MouseOverDetectorMaster.instance.remove(this.object);
        this._eventElement = element;
        MouseOverDetectorMaster.instance.add(this.object, element);
    }
    constructor(object: IComponentable, eventElement: Element = Null()){
        super(object);
        if (eventElement != Null())
            this.eventElement = eventElement;
    }
    onDestroy(){
        if(this._eventElement != Null())
            MouseOverDetectorMaster.instance.remove(this.object);
    }
}