import { DictTopic, EventTopic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { EventDispatcher } from "../component/eventDispatcher"
import { print } from "../devUtils"
import { Workspace } from "../sobjects/workspace"
import { Vector2, textToHtml } from "../utils"
import { LIB_VERSION } from '../version';

enum ClientMsgTypes{
    STATUS='status',
    NOTIFICATION='notification'
}

type Message = {
    message:string,
    type:ClientMsgTypes
}

export class Footer extends Componentable{
    static ins: Footer
    static setStatus(status: string){
        Footer.ins.setStatus(status);
    }
    protected get template(): string{
        return `
            <div class="footer">
            <div id="extend-area"></div>
            <div id="bar">
                <span id="workspace-name"></span>
                <span id="status"></span>
                <span class="float-left version">Grapycal v${LIB_VERSION}</span>
            </div>
            </div>
            `;
        }

    protected get style(): string{
        return `
        
            #bar{
                white-space: nowrap;
                position: relative;
                padding: 0 30px;
                display: flex;
                align-items: center;
                bottom: 0;
                height: 24px;
                gap: 50px;
                user-select: none;
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
                cursor: ns-resize;
            }
            .float-left{
                margin-left: auto;
            }
            #status{
                overflow: hidden;
            }
            #extend-area{
                overflow: auto;
                position: relative;
                bottom: 0;
                top: 0;
                height: 0;
                background-color: var(--z0);
                flex-shrink: 1;
                padding: 0 30px;
            }
            #version{
                flex-shrink: 0;
            }
            `;
        }

    workspaceName: HTMLSpanElement
    status: HTMLSpanElement
    bar: HTMLDivElement
    extendArea: HTMLDivElement
    eventDispatcher: EventDispatcher = new EventDispatcher(this);
    displacement: number = 0;
    constructor(){
        super();
        Footer.ins = this;
        this.htmlItem.setParentElement(document.body.getElementsByTagName('footer')[0]);
        this.workspaceName = this.htmlItem.getEl('workspace-name', HTMLSpanElement);
        this.status = this.htmlItem.getEl('status', HTMLSpanElement);
        this.bar = this.htmlItem.getEl('bar', HTMLDivElement);
        this.extendArea = this.htmlItem.getEl('extend-area', HTMLDivElement);

        this.status.innerHTML = 'Loading workspace...';

        this.workspaceName.innerHTML = 'workspace.grapycal';

        this.link(this.eventDispatcher.onDrag,this.onDrag);
        this.link(this.eventDispatcher.onDragEnd,this.onDragEnd)
        ;
        Workspace.instance.objectsync.on(`status_message`, (msg:Message)=>{
            if(msg.type==ClientMsgTypes.STATUS)
                this.setStatus(msg.message);
        });
        Workspace.instance.objectsync.on(`status_message_${Workspace.instance.objectsync.clientId}`, (msg:Message)=>{
            if(msg.type==ClientMsgTypes.STATUS)
                this.setStatus(msg.message);
        });
        Workspace.instance.objectsync.getTopic('meta',DictTopic<string,any>).onSet.add((value)=>{
            this.workspaceName.innerHTML = value.get('workspace name');
            // title
            let fileName = value.get('workspace name').split('/').pop().split('.')[0];
            document.title = `${fileName} - Grapycal`;
        })
        
    }

    setStatus(status: string){
        this.status.innerHTML = status;
        const p = document.createElement('p');
        p.innerHTML = textToHtml(status);
        this.extendArea.append(p);
    }

    onDrag(event: DragEvent, from:Vector2, to:Vector2){
        this.displacement += to.y - from.y;
        let realDisplacement = Math.max(0, this.displacement);
        realDisplacement = Math.min(realDisplacement, 400);
        this.extendArea.style.height = `${realDisplacement}px`;
    }

    onDragEnd(event: DragEvent){
        let realDisplacement = Math.max(0, this.displacement);
        realDisplacement = Math.min(realDisplacement, 400);
        this.displacement = realDisplacement;
        
    }
}