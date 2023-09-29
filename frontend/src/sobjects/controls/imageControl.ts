import { StringTopic } from "objectsync-client"
import { Control } from "./control"
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

        //paste image from clipboard
        document.addEventListener('paste', (e) => {
            let items = e.clipboardData.items
            if (items) {
                for (let item of items) {
                    if (item.type.indexOf("image") !== -1) {
                        print(item)
                        let blob = item.getAsFile()
                        let reader = new FileReader()
                        reader.onload = (event) => {
                            let imageTopic = this.getAttribute("image", StringTopic)
                            print(reader.result)
                            let buf = reader.result as ArrayBuffer
                            var base64String = btoa(String.fromCharCode.apply(null, new Uint8Array(buf) as any as number[]));
                            
                            imageTopic.set(base64String)
                        }
                        reader.readAsArrayBuffer(blob)
                    }
                }
            }
        })
    }

}