import { StringTopic, Topic } from "objectsync-client"
import { ComponentManager, IComponentable } from "../component/component"
import { HtmlItem } from "../component/htmlItem"
import { as } from "../utils"
import { Linker } from "../component/linker"
import { Workspace } from "../sobjects/workspace"
import { BindInputBoxAndTopic, inputFinished } from "../ui_utils/interaction"

export class TextEditor implements IComponentable {
    readonly template: string = `
    <div class="attribute-editor flex-horiz stretch">
        <div id="attribute-name"></div>
        <input id="input" type="text" class="text-editor">
    </div>
    `;

    readonly componentManager = new ComponentManager();
    readonly htmlItem: HtmlItem
    readonly input: HTMLInputElement
    readonly linker = new Linker(this);
    readonly connectedAttributes: StringTopic[]
    private locked = false;

    constructor(displayName: string, editorArgs: any, connectedAttributes: StringTopic[]) {
        this.connectedAttributes = connectedAttributes
        this.htmlItem = new HtmlItem(this)
        this.htmlItem.applyTemplate(this.template)
        this.input = as(this.htmlItem.getHtmlEl('input'), HTMLInputElement)
        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName
        new BindInputBoxAndTopic(this,this.input, this.connectedAttributes,Workspace.instance.objectsync)
    }

}
