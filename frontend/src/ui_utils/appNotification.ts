import { Componentable } from "../component/componentable"
import { Workspace } from "../sobjects/workspace"
import { as } from "../utils"

enum ClientMsgTypes{
    STATUS='status',
    NOTIFICATION='notification'
}

type Message = {
    message:string,
    type:ClientMsgTypes
}

/**
 * Notifications at bottom right coner of the screen
 */
export class AppNotification extends Componentable{
    protected get template(): string {
        return `
        <div class="cont" id="slot_default"></div>
        `
    }
    protected get style(): string {
        return`
        .cont{
            position:absolute;
            display:flex;
            flex-direction:column-reverse;
            right:10px;
            bottom:10px;
            gap:10px;
            z-index: 20;
        }
        `
    }
    constructor(){
        super()
        this.htmlItem.setParentElement(document.body)
        Workspace.instance.objectsync.on(`status_message`, (msg:Message)=>{
            if(msg.type==ClientMsgTypes.NOTIFICATION)
                this.add(msg.message);
        });
        Workspace.instance.objectsync.on(`status_message_${Workspace.instance.objectsync.clientId}`, (msg:Message)=>{
            if(msg.type==ClientMsgTypes.NOTIFICATION)
                this.add(msg.message);
        });
    }

    public add(content:string,sustain = 2000,decay = 1000){
        const item = new AppNotificationItem(content,sustain,decay)
        item.htmlItem.setParent(this.htmlItem)
    }

}

class AppNotificationItem extends Componentable{
    protected get template(): string {
        return `
        <div class="item"></div>
        `
    }
    protected get style(): string {
        return `
        .item{
            min-height: 100px;
            width: 350px;
            background: var(--z2);
            border: var(--success) solid 1px;
            border-radius: 8px;
            padding: 10px;
            }
        }
        `
    }
    private startTime = Date.now()

    private base: HTMLDivElement
    private underMouse = false
    constructor(content:string,private sustain = 2000,private decay = 1000){
        super()
        this.htmlItem.baseElement.innerHTML = content
        this.link2(this.htmlItem.baseElement,'mouseenter',this.mouseenter)
        this.link2(this.htmlItem.baseElement,'mouseleave',this.mouseleave)
        window.requestAnimationFrame(this.animate.bind(this))
        this.base = as(this.htmlItem.baseElement,HTMLDivElement)
    }

    private mouseenter(){
        this.underMouse = true
    }

    private mouseleave(){
        this.underMouse = false
    }

    private animate(){
        if(this.underMouse){
            this.startTime = Date.now()
        }
        const dt = Date.now() - this.startTime
        if(dt>this.sustain + this.decay){
            this.destroy()
            return
        }
        if(dt>this.sustain){
            this.base.style.opacity = 1-(dt-this.sustain)/this.decay + ''
        }
        else{
            this.base.style.opacity = '1'
        }

        requestAnimationFrame(this.animate.bind(this))
    }
}
