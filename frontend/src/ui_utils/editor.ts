import { ComponentManager, IComponentable } from "../component/component"
import { HtmlHierarchyItem } from "../component/htmlHierarchyItem"
import { Transform } from "../component/transform"

export class Editor implements IComponentable{
    viewport: HTMLElement = document.createElement('div');
    editor: HTMLElement = document.createElement('div');
    transformBase: HTMLElement = document.createElement('div');

    componentManager = new ComponentManager();
    htmlHierarchyItem: HtmlHierarchyItem = new HtmlHierarchyItem(this,this.editor,this.editor);
    transform: Transform = new Transform(this,this.viewport);
    
    constructor(){
        this.viewport.classList.add('Viewport');
        this.editor.classList.add('Editor');
        this.editor.id = 'Editor';
        document.body.appendChild(this.viewport);
        this.viewport.appendChild(this.transformBase)
        this.transformBase.appendChild(this.editor);
        this.transformBase.style.position = 'absolute';
        this.transformBase.style.top = '50%';
        this.transformBase.style.left = '50%';
        this.transformBase.style.width = '1px';
        this.transformBase.style.height = '1px';
        this.transform.makeDraggable();
    }
}