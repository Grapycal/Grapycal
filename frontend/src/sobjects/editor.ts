import { ObjectSyncClient } from "objectsync-client"
import { ComponentManager } from "../component/component"
import { EventDispatcher as EventDispatcher } from "../component/eventDispatcher"
import { HtmlItem } from "../component/htmlItem"
import { MouseOverDetector } from "../component/mouseOverDetector"
import { Transform } from "../component/transform"
import { CompSObject } from "./compSObject"
import { Linker } from "../component/linker"
import { Port } from "./port"
import { print } from "../devUtils"

export class Editor extends CompSObject{
    readonly template: string = `
    <div style="width:100%;height:100%">
        <div class="viewport" id="Viewport" style="width:100%;height:100%;position:absolute;top:0;left:0;">
            <div style="position:absolute;top:50%;left:50%">
                
                <div id="slot_default" class="editor" style="position:absolute;top:50%;left:50%;width:1px;height:1px;">
                <svg class="bg" id="bg"
                    <defs>
                        <pattern id="smallGrid" width="8" height="8" patternUnits="userSpaceOnUse">
                            <path d="M 8 0 L 0 0 0 8" fill="none" stroke="#444444" stroke-width="0.5" />
                        </pattern>
                        <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
                            <rect width="80" height="80" fill="url(#smallGrid)" />
                            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="#444444" stroke-width="1" />
                        </pattern>
                    </defs>

                    <rect width="100%" height="100%" fill="url(#grid)" />
                    
                </svg>
                </div>
            </div>
            
        </div>

    </div>
    `;

    componentManager = new ComponentManager();
    linker = new Linker(this);
    eventDispatcher: EventDispatcher;
    htmlItem: HtmlItem;
    transform: Transform;
    
    constructor(objectsync: ObjectSyncClient, id: string){
        super(objectsync,id);
        this.htmlItem = new HtmlItem(this, document.body);
        this.htmlItem.applyTemplate(this.template);
        let viewport = this.htmlItem.getHtmlEl('Viewport')
        let editor = this.htmlItem.getHtmlEl('slot_default')
        
        this.transform = new Transform(this,editor,viewport);

        this.eventDispatcher = new EventDispatcher(this, viewport);
        this.linker.link(this.eventDispatcher.onMoveGlobal,this.mouseMove)
        new MouseOverDetector(this, viewport);
        
        this.transform.scale = 1
        this.transform.maxScale = 8
        this.transform.minScale = 0.4
        this.transform.draggable = true;
        this.transform.scrollable = true;

    }

    private mouseMove(e: MouseEvent){
        // If there's performance issues, maybe optimize this
        for(let port of this.TopDownSearch(Port)){
            let dist = port.htmlItem.position.distanceTo(this.eventDispatcher.mousePos)
            if(dist < 200){
                port.htmlItem.baseElement.classList.add('port-near-mouse-1')
                port.htmlItem.baseElement.classList.remove('port-near-mouse-2')
            }else if (dist < 400){
                port.htmlItem.baseElement.classList.add('port-near-mouse-2')
                port.htmlItem.baseElement.classList.remove('port-near-mouse-1')
            }
            else{
                port.htmlItem.baseElement.classList.remove('port-near-mouse-1')
                port.htmlItem.baseElement.classList.remove('port-near-mouse-2')
            }
        }
    }
    
    public createEdge(tailId: string, headId: string): void{
        this.makeRequest('create_edge',{tail_id:tailId,head_id:headId})
    }
}