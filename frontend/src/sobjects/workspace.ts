import { ObjectSyncClient, ObjectTopic } from "objectsync-client"
import { CompSObject } from "./compSObject";
import { EventDispatcher, GlobalEventDispatcher } from "../component/eventDispatcher"
import { Editor } from "./editor"
import { SelectionManager } from "../component/selectionManager"

export class Workspace extends CompSObject{
    public static instance: Workspace
    readonly main_editor = this.getAttribute('main_editor', ObjectTopic<Editor>)
    readonly eventDispatcher = new EventDispatcher(this, document.getElementById('workspace'))
    readonly selection = new SelectionManager(this)
    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)
        Workspace.instance = this
        document.getElementById('settings-button').addEventListener('click',()=>{
            document.getElementById('settings-page').classList.toggle('open')
            objectsync.emit('refresh_extensions')
        })
    }
    protected onStart(): void {
        this.main_editor.getValue().eventDispatcher.onClick.add(()=>{
            if(GlobalEventDispatcher.instance.isKeyDown('Control')) return;
            if(GlobalEventDispatcher.instance.isKeyDown('Shift')) return;
            this.selection.deselectAll()
        })
    }
}