import { ObjectSyncClient } from "objectsync-client"
import { Vector2 } from "../../utils"
import { Node } from "../node"

export class TextOutputNode extends Node{
    protected readonly templates: {[key: string]: string} = {
    block: 
    `<div class="Node BlockNode flex-horiz space-between">
        <div id="slot_input_port" class="no-width flex-vert space-evenly"></div>
        <div class="NodeContent full-width flex-vert space-evenly"> 
            <div id="label" class="center" ></div>
        </div>
        <div id="slot_output_port" class="no-width flex-vert space-evenly"></div>
    </div>`
    }
    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)
        this.onStart.add(()=>{
            this.transform.pivot = new Vector2(0,0.5)
        })
    }
}