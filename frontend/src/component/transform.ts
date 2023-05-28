import { Null, print } from "../devUtils"
import { Action, Vector2, as } from "../utils"
import { Component, IComponentable } from "./component"
import { EventDispatcher } from "./eventDispatcher"
import { HtmlItem } from "./htmlItem"

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
    htmlItem: HtmlItem = Null();
    parent: Transform | TransformRoot = Null();
    _targetElement: HTMLElement = Null();
    get targetElement(){return this._targetElement;}
    set targetElement(targetElement: HTMLElement){
        this._targetElement = targetElement;
        if(targetElement != Null() && this.draggable){
            this.targetElement.style.position = 'absolute'
            this.targetElement.style.left = '0px'
            this.targetElement.style.top = '0px'
        }
    }
    specifiedTargetElement: HTMLElement = Null();

    onChange = new Action<[]>();

    private _pivot: Vector2 = new Vector2(0.5, 0.5);
    private _scale: number = 1;
    private _translation: Vector2 = Vector2.zero;

    get pivot(){return this._pivot;}
    set pivot(pivot: Vector2){
        this._pivot = pivot;
        this.targetElement.style.transformOrigin = `${pivot.x*100}% ${pivot.y*100}%`;
        this.updateUI();
    }
    
    get scale(){return this._scale;}
    scaleChanged = new Action<[number]>();
    set scale(scale: number){
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
    settranslation(translation: Vector2){
        this._translation = translation;
        this.updateUI();
    }

    _draggable: boolean = false;
    get draggable(){return this._draggable;}
    set draggable(draggable: boolean){
        this._draggable = draggable;

        this.onDrag = this.onDrag.bind(this);
        if (draggable){
            this.getComponent(EventDispatcher).onDrag.add(this.onDrag);
        }
        else
            this.getComponent(EventDispatcher).onDrag.remove(this.onDrag);
    }

    _scrollable: boolean = false;
    get scrollable(){return this._scrollable;}
    set scrollable(scrollable: boolean){
        this._scrollable = scrollable;
        this.onScroll = this.onScroll.bind(this);
        if (scrollable){
            this.getComponent(EventDispatcher).onScroll.add(this.onScroll);
        }
        else
            this.getComponent(EventDispatcher).onScroll.remove(this.onScroll);
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

    // get worldCenter(){
    //     return {
    //         x: this.worldPosition.x + this.targetElement.clientWidth*(0.5-this.pivot.x),
    //         y: this.worldPosition.y + this.targetElement.clientHeight*(0.5-this.pivot.y)
    //     }
    // }
    
    constructor(object:IComponentable, targetElement:HTMLElement=Null(), eventEl: HTMLElement=Null()){
        super(object);
        this.htmlItem = this.getComponent(HtmlItem);
        this.specifiedTargetElement = targetElement;
        this.targetElement = this.specifiedTargetElement || as(this.htmlItem.baseElement,HTMLElement);

        this.htmlItem.templateChanged.add(this.templateChanged.bind(this));
        
        //this.onChange.add(this.notifyChangeToChildren.bind(this));

        this.updateParent();
        this.updateUI();
    }

    private templateChanged(){
        // remove callback
        this.targetElement = this.specifiedTargetElement || as(this.htmlItem.baseElement,HTMLElement);
        this.updateUI();
    }

    onDrag(e:MouseEvent,mousePos:Vector2,prevMousePos:Vector2){
        let startMouseLocal = this.worldToLocal(prevMousePos);
        let mouseLocal = this.worldToLocal(mousePos);
        this.translate(new Vector2(
            (mouseLocal.x - startMouseLocal.x)*this.scale,
            (mouseLocal.y - startMouseLocal.y)*this.scale
        ));
        mouseLocal = this.worldToLocal(mousePos);
        this.updateUI();
    }

    onScroll(e:WheelEvent){
        e.stopPropagation();
        let startMouseLocal = this.worldToLocal(new Vector2(e.clientX, e.clientY));
        this.scale *= Math.exp(-0.001*e.deltaY);
        this.updateUI();
        let mouseLocal = this.worldToLocal(new Vector2(e.clientX, e.clientY));
        this.translate(new Vector2(
            (mouseLocal.x - startMouseLocal.x)*this.scale,
            (mouseLocal.y - startMouseLocal.y)*this.scale
        ));
        mouseLocal = this.worldToLocal(new Vector2(e.clientX, e.clientY));
    }

    public translate(translation: Vector2){  
        this.translation = this.translation.add(translation);
        this.onChange.invoke();
        this.updateUI();
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
        if (this.targetElement === null)
            return;
        this.updateParent();
        let transformString = ''
        //if(this.parent !== null)
            //transformString += `translate(${this.parent.pivot.x*-100}%,${this.parent.pivot.y*-100}%)`
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
        let rect = this.targetElement.getBoundingClientRect()
        return {
            'x':rect.width/this.targetElement.offsetWidth,
            'y':rect.height/this.targetElement.offsetHeight
        };
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
