import { Null, print } from "../devUtils"
import { Component, IComponentable } from "./component"

class MouseOverDetectorMaster{
    private static _instance: MouseOverDetectorMaster = Null();
    static get instance(): MouseOverDetectorMaster{
        if(this._instance == Null())
            this._instance = new MouseOverDetectorMaster();
        return this._instance;
    }
    _frontMostObject: IComponentable = Null();
    get frontMostObject(): IComponentable{
        return this._frontMostObject;
    }
    set frontMostObject(object: IComponentable){
        this._frontMostObject = object;
    }
    _allObjects: IComponentable[] = [];
    get allElements(): IComponentable[]{
        return this._allObjects;
    }
    mouseEnter(object: IComponentable){
        this._allObjects.push(object);
    }
    mouseLeave(object: IComponentable){
        this._allObjects.splice(this._allObjects.indexOf(object), 1);
    }

}

export class MouseOverDetector extends Component{

    static get frontMostObject(): IComponentable{
        return MouseOverDetectorMaster.instance.frontMostObject;
    }
    static get allObjects(): IComponentable[]{
        return MouseOverDetectorMaster.instance.allElements;
    }
    _eventElement: Element = Null();
    get eventElement(): Element{
        return this._eventElement;
    }
    set eventElement(element: Element){
        if(this._eventElement != Null()){
            this._eventElement.removeEventListener("mouseenter", this.mouseEnter);
            this._eventElement.removeEventListener("mouseleave", this.mouseLeave);
        }
        this._eventElement = element;
        this._eventElement.addEventListener("mouseenter", this.mouseEnter);
        this._eventElement.addEventListener("mouseleave", this.mouseLeave);
    }
    constructor(object: IComponentable, eventElement: Element = Null()){
        super(object);
        this.mouseEnter = this.mouseEnter.bind(this);
        this.mouseLeave = this.mouseLeave.bind(this);
        if (eventElement != Null())
            this.eventElement = eventElement;
    }
    mouseEnter(e:Event){
        MouseOverDetectorMaster.instance.mouseEnter(this.object);
        if(e.eventPhase == Event.AT_TARGET){
            MouseOverDetectorMaster.instance.frontMostObject = this.object;
        }
    }
    mouseLeave(e:Event){
        MouseOverDetectorMaster.instance.mouseLeave(this.object);
    }

}