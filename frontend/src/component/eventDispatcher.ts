import { print } from "../devUtils"
import { Action, Vector2 } from "../utils"
import { Component, IComponentable } from "./component"

export interface ICanReceiveMouseEvent{
    addEventListener(type: 'mousedown', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mousemove', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mouseup', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mouseover', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'wheel', listener: (event: WheelEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'dblclick', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;

    removeEventListener(type: 'mousedown', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mousemove', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mouseup', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mouseover', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'wheel', listener: (event: WheelEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'dblclick', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
}

export class GlobalEventDispatcher{
    static instance: GlobalEventDispatcher = new GlobalEventDispatcher();

    public readonly onMove = new Action<[MouseEvent,Vector2]>();
    public readonly onMouseDown = new Action<[MouseEvent]>();
    public readonly onMouseUp = new Action<[MouseEvent]>();

    public readonly keyState: {[key: string]: boolean} = {};

    private _mousePos: Vector2 = Vector2.zero;
    get mousePos(){return this._mousePos;}
    
    constructor(){
        document.addEventListener('mousemove', this._onMouseMove.bind(this));
        document.addEventListener('mousedown', this._onMouseDown.bind(this));
        document.addEventListener('mouseup', this._onMouseUp.bind(this));
        document.addEventListener('keydown', this._onKeyDown.bind(this));
        document.addEventListener('keyup', this._onKeyUp.bind(this));
    }

    private _onMouseMove(event: MouseEvent){
        this._mousePos = new Vector2(event.clientX, event.clientY);
        this.onMove.invoke(event, new Vector2(event.clientX, event.clientY));
    }

    private _onMouseDown(event: MouseEvent){
        this.onMouseDown.invoke(event);
    }

    private _onMouseUp(event: MouseEvent){
        this.onMouseUp.invoke(event);
    }

    public isKeyDown(key: string){
        let result =  this.keyState[key];
        if(result == undefined) return false;
        return result;
    }

    private _onKeyDown(event: KeyboardEvent){
        this.keyState[event.key] = true;
    }

    private _onKeyUp(event: KeyboardEvent){
        this.keyState[event.key] = false;
    }
}

export class EventDispatcher extends Component{
    static readonly allEventDispatchers: EventDispatcher[] = [];

    private eventElement: ICanReceiveMouseEvent = null;
    private prevMousePos: Vector2 = Vector2.zero;
    private fowardCalled: boolean = false;

    get mousePos(){return GlobalEventDispatcher.instance.mousePos;}
    get onMoveGlobal(){return GlobalEventDispatcher.instance.onMove;}
    get onMouseDownGlobal(){return GlobalEventDispatcher.instance.onMouseDown;}
    get onMouseUpGlobal(){return GlobalEventDispatcher.instance.onMouseUp;}

    public readonly onDragStart = new Action<[MouseEvent,Vector2]>();
    public readonly onDrag = new Action<[MouseEvent,Vector2,Vector2]>();
    public readonly onDragEnd = new Action<[MouseEvent,Vector2]>();
    public readonly onScroll = new Action<[WheelEvent]>();
    public readonly onDoubleClick = new Action<[MouseEvent]>();
    public readonly onMouseDown = new Action<[MouseEvent]>();
    public readonly onClick = new Action<[MouseEvent]>();

    constructor(object:IComponentable,eventElement: ICanReceiveMouseEvent = null){
        super(object);
        EventDispatcher.allEventDispatchers.push(this);
        //bind
        this._onMouseDown = this._onMouseDown.bind(this);
        this._onMouseMove = this._onMouseMove.bind(this);
        this._onMouseUp = this._onMouseUp.bind(this);
        this._onDoubleClick = this._onDoubleClick.bind(this);

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
        this.eventElement?.removeEventListener('dblclick', this._onDoubleClick);
        this.eventElement = eventElement;
        this.eventElement.addEventListener('mousedown', this._onMouseDown);
        this.eventElement.addEventListener('wheel', this.onScroll.invoke);
        this.eventElement.addEventListener('dblclick', this._onDoubleClick);
    }

    public forwardEvent(){
        this.fowardCalled = true;
    }

    /**
     * Usefull when creating a node with mouse
     */
    public fakeOnMouseDown(){
        let event = new MouseEvent('mousedown');
        this._onMouseDown(event);
    }

    private _onMouseDown(event: MouseEvent){
        this.onMouseDown.invoke(event);
        this.fowardCalled = false;
        document.addEventListener('mousemove', this._onMouseMove);
        document.addEventListener('mouseup', this._onMouseUp);
        this.prevMousePos = new Vector2(this.mousePos.x, this.mousePos.y);
        if (!this.fowardCalled && this.onDragStart.numCallbacks > 0 ||this.onDragStart.numCallbacks > 0 || this.onDrag.numCallbacks > 0 || this.onDragEnd.numCallbacks > 0){
            event.stopPropagation();
        }
        this.fowardCalled = false;
    }

    private _onMouseMove(event: MouseEvent){
        this.fowardCalled = false;
        const mousePos = new Vector2(event.clientX, event.clientY);
        if(!this._isDragging){
            this.onDragStart.invoke(event, mousePos);
            this._isDragging = true;
        }
        this.onDrag.invoke(event, mousePos, this.prevMousePos);
        this.prevMousePos = mousePos;
        event.preventDefault(); // Avoid selecting text
        if (!this.fowardCalled){
            event.stopPropagation();
        }
    }

    private _onMouseUp(event: MouseEvent){
        this.fowardCalled = false;
        if (this._isDragging)
            this.onDragEnd.invoke(event, new Vector2(event.clientX, event.clientY));
        else{
            this.onClick.invoke(event);
        }
        this._isDragging = false;
        document.removeEventListener('mousemove', this._onMouseMove);
        document.removeEventListener('mouseup', this._onMouseUp);
    }

    private _onDoubleClick(event: MouseEvent){
        this.fowardCalled = false;
        this.onDoubleClick.invoke(event);
        if (!this.fowardCalled){
            event.stopPropagation();
        }
    }

    public onDestroy(){
        EventDispatcher.allEventDispatchers.splice(EventDispatcher.allEventDispatchers.indexOf(this), 1);
        this.eventElement?.removeEventListener('mousedown', this._onMouseDown);
        this.eventElement?.removeEventListener('wheel', this.onScroll.invoke);
        this.eventElement?.removeEventListener('dblclick', this._onDoubleClick);
        super.onDestroy();
    }
}