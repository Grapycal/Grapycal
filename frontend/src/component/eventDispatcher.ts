import { print } from "../devUtils"
import { Action,ActionDict, Vector2 } from "../utils"
import { Component, IComponentable } from "./component"
import { HtmlItem } from "./htmlItem"

export interface ICanReceiveMouseEvent{
    addEventListener(type: 'mousedown', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mousemove', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mouseup', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mouseover', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'wheel', listener: (event: WheelEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'dblclick', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: 'mouseleave', listener: (event: MouseEvent) => void, options?: boolean | AddEventListenerOptions): void;

    removeEventListener(type: 'mousedown', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mousemove', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mouseup', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mouseover', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'wheel', listener: (event: WheelEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'dblclick', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: 'mouseleave', listener: (event: MouseEvent) => void, options?: boolean | EventListenerOptions): void;
}

export class GlobalEventDispatcher{
    static instance: GlobalEventDispatcher = new GlobalEventDispatcher();

    public readonly onMove = new Action<[MouseEvent,Vector2]>();
    public readonly onMouseDown = new Action<[MouseEvent]>();
    public readonly onMouseUp = new Action<[MouseEvent]>();
    public readonly onKeyDown = new ActionDict<string,[KeyboardEvent]>()
    public readonly onAnyKeyDown = new Action<[KeyboardEvent]>();

    public readonly keyState: {[key: string]: boolean} = {};

    private _mousePos: Vector2 = new Vector2(window.innerWidth/2, window.innerHeight/2);
    get mousePos(){return this._mousePos;}
    
    constructor(){
        // All listen on capture phase
        document.addEventListener('mousemove', this._onMouseMove.bind(this),true);
        document.addEventListener('mousedown', this._onMouseDown.bind(this),true);
        document.addEventListener('mouseup', this._onMouseUp.bind(this),true);
        document.addEventListener('keydown', this._onKeyDown.bind(this),true);
        document.addEventListener('keyup', this._onKeyUp.bind(this),true);
        window.addEventListener('blur', this._onBlur.bind(this),true);
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
        // to lower case if [A-Z]
        let key = event.key;
        if(key.length == 1 && key.match(/[A-Z]/)){
            key = key.toLowerCase();
        }
        // key
        this.onKeyDown.invoke(key,event);
        // ctrl key
        if(event.ctrlKey){
            this.onKeyDown.invoke(`ctrl ${key}`,event);
        }
        // alt key
        if(event.altKey){
            this.onKeyDown.invoke(`alt ${key}`,event);
        }
        // shift key
        if(event.shiftKey){
            this.onKeyDown.invoke(`shift ${key}`,event);
        }
        // ctrl shift key
        if(event.ctrlKey && event.shiftKey){
            this.onKeyDown.invoke(`ctrl shift ${key}`,event);
        }
        this.onAnyKeyDown.invoke(event);
        this.keyState[key] = true;
    }

    private _onKeyUp(event: KeyboardEvent){
        // to lower case if [A-Z]
        let key = event.key;
        if(key.length == 1 && key.match(/[A-Z]/)){
            key = key.toLowerCase();
        }

        this.keyState[key] = false;
    }

    private _onBlur(event: FocusEvent){
        for(let key in this.keyState){
            this.keyState[key] = false;
        }
    }
}

export class EventDispatcher extends Component{
    static readonly allEventDispatchers: EventDispatcher[] = [];

    private eventElement: ICanReceiveMouseEvent = null;
    private prevMousePos: Vector2 = Vector2.zero;
    private fowardCalled: boolean = false;
    private _isDraggable: (e:MouseEvent) => boolean = () => true;
    public set isDraggable(value: (e:MouseEvent) => boolean){
        this._isDraggable = value;
    }

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
    public readonly onMouseOver = new Action<[MouseEvent]>();
    public readonly onMouseLeave = new Action<[MouseEvent]>();

    constructor(object:IComponentable,eventElement: ICanReceiveMouseEvent = null){
        super(object);
        EventDispatcher.allEventDispatchers.push(this);
        //bind
        this._onMouseDown = this._onMouseDown.bind(this);
        this._onMouseMove = this._onMouseMove.bind(this);
        this._onMouseUp = this._onMouseUp.bind(this);
        this._onDoubleClick = this._onDoubleClick.bind(this);

        if(eventElement == null){
            if(this.componentManager.hasComponent(HtmlItem)){
                eventElement = this.componentManager.getComponent(HtmlItem).baseElement;
            }
        }
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
        this.eventElement?.removeEventListener('mouseover', this.onMouseOver.invoke);
        this.eventElement?.removeEventListener('mouseleave', this.onMouseLeave.invoke);
        this.eventElement = eventElement;
        this.eventElement.addEventListener('mousedown', this._onMouseDown);
        this.eventElement.addEventListener('wheel', this.onScroll.invoke);
        this.eventElement.addEventListener('dblclick', this._onDoubleClick);
        this.eventElement.addEventListener('mouseover', this.onMouseOver.invoke);
        this.eventElement.addEventListener('mouseleave', this.onMouseLeave.invoke);
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
        this.fowardCalled = false;
        this.onMouseDown.invoke(event);
        if(!this._isDraggable(event)){
            if (!this.fowardCalled && this.onMouseDown.numCallbacks > 0){
                event.stopPropagation();
            }
            return;
        }
        document.addEventListener('mousemove', this._onMouseMove);
        document.addEventListener('mouseup', this._onMouseUp);
        this.prevMousePos = new Vector2(this.mousePos.x, this.mousePos.y);
        if (!this.fowardCalled && (this.onDragStart.numCallbacks > 0 || this.onDrag.numCallbacks > 0 || this.onDragEnd.numCallbacks > 0)){
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
        this.eventElement?.removeEventListener('mouseover', this.onMouseOver.invoke);
        this.eventElement?.removeEventListener('mouseleave', this.onMouseLeave.invoke);
        document.removeEventListener('mousemove', this._onMouseMove);
        document.removeEventListener('mouseup', this._onMouseUp);
        super.onDestroy();
    }
}