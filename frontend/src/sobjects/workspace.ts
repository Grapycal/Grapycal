import { ObjectSyncClient, ObjectTopic } from "objectsync-client"
import { CompSObject } from "./compSObject";
import { Port } from "./port"
import { EventDispatcher } from "../component/eventDispatcher"
import { Editor } from "./editor"
import { print } from "../devUtils"

export class Workspace extends CompSObject{
    public static instance: Workspace
    main_editor = this.getAttribute('main_editor', ObjectTopic<Editor>)
    eventDispatcher = new EventDispatcher(this, document.getElementById('workspace'))
    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)
        Workspace.instance = this
    }
}