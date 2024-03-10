import { StringTopic } from "objectsync-client"
import { Control } from "./control"
import { print } from "../../devUtils"
import { as, getImageFromClipboard } from "../../utils"
import { Workspace } from "../workspace"


export class ImageControl extends Control {
    
    protected template = `
    <div class="control" tabindex=0>
        <img class="control-image full-height full-width" id="image">
    </div>
    `

    protected css = `
    .focused{
        outline: 1px solid #ffffff;
    }
    .control{
        background: #eee url('data:image/svg+xml,\
           <svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"         fill-opacity=".25" >\
                    <rect x="200" width="200" height="200" />\
                    <rect y="200" width="200" height="200" />\
                    </svg>');
        background-size: 20px 20px;
    }
    `

    protected onStart(): void {
        super.onStart()
        let base = as(this.htmlItem.baseElement, HTMLDivElement)
        let image = this.htmlItem.getEl("image", HTMLImageElement)
        let imageTopic = this.getAttribute("image", StringTopic)
        this.link(imageTopic.onSet, (newValue) => {
            // set the image data (jpg)
            image.src = "data:image/jpg;base64," + newValue
            this.node.moved.invoke()
        })

        base.onfocus = () => {
            base.classList.add("ImageControl-focused")
            this.link2(document, "paste", this.onPaste)
        }
        base.onblur = () => {
            base.classList.remove("ImageControl-focused")
            this.unlink2(document, "paste")
        }


    }


    onPaste(e: ClipboardEvent) {
        getImageFromClipboard(e, (base64String) => {
            // we message must < 4MB
            // but we will limit it to 2MB because change of StringTopic also sends old value
            if (base64String.length > 2000000) {
                Workspace.instance.appNotif.add("Image is too large. Max size is 2MB")
                return
            }
            let imageTopic = this.getAttribute("image", StringTopic)
            imageTopic.set(base64String)
        })
    }

}