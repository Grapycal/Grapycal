import { DictTopic, ListTopic } from "objectsync-client"
import { GlobalEventDispatcher } from "../../component/eventDispatcher"
import { MouseOverDetector } from "../../component/mouseOverDetector"
import { print } from "../../devUtils"
import { Editor } from "../../sobjects/editor"
import { Workspace } from "../../sobjects/workspace"
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
        if(this.strings.length==0)return[];
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

export type OptionInfo = {key:string,value:string,callback:()=>void,displayName?:string}
export class AutoCompMenu extends PopupMenu{
    get template():string{
        return `
        <div class="base">
            <div class="search-container">
                <input type="text" id="search" class="search" placeholder="Search...">

                <div class="down-arrow">&#9660;</div>
            </div>
            <!-- a down arrow symbol -->
            
            <template id="option-template">
                <div class="option">
                </div>
            </template>
        </div>
        `
    }
    get style():string{
        return super.style + `
        .search-container{
            position: relative;
            width: 100%;
            box-sizing: border-box;
            border: none;
            background-color: var(--z1);
            color: var(--text-high);
        }
        .search{
            padding: 0px 5px;
            width: 100%;
        }
        .down-arrow{
            position: absolute;
            right: 2px;
            top: 0px;
            bottom: 0px;
            margin: auto;
            height: 1em;
            color: var(--text-low);
            pointer-events: none;

        }
        .option{
            padding:0px 5px;
        }
        `
    }
    protected search:HTMLInputElement
    private substringSearchIndex:SubstringSearchIndex = new SubstringSearchIndex()
    private valueToCallback:Map<string,()=>void> = new Map()
    private valueToDisplayName:Map<string,string> = new Map()
    private lastSetValue = ''
    get value():string{
        return this.search.value
    }
    set value(val:string){
        this.search.value = val
        this.lastSetValue = val
    }
    constructor(){
        super()
        this.search = this.htmlItem.getHtmlEl('search') as HTMLInputElement

        this.link2(this.search,'input',this.onInput)
        this.link2(this.search,'focus',this.onFocus)
        
    }
    
    public setOptions(options:OptionInfo[]){
        let keys = []
        let values = []
        this.valueToCallback.clear()
        this.valueToDisplayName.clear()
        for(let i = 0;i<options.length;i++){
            keys.push(options[i].key.toLowerCase())
            values.push(options[i].value)
            this.valueToCallback.set(options[i].value,options[i].callback)
            this.valueToDisplayName.set(options[i].value,options[i].displayName||options[i].key)
        }
        this.substringSearchIndex.setStrings(keys,values)
    }

    private onSearch(valueOverride:string = null){
        let query = valueOverride != null?valueOverride:this.value.toLowerCase()
        let results = this.substringSearchIndex.search(query)
        this.clearOptions()
        for(let result of results){
            const callback = ()=>{
                this.value = this.valueToDisplayName.get(result)
                this.valueToCallback.get(result)()
            }
            this.addOption(this.valueToDisplayName.get(result),callback)
        }
    }
    private onFocus(){
        if(!this.opened)
            this.open()
    }
    private onInput(){
        this.onSearch()
    }
    openAt(x:number,y:number){
        super.openAt(x,y)
        this.search.focus()
        this.onSearch()
        this.link(GlobalEventDispatcher.instance.onAnyKeyDown,this.onKeyDown)
    }
    open(){
        super.open()
        this.search.focus()
        this.onSearch('') // show all options by setting empty query
        this.setFocusedOption(this.value)
        this.link(GlobalEventDispatcher.instance.onAnyKeyDown,this.onKeyDown)
        this.search.selectionEnd = 1000 // Select all.
    }
    close(): void {
        super.close()
            this.search.blur()
        this.value = this.lastSetValue
        this.unlink(this.onKeyDown)
    }

    private onKeyDown(e:KeyboardEvent){
        if(e.key == 'Escape' && this.opened){
            this.close()
        }
    }
}