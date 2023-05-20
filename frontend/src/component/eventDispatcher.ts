import { Null, print } from "../devUtils"
import { Action, Vector2 } from "../utils"
import { Component, IComponentable } from "./component"

export interface ICanReceiveMouseEvent{
    addEventListener(type: 'mousedown', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mousemove', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mouseup', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mouseover', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'wheel', listener: (event: WheelEvent) => void, options?: boolean | AddEventListenerOptions): void;

    removeEventListener(type: 'mousedown', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mousemove', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mouseup', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mouseover', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'wheel', listener: (event: WheelEvent) => void, options?: boolean | EventListenerOptions): void;
}

export class EventDispatcher extends Component{
    private eventElement: ICanReceiveMouseEvent = Null();
    private prevMousePos: Vector2 = Vector2.zero;
    private fowardCalled: boolean = false;

    private _mousePos: Vector2 = Vector2.zero;
    get mousePos(){return this._mousePos;}

    public onDragStart = new Action<[MouseEvent,Vector2]>();
    public onDrag = new Action<[MouseEvent,Vector2,Vector2]>();
    public onDragEnd = new Action<[MouseEvent,Vector2]>();
    public onScroll = new Action<[WheelEvent]>();


    constructor(object:IComponentable,eventElement: ICanReceiveMouseEvent = Null()){
        super(object);
        //bind
        this._onMouseDown = this._onMouseDown.bind(this);
        this._onMouseMove = this._onMouseMove.bind(this);
        this._onMouseUp = this._onMouseUp.bind(this);

        this.eventElement = eventElement;
        if(this.eventElement){
            this.setEventElement(this.eventElement)
        }
    }

    private _isDragging: boolean = false;
    get isDragging(){return this._isDragging;}

    public setEventElement(eventElement: ICanReceiveMouseEvent){
        this.eventElement?.removeEventListener('mousedown', this._onMouseDown);
        this.eventElement?.removeEventListener('wheel', this.onScroll.invoke);
        this.eventElement = eventElement;
        this.eventElement.addEventListener('mousedown', this._onMouseDown);
        this.eventElement.addEventListener('wheel', this.onScroll.invoke);
    }

    public forwardEvent(){
        this.fowardCalled = true;
    }

    private _onMouseDown(event: MouseEvent){ 
        this._mousePos = new Vector2(event.clientX, event.clientY);
        this.fowardCalled = false;
        //this.eventElement.addEventListener('mousemove', this._onMouseMove);
        document.addEventListener('mousemove', this._onMouseMove);
        //this.eventElement.addEventListener('mouseup', this._onMouseUp);
        document.addEventListener('mouseup', this._onMouseUp);
        this.prevMousePos = new Vector2(event.clientX, event.clientY);
        if (!this.fowardCalled){
            event.stopPropagation();
        }
        this.fowardCalled = false;
    }

    private _onMouseMove(event: MouseEvent){
        this._mousePos = new Vector2(event.clientX, event.clientY);
        this.fowardCalled = false;
        const mousePos = new Vector2(event.clientX, event.clientY);
        if(!this._isDragging){
            this.onDragStart.invoke(event, mousePos);
            this._isDragging = true;
        }
        this.onDrag.invoke(event, mousePos, this.prevMousePos);
        this.prevMousePos = mousePos;
        if (!this.fowardCalled){
            event.stopPropagation();
        }
    }

    private _onMouseUp(event: MouseEvent){
        this._mousePos = new Vector2(event.clientX, event.clientY);
        this.fowardCalled = false;
        this.onDragEnd.invoke(event, new Vector2(event.clientX, event.clientY));
        this._isDragging = false;
        //this.eventElement.removeEventListener('mousemove', this._onMouseMove);
        document.removeEventListener('mousemove', this._onMouseMove);
        //this.eventElement.removeEventListener('mouseup', this._onMouseUp);
        document.removeEventListener('mouseup', this._onMouseUp);
        if (!this.fowardCalled){
            event.stopPropagation();
        }
    }

}