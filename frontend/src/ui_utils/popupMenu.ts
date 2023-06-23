import { print } from "../devUtils"

export class PopupMenu{
    static _instance:PopupMenu
    static get instance(){
        if(!this._instance){
            this._instance = new PopupMenu(0,0)
        }
        return this._instance
    }
    private popup: HTMLElement

    constructor(x:number,y:number){
        let popup = document.createElement('div')
        popup.classList.add('popup')
        popup.style.left = x+'px'
        popup.style.top = y+'px'
        document.body.appendChild(popup)
        this.popup = popup
        this.onElsewhereClick = this.onElsewhereClick.bind(this)
        document.addEventListener('mousedown',this.onElsewhereClick)
    }

    onElsewhereClick(e:MouseEvent){
        if(!this.popup.contains(e.target as Node)){
            this.close()
        }
    }

    addOption(text:string,onclick:()=>void){
        let option = document.createElement('div')
        option.classList.add('popup-option')
        option.innerText = text
        option.addEventListener('click',()=>{
            this.close()
            onclick()
        })
        this.popup.appendChild(option)
    }
    reset(x:number,y:number):PopupMenu{
        this.popup.style.left = x+'px'
        this.popup.style.top = y+'px'
        this.popup.style.display = 'block'
        //remove all children
        while(this.popup.firstChild){
            this.popup.removeChild(this.popup.firstChild)
        }
        return this
    }

    close(){
        if(PopupMenu.instance != this){
            this.remove()
            return
        }
        while(this.popup.firstChild){
            this.popup.removeChild(this.popup.firstChild)
        }
        this.popup.style.display = 'none'
    }

    remove(){
        document.body.removeChild(this.popup)
        document.removeEventListener('mousedown',this.onElsewhereClick)
    }
}

/*
css:
.popup{
    position:absolute;
    width:200px;
}
.popup-option{
    padding:10px;
    cursor:pointer;
}
*/