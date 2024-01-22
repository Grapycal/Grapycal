import { Componentable } from "../../component/componentable"
import { GlobalEventDispatcher } from "../../component/eventDispatcher"
import { print } from "../../devUtils"

export class PopupMenu extends Componentable{
    /**
     * The base class of simplePopupMenu
     */
    
    private base: HTMLElement
    private optionTemplate: HTMLTemplateElement
    protected opened:boolean = false
    private optionElements: HTMLElement[] = []
    private focusedOption: number = 0
    hideWhenClosed: boolean

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
            display: none;
            border-radius: 2px;
            overflow:hidden;
            z-index: 100;
        }
        .option{ 
            cursor: pointer;
        }
        .option.focused{
            background-color: var(--t1);
        }
        `
    }

    constructor(){
        super()
        this.htmlItem.setParentElement(document.body)
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

    protected addOptionElement(el:HTMLElement,onclick:()=>void){
        el.classList.add(this.constructor.name+'-option')
        el.addEventListener('click',(e)=>{
            this.close()
            onclick()
            e.stopPropagation()
        })
        this.optionTemplate.parentNode.appendChild(el)
        this.optionElements.push(el)
        if(this.optionElements.length == 1){
            this.focusOptionChange(0,0)
        }
    }

    protected generateOptionElement():HTMLElement{
        let option = this.optionTemplate.content.firstElementChild.cloneNode(true) as HTMLElement
        return option
    }

    public addOption(text:string,onclick:()=>void){
        let option = this.generateOptionElement()
        option.innerText = text
        this.addOptionElement(option,onclick)
        return option
    }

    openAt(x:number,y:number){
        this.base.style.left = x+'px'
        this.base.style.top = y+'px'
        this.base.style.display = 'block'
        this.base.style.position = 'absolute'
        this.opened = true

        this.link(GlobalEventDispatcher.instance.onMouseDown,this.onElsewhereClick)
    }

    open(){
        this.base.style.display = 'block'
        this.base.style.position = 'relative'
        this.opened = true

        this.link(GlobalEventDispatcher.instance.onMouseDown,this.onElsewhereClick)
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

    private onEnter(e:KeyboardEvent){
        if(!this.opened) return
        if(this.optionElements[this.focusedOption] === undefined) return
        this.optionElements[this.focusedOption].click()
        e.stopPropagation()
    }

    private focusOptionChange(from:number, to:number){
        this.optionElements[from].classList.remove(this.constructor.name+'-focused')
        this.optionElements[to].classList.add(this.constructor.name+'-focused')
    }

    close(){
        if(this.hideWhenClosed){
            this.base.style.display = 'none'
        }
        this.opened = false
        this.clearOptions()
        
        this.unlink(GlobalEventDispatcher.instance.onMouseDown)
    }

    clearOptions(){
        for(let option of this.optionElements){
            option.remove()
        }
        this.optionElements = []
        this.focusedOption = 0
    }
}