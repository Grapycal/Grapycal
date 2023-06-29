import { ObjectSyncClient } from "objectsync-client"
import { ComponentManager, IComponentable } from "../component/component"
import { EventDispatcher as EventDispatcher } from "../component/eventDispatcher"
import { HtmlItem } from "../component/htmlItem"
import { MouseOverDetector } from "../component/mouseOverDetector"
import { Transform } from "../component/transform"
import { CompSObject } from "./compSObject"

export class Editor extends CompSObject{
    readonly template: string = `
    <div style="width:100%;height:100%">
        <div class="viewport" id="Viewport" style="width:100%;height:100%;position:absolute;top:0;left:0;">
            <div style="position:absolute;top:50%;left:50%">
                
                <div id="slot_default" class="editor" style="position:absolute;top:50%;left:50%;width:1px;height:1px;">
                <div class="bg" id="bg"></div>
                </div>
            </div>
        </div>
        <div class="vignette"></div>

        <div class="sidebar-container">
            <div class="sidebar-slot" id="slot_sidebar"></div>
            <div class="settings-button" id="settings-button">
                Settings
            </div>
        </div>
    </div>
    `;

    componentManager = new ComponentManager();
    htmlItem: HtmlItem;
    transform: Transform;
    
    constructor(objectsync: ObjectSyncClient, id: string){
        super(objectsync,id);
        this.htmlItem = new HtmlItem(this, document.body);
        this.htmlItem.applyTemplate(this.template);
        let viewport = this.htmlItem.getHtmlEl('Viewport')
        let editor = this.htmlItem.getHtmlEl('slot_default')
        
        this.transform = new Transform(this,editor,viewport);

        new EventDispatcher(this, viewport);
        new MouseOverDetector(this, viewport);
        
        this.transform.scale = 1.3
        this.transform.draggable = true;
        this.transform.scrollable = true;

        this.htmlItem.getHtmlEl('settings-button').addEventListener('click',()=>{
            document.getElementById('settings-page').classList.toggle('open')
        })
    }
}