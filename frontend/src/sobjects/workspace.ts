import { ObjectSyncClient, ObjectTopic} from "objectsync-client"
import { CompSObject } from "./compSObject";
import { EventDispatcher, GlobalEventDispatcher } from "../component/eventDispatcher"
import { Editor } from "./editor"
import { SelectionManager } from "../component/selectionManager"
import { Inspector } from "../inspector/inspector"
import { Node } from "./node"
import { Edge } from "./edge"
import { Footer } from "../ui_utils/footer"

export class Workspace extends CompSObject{
    public static instance: Workspace
    readonly main_editor = this.getAttribute('main_editor', ObjectTopic<Editor>)
    readonly eventDispatcher = new EventDispatcher(this, document.getElementById('workspace'))
    // This selection manager is for the regular selecting
    readonly selection = new SelectionManager(this) 
    // This selection manager is used by attr editors in the inspector
    readonly functionalSelection = new SelectionManager(this) 
    readonly inspector = new Inspector()
    readonly record: ObjectSyncClient['record']
    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id);
        (this.selection as any).name = 'selection';
        (this.functionalSelection as any).name = 'functionalSelection'
        
        Workspace.instance = this
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
        this.functionalSelection.enabled = false
        this.record = objectsync.record
    }
    protected onStart(): void {
        this.main_editor.getValue().eventDispatcher.onClick.add(()=>{
            if(GlobalEventDispatcher.instance.isKeyDown('Control')) return;
            if(GlobalEventDispatcher.instance.isKeyDown('Shift')) return;
            this.selection.clearSelection()
        })
        GlobalEventDispatcher.instance.onKeyDown.add('Delete',this.deletePressed.bind(this))
        Footer.setStatus('Workspace loaded.')
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