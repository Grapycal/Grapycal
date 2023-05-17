import { Null, print } from "../devUtils"
import { Component, IComponentable } from "./component"
import { HtmlHierarchyItem } from "./htmlHierarchyItem"

export class TransformRoot extends Component{
    scale: number = 1;
    translation: {x: number, y: number} = {x: 0, y: 0};
    pivot: {x: number, y: number} = {x: 0.5, y: 0.5};
}

// Dependency: HtmlHierarchyItem
export class Transform extends Component{
    htmlHierarchyItem: HtmlHierarchyItem = Null();
    parent: Transform | TransformRoot = Null();
    baseElement: HTMLElement = Null();
    eventEl: HTMLElement = Null();
    _pivot: {x: number, y: number} = {x: 0.5, y: 0.5};
    _scale: number = 1;
    _translation: {x: number, y: number} = {x: 0, y: 0};

    get pivot(){return this._pivot;}
    set pivot(pivot: {x: number, y: number}){
        this._pivot = pivot;
        this.baseElement.style.transformOrigin = `${pivot.x*100}% ${pivot.y*100}%`;
        this.updateUI();
    }
    
    get scale(){return this._scale;}
    set scale(scale: number){
        this._scale = scale;
        this.updateUI();
    }
    
    get translation(){return this._translation;}
    set translation(translation: {x: number, y: number}){
        this._translation = translation;
        this.updateUI();
    }
    
    constructor(object:IComponentable, eventEl?: HTMLElement){
        super(object);
        this.htmlHierarchyItem = this.getComponent(HtmlHierarchyItem);
        this.baseElement = this.getComponent(HtmlHierarchyItem).baseElement;
        this.eventEl = eventEl || this.baseElement;
        this.updateUI();
    }

    // strategy: fix mouse local position
    makeDraggable(){
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
            //print(mouseLocal)
        }
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


    private updateParent(){
        this.parent = this.htmlHierarchyItem.findTransformParent() || new TransformRoot(this.object);
    }

    private updateUI(){
        this.updateParent();
        let transformString = ''
        //if(this.parent !== null)
            //transformString += `translate(${this.parent.pivot.x*-100}%,${this.parent.pivot.y*-100}%)`
        transformString += `translate(${this.pivot.x*-100}%,${this.pivot.y*-100}%)`
        transformString += `translate(${this._translation.x}px,${this._translation.y}px)`;
        transformString += `scale(${this._scale})`
        this.baseElement.style.transform = transformString;
    }

    public getAbsoluteOrigin(){
        this.updateUI();
        let rect = this.baseElement.getBoundingClientRect()
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
        let rect = this.baseElement.getBoundingClientRect()
        return {
            'x':rect.width/this.baseElement.offsetWidth,
            'y':rect.height/this.baseElement.offsetHeight
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
