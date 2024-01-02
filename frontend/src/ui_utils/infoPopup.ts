import { Componentable } from "../component/componentable"
import { Transform } from "../component/transform"
import { Node } from "../sobjects/node"
import { Vector2 } from "../utils"

export class InfoPopup extends Componentable{
    protected get template(): string {
        return `
            <div class="base">
                <div class="message"></div>
                <svg width="20px" height="20px" style="position: absolute; bottom: -20px; left: -20px;">
                    <line x1="20" y1="0" x2="0" y2="20" />
                </svg>
            </div>
        `
    }
    protected get style():string{
        return `
            .base{
                background-color: var(--z2);
                position: absolute;
                flex-direction: column;
                justify-content: center;
                z-index: 1000;
                border: 1px solid var(--z3);
                border-radius: 4px;
                padding: 10px;
                width: 300px;
                height: 200px;
                overflow: auto;
            }
            .message{
                max-width: 400px;
                max-height: 200px;
                overflow-y: auto;
                padding: 5px;
                overflow-wrap: break-word;
            }
        `
    }
    baseDiv: HTMLDivElement
    transform: Transform
    private _mouseOver: boolean = false
    get mouseOver(): boolean {return this._mouseOver}

    constructor() {
        super()
        this.baseDiv = this.htmlItem.baseElement as HTMLDivElement
        this.htmlItem.setParentElement(document.body)
        this.transform = new Transform(this)

        this.hide()

        this.transform.pivot = new Vector2(0.,1)
        this.baseDiv.addEventListener("wheel",(e)=>{
            //if scrollable, stop propagation
            if(this.baseDiv.scrollHeight > this.baseDiv.clientHeight){
                e.stopPropagation()
            }
        })
        this.link2(this.baseDiv,'mouseenter',()=>{this._mouseOver = true})
        this.link2(this.baseDiv,'mouseleave',()=>{this._mouseOver = false})
    }

    show(){
        this.baseDiv.style.display = "block"
    }

    hide(){
        this.baseDiv.style.display = "none"
    }
}