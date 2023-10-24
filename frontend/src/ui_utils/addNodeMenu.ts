import { DictTopic, ListTopic } from "objectsync-client"
import { GlobalEventDispatcher } from "../component/eventDispatcher"
import { MouseOverDetector } from "../component/mouseOverDetector"
import { print } from "../devUtils"
import { Editor } from "../sobjects/editor"
import { Workspace } from "../sobjects/workspace"
import { PopupMenu } from "./popupMenu"

type ListNode = {
    next:ListNode
    prev:ListNode
    data:any
}

class List{
    private head: ListNode = null
    private tail: ListNode = null
    private cursor: ListNode = null

    public insert(data:any){
        //  insert after cursor
        let node:ListNode = {
            next:null,
            prev:null,
            data:data
        }
        if(this.head == null){
            this.head = node
            this.tail = node
            this.cursor = node
        }
        else{
            if(this.cursor.next != null){
                this.cursor.next.prev = node
            }
            else{
                this.tail = node
            }
            node.next = this.cursor.next
            node.prev = this.cursor
            this.cursor.next = node
            this.cursor = node
        }
    }

    public remove(){
        if(this.cursor == null) throw new Error('Cursor is null')
        if(this.cursor.prev != null){
            this.cursor.prev.next = this.cursor.next
        }
        else{
            this.head = this.cursor.next
        }
        if(this.cursor.next != null){
            this.cursor.next.prev = this.cursor.prev
        }
        else{
            this.tail = this.cursor.prev
        }
        this.cursor = this.cursor.next
    }

    public resetCursor(){
        this.cursor = this.head
    }

    public get(){
        if(this.cursor == null) throw new Error('Cursor is null')
        return this.cursor.data
    }

    public next(){
        if(this.cursor == null) throw new Error('Cursor is null')
        this.cursor = this.cursor.next
    }

    public hasNext(){
        return this.cursor != null
    }
            
    public isEmpty(){
        return this.head == null
    }
}

class SubstringSearchIndex{
    private charToPos:Map<string,number[][]> = new Map()
    private strings:string[] = []
    private values:string[] = []
    private currentPos:Array<number> = []
    private charMatched:Array<boolean> = []
    public setStrings(keys:string[],values:string[] = undefined){
        this.strings = keys
        this.values = values||keys
        this.charToPos.clear()
        for(let i = 0;i<keys.length;i++){
            let str = keys[i]
            for(let j = 0;j<str.length;j++){
                let char = str[j]
                let pos = this.charToPos.get(char)
                if(pos == undefined){
                    pos = new Array(keys.length)
                    for(let i = 0;i<keys.length;i++){
                        pos[i] = []
                    }
                    this.charToPos.set(char,pos)
                }
                pos[i].push(j)
            }
        }
        // prepare data structures for search
        this.currentPos = new Array(keys.length)
        this.charMatched = new Array(keys.length)
    }
    public search(query:string):string[]{
        //print('searching for',query)
        this.currentPos.fill(0)
        let candidates = new List()
        for(let i = 0;i<this.strings.length;i++){
            candidates.insert(i)
        }
        //print(candidates)

        for(let i = 0;i<query.length;i++){
            let char = query[i]
            let poss = this.charToPos.get(char)
            if(poss == undefined){
                return []
            }
            this.charMatched.fill(false)
            candidates.resetCursor()
            //print('searching for',char,'in',candidates)
            for(let stridx = candidates.get();candidates.hasNext();candidates.next()){
                stridx = candidates.get()
                //print(stridx,char)
                let occurences = poss[stridx]
                for(let occidx=0;occidx<occurences.length;occidx++){
                    //print('occ',occurences[occidx])
                    let occ = occurences[occidx]
                    if(occ >= this.currentPos[stridx]){
                        this.currentPos[stridx] = occ+1
                        this.charMatched[stridx] = true
                        break
                    }
                }
            }
            candidates.resetCursor()
            for(let stridx = candidates.get();candidates.hasNext();){
                stridx = candidates.get()
                if(!this.charMatched[stridx]){
                    //print('removing',stridx)
                    candidates.remove()
                }else{
                    candidates.next()
                }
            }
            if(candidates.isEmpty()){
                return []
            }
        }
        candidates.resetCursor()
        let res = []
        //sort by current pos
        let sorted = []
        for(let stridx = candidates.get();candidates.hasNext();candidates.next()){
            stridx = candidates.get()
            sorted.push([stridx,this.currentPos[stridx]])
        }
        sorted.sort((a,b)=>a[1]-b[1])
        for(let i = 0;i<sorted.length;i++){
            let stridx = sorted[i][0]
            res.push(this.values[stridx])
        }
        return res
    }
}

export class AddNodeMenu extends PopupMenu{
    get template():string{
        return `
        <div class="base">
            <input type="text" id="search" placeholder="Search...">
            <template id="option-template">
                <div class="option">
                </div>
            </template>
        </div>
        `
    }
    get style():string{
        return super.style + `
        #search{
            width: 100%;
            height: 30px;
            padding: 5px;
            box-sizing: border-box;
            border: none;
            border-bottom: 1px solid var(--text-low);
            background-color: var(--z1);
            color: var(--text-high);
        }
        `
    }
    private search:HTMLInputElement
    private nodeTypesTopic:DictTopic<string,any>
    private nodeTypesIsDirty:boolean = true
    private substringSearchIndex:SubstringSearchIndex = new SubstringSearchIndex()
    constructor(private editor:Editor){
        super()
        this.link(GlobalEventDispatcher.instance.onAnyKeyDown,this.onKeyDown)
        this.search = this.htmlItem.getHtmlEl('search') as HTMLInputElement
        this.nodeTypesTopic = Workspace.instance.objectsync.getTopic('node_types',DictTopic<string,any>)
        this.link(this.nodeTypesTopic.onSet,()=>{this.nodeTypesIsDirty = true;console.log('node types is dirty')})
    }
    public addOption(text:string,onclick:()=>void){
        let option = this.generateOptionElement()
        option.innerText = text
        this.addOptionElement(option,onclick)
        return option
    }
    private onKeyDown(e:KeyboardEvent){
        if(!MouseOverDetector.objectsUnderMouse.includes(this.editor)){
            return
        }
        if(document.activeElement==document.body && !this.opened && e.key.length == 1 && e.key.match(/[a-zA-Z0-9_]/) &&!e.ctrlKey && !e.altKey && !e.metaKey
        ){
            this.open(GlobalEventDispatcher.instance.mousePos.x,GlobalEventDispatcher.instance.mousePos.y)
            this.onSearch()
        }
        if(e.key == 'Escape' && this.opened){
            this.close()
        }
        if(e.key == 'Backspace' && this.search.value.length == 0 && this.opened){
            this.close()
        }
    }
    private indexNodeTypes(){
        let nodeTypes = this.nodeTypesTopic.getValue()
        let keys:string[] = []
        let values:string[] = []
        nodeTypes.forEach((nodeType,nodeTypeName)=>{
            nodeTypeName = nodeTypeName as string
            keys.push(nodeTypeName.toLowerCase().split('.')[1].slice(0,-4)) // remove Node suffix
            values.push(nodeTypeName)
        })
        this.substringSearchIndex.setStrings(keys,values)
    }

    private onSearch(){
        if(this.nodeTypesIsDirty){
            this.indexNodeTypes()
            this.nodeTypesIsDirty = false
        }
        let query = this.search.value.toLowerCase()
        let results = this.substringSearchIndex.search(query)
        this.clearOptions()
        let translation = this.editor.transform.worldToLocal(GlobalEventDispatcher.instance.mousePos).toString()
        for(let i = 0;i<results.length;i++){
            let result = results[i]
            let displayName = result.split('.')[1].slice(0,-4)
            this.addOption(displayName,()=>{
                
                this.editor.createNode(result,{translation:translation})
            })
        }
    }
    open(x:number,y:number){
        super.open(x,y)
        this.search.focus()
        this.link2(this.search,'input',this.onSearch)
    }
    close(): void {
        super.close()
        this.search.blur()
        this.search.value = ''
        this.unlink2(this.search,'input')
    }
}