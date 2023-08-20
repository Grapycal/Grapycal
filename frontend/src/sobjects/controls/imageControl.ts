import { StringTopic } from "objectsync-client"
import { Control } from "./control";
import { HtmlItem } from "../../component/htmlItem"
import { print } from "../../devUtils"

export class ImageControl extends Control {
    
    protected template = `
    <div class="control">
        <img class="control-image full-height full-width" id="image">
    </div>
    `

    protected onStart(): void {
        super.onStart()
        let image = this.htmlitem.getEl("image", HTMLImageElement)
        let imageTopic = this.getAttribute("image", StringTopic)
        this.link(imageTopic.onSet, (newValue) => {
            // set the image data (jpg)
            image.src = "data:image/jpg;base64," + newValue
            this.node.moved.invoke()
        })
    }

}