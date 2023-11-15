import { Componentable } from "../component/componentable"
import { GlobalEventDispatcher } from "../component/eventDispatcher"
import { print } from "../devUtils"

export class PopupMenu extends Componentable{
    static _instance:PopupMenu
    static get instance(){
        if(!this._instance){
            this._instance = new PopupMenu()
        }
        return this._instance
    }
    private base: HTMLElement
    private optionTemplate: HTMLTemplateElement
    protected opened:boolean = false
    private optionElements: HTMLElement[] = []
    private focusedOption: number = 0

    get template():string{
        return `
        <div class="base">
            <template id="option-template">
                <div class="option">
                </div>
            </template>
        </div>
        `
    }

    get style():string{
        return `
        .base{
            position: absolute;
            display: none;
            background-color: var(--z2);
            border: 1px solid var(--text-low);
            border-radius: 2px;
            box-shadow: 0px 0px 5px 0px black;
            z-index: 100;
        }
        .option{ 
            cursor: pointer;
            padding: 5px;
        }
        .option.focused{
            background-color: var(--t1);
        }
        `
    }

    constructor(){
        super()
        this.htmlItem.setParentElement(document.body)
        this.link(GlobalEventDispatcher.instance.onMouseDown,this.onElsewhereClick)
        this.base = this.htmlItem.baseElement as HTMLElement
        this.optionTemplate = this.htmlItem.getHtmlEl('option-template') as HTMLTemplateElement
        
        this.link(GlobalEventDispatcher.instance.onKeyDown.slice('ArrowDown'),this.onArrowDown)
        this.link(GlobalEventDispatcher.instance.onKeyDown.slice('ArrowUp'),this.onArrowUp)
        this.link(GlobalEventDispatcher.instance.onKeyDown.slice('Enter'),this.onEnter)
    }

    onElsewhereClick(e:MouseEvent){
        if(!this.base.contains(e.target as Node)){
            this.close()
        }
    }

    protected generateOptionElement():HTMLElement{
        let option = this.optionTemplate.content.firstElementChild.cloneNode(true) as HTMLElement
        return option
    }

    protected addOptionElement(el:HTMLElement,onclick:()=>void){
        el.classList.add(this.constructor.name+'-option')
        el.addEventListener('click',()=>{
            this.close()
            onclick()
        })
        this.base.appendChild(el)
        this.optionElements.push(el)
        if(this.optionElements.length == 1){
            this.focusOptionChange(0,0)
        }
    }

    open(x:number,y:number){
        this.base.style.left = x+'px'
        this.base.style.top = y+'px'
        this.base.style.display = 'block'
        this.opened = true
    }

    private onArrowDown(e:KeyboardEvent){
        if(!this.opened) return
        e.preventDefault()
        if (this.focusedOption == this.optionElements.length-1){
            return
        }
        if (this.focusedOption < this.optionElements.length-1){
            this.focusedOption++

            this.focusOptionChange(this.focusedOption-1,this.focusedOption)
        }
    }

    private onArrowUp(e:KeyboardEvent){
        if(!this.opened) return
        e.preventDefault()
        if (this.focusedOption > 0){
            this.focusedOption--
            this.focusOptionChange(this.focusedOption+1,this.focusedOption)
        }
    }

    private onEnter(){
        if(!this.opened) return
        if(this.optionElements[this.focusedOption] === undefined) return
        this.optionElements[this.focusedOption].click()
    }

    private focusOptionChange(from:number, to:number){
        this.optionElements[from].classList.remove(this.constructor.name+'-focused')
        this.optionElements[to].classList.add(this.constructor.name+'-focused')
    }

    close(){
        this.base.style.display = 'none'
        this.opened = false
        this.clearOptions()
    }

    clearOptions(){
        for(let option of this.optionElements){
            option.remove()
        }
        this.optionElements = []
        this.focusedOption = 0
    }
}