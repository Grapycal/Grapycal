import { ComponentManager, IComponentable } from "../component/component"
import { HtmlItem } from "../component/htmlItem"
import { Transform } from "../component/transform"

export class Editor implements IComponentable{
    template: string = `
    <div class="Viewport" id="Viewport" style="width:100%;height:100%;position:absolute;top:0;left:0;">
        <div style="position:absolute;top:50%;left:50%">
            <div id="slot_default" class="Editor" style="position:absolute;top:50%;left:50%;width:1px;height:1px;">
            </div>
        </div>
    </div>
    `;

    componentManager = new ComponentManager();
    htmlItem: HtmlItem;
    transform: Transform;
    
    constructor(){
        this.htmlItem = new HtmlItem(this, document.body);
        this.htmlItem.applyTemplate(this.template);
        let viewport = this.htmlItem.getById('Viewport')
        let editor = this.htmlItem.getById('slot_default')
        this.transform = new Transform(this,editor,viewport);

        document.body.appendChild(viewport);
        
        this.transform.makeDraggable();
    }
}