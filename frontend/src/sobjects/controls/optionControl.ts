import { IntTopic, ListTopic, StringTopic } from "objectsync-client"
import { Control } from "./control"
import { print } from "../../devUtils"
import { AutoCompMenu, OptionInfo } from "../../ui_utils/popupMenu/autoCompMenu"


export class OptionControl extends Control {
    
    menu = new AutoCompMenu()
    value = this.getAttribute('value',StringTopic)
    options = this.getAttribute('options',ListTopic<string>)
    label = this.getAttribute('label',StringTopic)
    private locked = false

    protected template = `
    <div class="control flex-horiz">
        <div class="label" id="label">Text</div>
        <div id="slot_menu"></div>
    </div>
    `

    protected css: string = `
        .label{
            flex-shrink: 0;
            min-width: 20px;
        }
    `

    protected onStart(): void {
        super.onStart()
        this.menu.htmlItem.setParent(this.htmlItem,'menu')
        this.menu.show()
        const optionInfos: OptionInfo[] = []
        this.link(this.options.onSet,()=>{
            for(let o of this.options.getValue()){
                optionInfos.push({
                    key:o,value:o,callback:()=>{this.select(o)}
                })
            }
            this.menu.setOptions(optionInfos)
        })
        let labelEl = this.htmlItem.getEl("label", HTMLDivElement)
        this.link(this.label.onSet, (label) => {
            if (label == '') {
                labelEl.style.display = 'none'
                return
            }
            //replace spaces with non-breaking spaces
            label = label.replace(/ /g, "\u00a0")

            labelEl.innerHTML = label
        })
        this.link(this.value.onSet,(v)=>this.menu.value = v)
    }

    private select(value:string){
        if(this.value.getValue() == value) return
        this.locked = true;
        this.value.set(value)
        this.locked = false;
    }

}