import { print } from "../devUtils"
import { PopupMenu } from "./popupMenu"

export class SimplePopupMenu extends PopupMenu{
    static _instance:SimplePopupMenu
        static get instance(){
            if(!this._instance){
                this._instance = new SimplePopupMenu()
            }
            return this._instance
        }
    public addOption(text:string,onclick:()=>void){
        let option = this.generateOptionElement()
        option.innerText = text
        this.addOptionElement(option,onclick)
    }
}