import { print } from "../devUtils"
import { Action, Vector2, as } from "../utils"
import { Component, IComponentable } from "./component"
import { EventDispatcher, GlobalEventDispatcher } from "./eventDispatcher"
import { HtmlItem } from "./htmlItem"
import { Linker } from "./linker"

export class TransformRoot extends Component{
    scale: number = 1;
    translation: Vector2 = Vector2.zero;
    pivot: Vector2 = new Vector2(0.5, 0.5);
    
    onChange = new Action<[]>(); //dummy

    worldToLocal(position: Vector2){
        return position;
    }
}


// Dependency: HtmlItem
export class Transform extends Component{
    htmlItem: HtmlItem = null;
    linker = new Linker(this);
    parent: Transform | TransformRoot = null;
    _targetElement: HTMLElement = null;
    get targetElement(){return this._targetElement;}
    set targetElement(targetElement: HTMLElement){
        this._targetElement = targetElement;
        if(targetElement != null && this.draggable){
            if(this.actuallyDraggable){
                this.targetElement.style.position = 'absolute'
                this.targetElement.style.left = '0px'
                this.targetElement.style.top = '0px'
            }
        }
    }
    specifiedTargetElement: HTMLElement = null;

    onChange = new Action<[]>();
    dragged = new Action<[Vector2]>();

    private _pivot: Vector2 = new Vector2(0.5, 0.5);
    private _scale: number = 1;
    private _translation: Vector2 = Vector2.zero;

    public scrollSmoothness: number = 0;

    get pivot(){return this._pivot;}
    set pivot(pivot: Vector2){
        this._pivot = pivot;
        this.targetElement.style.transformOrigin = `${pivot.x*100}% ${pivot.y*100}%`;
        this.updateUI();
    }
    
    get scale(){return this._scale;}
    scaleChanged = new Action<[number]>();
    set scale(scale: number){
        if(this.maxScale !== null && scale > this.maxScale){
            scale = this.maxScale;
        }
        if(this.minScale !== null && scale < this.minScale){
            scale = this.minScale;
        }
        this._scale = scale;
        this.updateUI();
        this.scaleChanged.invoke(scale);
    }
    setscale(scale: number){
        this._scale = scale;
        this.updateUI();
    }
    
    get translation(){return this._translation;}
    translationChanged = new Action<[number, number]>();
    set translation(translation: Vector2){
        this._translation = translation;
        this.updateUI();
        this.translationChanged.invoke(translation.x, translation.y);
        this.onChange.invoke();
    }
    set globalPosition(globalPosition: Vector2){
        this.translation = this.parent.worldToLocal(globalPosition);
    }

    _draggable: boolean = false;
    get draggable(){return this._draggable;}
    set draggable(draggable: boolean){
        if(this._draggable == draggable) return;
        this._draggable = draggable;
        if (this.enabled && draggable)
            this.actuallyDraggable = true;
        else
            this.actuallyDraggable = false;
    }

    _actuallyDraggable: boolean = false; // Yes I ran out of naming ideas
    private get actuallyDraggable(){return this._actuallyDraggable;}
    private set actuallyDraggable(actuallyDraggable: boolean){
        if(this._actuallyDraggable == actuallyDraggable) return;
        this._actuallyDraggable = actuallyDraggable;

        if (actuallyDraggable){
            this.linker.link(this.getComponent(EventDispatcher).onDrag,this.onDrag);
            this.targetElement.style.position = 'absolute'
            this.targetElement.style.left = '0px'
            this.targetElement.style.top = '0px'
        }
        else
        {
            this.linker.unlink(this.getComponent(EventDispatcher).onDrag);
            this.targetElement.style.position = 'relative'
        }
    }


    _scrollable: boolean = false;
    get scrollable(){return this._scrollable;}
    set scrollable(scrollable: boolean){
        if(this._scrollable == scrollable) return;
        this._scrollable = scrollable;
        if (this.enabled && scrollable)
            this.actuallyScrollable = true;
        else
            this.actuallyScrollable = false;
    }

    _maxScale: number|null = null;
    get maxScale(){return this._maxScale;}
    set maxScale(maxScale: number){
        this._maxScale = maxScale;
        if(this._maxScale !== null && this.scale > maxScale){
            this.scale = maxScale;
        }
    }

    _minScale: number|null = null;
    get minScale(){return this._minScale;}
    set minScale(minScale: number){
        this._minScale = minScale;
        if(this._minScale !== null && this.scale < minScale){
            this.scale = minScale;
        }
    }

    _actuallyScrollable: boolean = false;
    private get actuallyScrollable(){return this._actuallyScrollable;}
    private set actuallyScrollable(actuallyScrollable: boolean){
        if(this._actuallyScrollable == actuallyScrollable) return;
        this._actuallyScrollable = actuallyScrollable;

        this.onScroll = this.onScroll.bind(this);
        if (actuallyScrollable){
            this.getComponent(EventDispatcher).onScroll.add(this.onScroll);
        }
        else
            this.getComponent(EventDispatcher).onScroll.remove(this.onScroll);
    }

    _enabled: boolean = true;
    get enabled(){return this._enabled;}
    set enabled(enabled: boolean){
        this._enabled = enabled;
        if (enabled && this.draggable)
            this.actuallyDraggable = true;
        else
            this.actuallyDraggable = false;

        if (enabled && this.scrollable)
            this.actuallyScrollable = true;
        else
            this.actuallyScrollable = false;
        if(!enabled){
            this.targetElement.style.transform = 'none';
        }
    }

    get worldPosition(){
        return this.getAbsoluteOrigin();
    }

    get parentPosition(){
        return this.translation
    }

    get localCenter(){
        return new Vector2(
            this.targetElement.offsetWidth*(0.5-this.pivot.x),
            this.targetElement.offsetHeight*(0.5-this.pivot.y)
        );
    }

    get worldCenter(){
        return this.localToWorld(this.localCenter);
    }

    get size(){
        let rect = this.targetElement.getBoundingClientRect();
        return new Vector2(rect.width, rect.height);
    }

    // get worldCenter(){
    //     return {
    //         x: this.worldPosition.x + this.targetElement.clientWidth*(0.5-this.pivot.x),
    //         y: this.worldPosition.y + this.targetElement.clientHeight*(0.5-this.pivot.y)
    //     }
    // }
    
    constructor(object:IComponentable, targetElement:HTMLElement=null, eventEl: HTMLElement=null){
        super(object);
        this.htmlItem = this.getComponent(HtmlItem);
        this.specifiedTargetElement = targetElement;
        this.targetElement = this.specifiedTargetElement || as(this.htmlItem.baseElement,HTMLElement);

        this.htmlItem.templateChanged.add(this.templateChanged.bind(this));

        this.updateParent();
        this.updateUI();
    }

    private templateChanged(){
        // remove callback
        this.targetElement = this.specifiedTargetElement || as(this.htmlItem.baseElement,HTMLElement);
        this.enabled = false
        this.enabled = true
        this.updateUI();
    }

    private onDrag(e:MouseEvent,mousePos:Vector2,prevMousePos:Vector2){
        let startMouseLocal = this.worldToLocal(prevMousePos);
        let mouseLocal = this.worldToLocal(mousePos);
        let delta = new Vector2(
            (mouseLocal.x - startMouseLocal.x)*this.scale,
            (mouseLocal.y - startMouseLocal.y)*this.scale
        )
        this.translate(delta);
        this.dragged.invoke(delta);
    }

    private onScroll(e:WheelEvent){
        e.stopPropagation();
        this.smoothScroll(-0.001*e.deltaY);
    }

    private smoothScroll(amount:number){
        let a = Math.exp(-this.scrollSmoothness);
        let startMouseLocal = this.worldToLocal(GlobalEventDispatcher.instance.mousePos);
        this.scale *= Math.exp(amount*a);
        this.updateUI();
        let mouseLocal = this.worldToLocal(GlobalEventDispatcher.instance.mousePos);
        this.translate(new Vector2(
            (mouseLocal.x - startMouseLocal.x)*this.scale,
            (mouseLocal.y - startMouseLocal.y)*this.scale
        ));
        if(Math.abs(amount) > 0.001){
            setTimeout(() => {
                this.smoothScroll(amount*(1-a));
            }, 20);
        }
        
    }

    public translate(translation: Vector2){  
        this.translation = this.translation.add(translation);
    }

    public scaleBy(scale: number){
        this.scale *= scale;
        this.onChange.invoke();
        this.updateUI();
    }


    private updateParent(){
        this.parent = this.htmlItem.findTransformParent() || new TransformRoot(this.object);
    }

    private updateUI(){
        if(!this.enabled)
            return;
        if (this.targetElement === null)
            return;
        this.updateParent();
        let transformString = ''
        transformString += `translate(${this.pivot.x*-100}%,${this.pivot.y*-100}%)`
        transformString += `translate(${this._translation.x}px,${this._translation.y}px)`;
        transformString += `scale(${this._scale})`
        this.targetElement.style.transform = transformString;
    }

    private notifyChangeToChildren(){
        for(let child of this.htmlItem.findTransformChildren()){
            child.onChange.invoke();
        }
    }

    public getAbsoluteOrigin(){
        this.updateUI();
        let rect = this.targetElement.getBoundingClientRect()
        return new Vector2(
            rect.x + rect.width*this.pivot.x,
            rect.y + rect.height*this.pivot.y
        );
    }

    public getAbsoluteScale(){
        this.updateUI();
        // Only works if element size is not zero
        // let rect = this.targetElement.getBoundingClientRect()
        // return {
        //     'x':rect.width/this.targetElement.offsetWidth,
        //     'y':rect.height/this.targetElement.offsetHeight
        // };
        let s = this.scale;
        let parent = this.parent;
        while(!(parent instanceof TransformRoot)){
            s *= parent.scale;
            parent = parent.parent;
        }
        return new Vector2(s,s);
    }

    public worldToLocal(pos: Vector2){
        let absOrigin = this.getAbsoluteOrigin();
        let absScale = this.getAbsoluteScale();
        return new Vector2(
            (pos.x - absOrigin.x)/absScale.x,
            (pos.y - absOrigin.y)/absScale.y
        )
    }

    public localToWorld(pos: Vector2){
        let absOrigin = this.getAbsoluteOrigin();
        let absScale = this.getAbsoluteScale();
        return new Vector2(
            pos.x*absScale.x + absOrigin.x,
            pos.y*absScale.y + absOrigin.y
        )
    }

    public othersToLocal(others: Transform){
        return this.worldToLocal(others.worldPosition);
    }
}
