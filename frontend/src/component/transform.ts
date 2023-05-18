import { Null, print } from "../devUtils"
import { Action } from "../utils"
import { Component, IComponentable } from "./component"
import { HtmlItem } from "./htmlItem"

export class TransformRoot extends Component{
    scale: number = 1;
    translation: {x: number, y: number} = {x: 0, y: 0};
    pivot: {x: number, y: number} = {x: 0.5, y: 0.5};
}

// Dependency: HtmlItem
export class Transform extends Component{
    htmlItem: HtmlItem = Null();
    parent: Transform | TransformRoot = Null();
    targetElement: HTMLElement = Null();
    specifiedTargetElement: HTMLElement = Null();
    specifiedEventEl: HTMLElement = Null();
    eventEl: HTMLElement = Null();
    _pivot: {x: number, y: number} = {x: 0.5, y: 0.5};
    _scale: number = 1;
    _translation: {x: number, y: number} = {x: 0, y: 0};

    get pivot(){return this._pivot;}
    set pivot(pivot: {x: number, y: number}){
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
    set translation(translation: {x: number, y: number}){
        this._translation = translation;
        this.updateUI();
        this.translationChanged.invoke(translation.x, translation.y);
    }
    settranslation(translation: {x: number, y: number}){
        this._translation = translation;
        this.updateUI();
    }

    _draggable: boolean = false;
    get draggable(){return this._draggable;}
    set draggable(draggable: boolean){
        this._draggable = draggable;
        if (draggable){
            if (this.eventEl !== Null())
                this.makeDraggable();
            this.targetElement.style.position = 'absolute';
        }
        else
            this.eventEl.onmousedown = null;
    }

    _scrollable: boolean = false;
    get scrollable(){return this._scrollable;}
    set scrollable(scrollable: boolean){
        this._scrollable = scrollable;
        if (scrollable){
            if (this.eventEl !== Null())
                this.makeScrollable();
            this.targetElement.style.position = 'absolute';
        }
        else
            this.eventEl.onwheel = null;
    }
    
    constructor(object:IComponentable, targetElement:HTMLElement=Null(), eventEl: HTMLElement=Null()){
        super(object);
        this.htmlItem = this.getComponent(HtmlItem);
        this.specifiedTargetElement = targetElement;
        this.targetElement = this.specifiedTargetElement || this.htmlItem.baseElement;
        this.specifiedEventEl = eventEl;
        this.eventEl = this.specifiedEventEl || this.targetElement;

        this.htmlItem.templateChanged.add(this.templateChanged.bind(this));
        
        this.updateParent();
        this.updateUI();
    }

    private templateChanged(){
        // remove callback
        if (this.draggable && this.eventEl !== Null()){       
            this.eventEl.onwheel = null;
            this.eventEl.onmousedown = null;
        }

        this.targetElement = this.specifiedTargetElement || this.htmlItem.baseElement;
        this.eventEl = this.specifiedEventEl || this.targetElement;

        if (this.draggable)
            this.makeDraggable();

        if (this.scrollable)
            this.makeScrollable();
            
        this.updateUI();
    }

    // strategy: fix mouse local position
    makeDraggable(){
        this.eventEl.onmousedown = (e) => {
            e.stopPropagation();
            let startMouseLocal = this.worldToLocal({x: e.clientX, y: e.clientY});
            let onmousemove = (e: MouseEvent) => {
                e.stopPropagation();
                this.updateParent();
                let parentScale = this.parent.scale || 1;
                let mouseLocal = this.worldToLocal({x: e.clientX, y: e.clientY});
                // mouseLocal has shifted now. Subtract the shift to get the translation
                this.translation = {
                    x: this.translation.x + 
                    (mouseLocal.x - startMouseLocal.x)
                    *this.scale, // local to parent space
                    y: this.translation.y + (mouseLocal.y - startMouseLocal.y)*this.scale
                }
                //print(mouseLocal.x,startMouseLocal.x,this.translation.x)
                mouseLocal = this.worldToLocal({x: e.clientX, y: e.clientY});
                this.updateUI();
            }
            let onmouseup = (e: MouseEvent) => {
                e.stopPropagation();
                document.removeEventListener('mousemove',onmousemove);
                document.removeEventListener('mouseup',onmouseup);
            }
            document.addEventListener('mousemove',onmousemove);
            document.addEventListener('mouseup',onmouseup);
        }
    }

    makeScrollable(){
        this.eventEl.onwheel = (e) => {
            e.stopPropagation();
            let startMouseLocal = this.worldToLocal({x: e.clientX, y: e.clientY});
            this.scale *= Math.exp(-0.001*e.deltaY);
            this.updateUI();
            let mouseLocal = this.worldToLocal({x: e.clientX, y: e.clientY});
            this.translation = {
                x: this.translation.x + (mouseLocal.x - startMouseLocal.x)*this.scale,
                y: this.translation.y + (mouseLocal.y - startMouseLocal.y)*this.scale
            }
            mouseLocal = this.worldToLocal({x: e.clientX, y: e.clientY});
        }
    }

    public translate(translation: {x: number, y: number}){  
        this.translation = {
            x: this.translation.x + translation.x,
            y: this.translation.y + translation.y
        }
        this.updateUI();
    }

    public scaleBy(scale: number){
        this.scale *= scale;
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

    public getAbsoluteOrigin(){
        this.updateUI();
        let rect = this.targetElement.getBoundingClientRect()
        // print('origin',{
        //     'x':rect.x + rect.width*this.pivot.x,
        //     'y':rect.y + rect.height*this.pivot.y
        // })
        return {
            'x':rect.x + rect.width*this.pivot.x,
            'y':rect.y + rect.height*this.pivot.y
        };
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

    public worldToLocal(pos: {x: number, y: number}){
        let absOrigin = this.getAbsoluteOrigin();
        let absScale = this.getAbsoluteScale();
        return {
            x: (pos.x - absOrigin.x)/absScale.x,
            y: (pos.y - absOrigin.y)/absScale.y
        }
    }

    public localToWorld(pos: {x: number, y: number}){
        let absOrigin = this.getAbsoluteOrigin();
        let absScale = this.getAbsoluteScale();
        return {
            x: pos.x*absScale.x + absOrigin.x,
            y: pos.y*absScale.y + absOrigin.y
        }
    }
}
