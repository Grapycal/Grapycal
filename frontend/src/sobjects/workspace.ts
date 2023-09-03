import { ObjectSyncClient, ObjectTopic, SObject } from "objectsync-client"
import { CompSObject } from "./compSObject";
import { EventDispatcher, GlobalEventDispatcher } from "../component/eventDispatcher"
import { Editor } from "./editor"
import { SelectionManager } from "../component/selectionManager"
import { Inspector } from "../inspector/inspector"
import { Node } from "./node"
import { Edge } from "./edge"

export class Workspace extends CompSObject{
    public static instance: Workspace
    readonly main_editor = this.getAttribute('main_editor', ObjectTopic<Editor>)
    readonly eventDispatcher = new EventDispatcher(this, document.getElementById('workspace'))
    readonly selection = new SelectionManager(this)
    readonly inspector = new Inspector()
    readonly record: ObjectSyncClient['record']
    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)
        Workspace.instance = this
        document.getElementById('settings-button').addEventListener('click',()=>{
            document.getElementById('settings-page').classList.toggle('open')
            objectsync.emit('refresh_extensions')
        })
        this.selection.onSelect.add((selectable)=>{
            let obj = selectable.object
            if(obj instanceof Node){
                this.inspector.addNode(obj)
            }
        })
        this.selection.onDeselect.add((selectable)=>{
            let obj = selectable.object
            if(obj instanceof Node){
                this.inspector.removeNode(obj)
            }
        })
        this.record = objectsync.record
    }
    protected onStart(): void {
        this.main_editor.getValue().eventDispatcher.onClick.add(()=>{
            if(GlobalEventDispatcher.instance.isKeyDown('Control')) return;
            if(GlobalEventDispatcher.instance.isKeyDown('Shift')) return;
            this.selection.deselectAll()
        })
        GlobalEventDispatcher.instance.onKeyDown.add('Delete',this.deletePressed.bind(this))
    }
    public getObjectSync(): ObjectSyncClient{
        return this.objectsync
    }
    private deletePressed(){
        let selectedIds = []
        for(let s of this.selection.selected){
            let o = s.object
            if(o instanceof Node || o instanceof Edge){
                selectedIds.push(o.id);
            }
        }
        this.objectsync.emit('delete',{ids:selectedIds})
    }
}