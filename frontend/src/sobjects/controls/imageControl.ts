import { StringTopic } from "objectsync-client"
import { Control } from "./control"
import { print } from "../../devUtils"
import { as } from "../../utils"
import { Buffer } from 'buffer';


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
        let items = e.clipboardData.items
        if (items) {
            for (let item of items) {
                if (item.type.indexOf("image") !== -1) {
                    let blob = item.getAsFile()
                    let reader = new FileReader()
                    reader.onload = (event) => {
                        let imageTopic = this.getAttribute("image", StringTopic)
                        let buf =Buffer.from( reader.result as ArrayBuffer)
                        var base64String = buf.toString('base64')
                        
                        imageTopic.set(base64String)
                    }
                    reader.readAsArrayBuffer(blob)
                }
            }
        }
    }

}