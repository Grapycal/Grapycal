import { Componentable } from "../component/componentable"
import { Workspace } from "../sobjects/workspace"
import { as } from "../utils"

export class ControlPanel extends Componentable{
    protected get template(): string {
        return `
        <div class="cont" id="slot_default">
            <button id="run">run</button>
            <button id="interrupt">interrupt</button>
        </div>
        `
    }
    protected get style(): string {
        return`
        .cont{
            position:absolute;
            display:flex;
            flex-direction:row;
            bottom: 40px;
            margin: 0 auto;
            background-color: var(--z2);
            opacity:0.5;
            height: 30px;
            z-index:15;
            left: 50%;
            transform: translate(-50%,-50%);
            border-radius: 10px;
            transition: 0.2s;
        }
        .cont:hover{
            opacity:1;
        }
        `
    }
    constructor(){
        super()
        this.htmlItem.setParentElement(document.body);
        this.link2(this.htmlItem.getEl("interrupt"),'click',()=>{
            Workspace.instance.objectsync.makeRequest('interrupt')
        })
    }
}