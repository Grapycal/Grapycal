import { Action, DictTopic, ListTopic, Topic } from "objectsync-client"
import { Componentable } from "../component/componentable"
import { as } from "../utils"
import { Workspace } from "../sobjects/workspace"
import { print } from "../devUtils"
import { object_equal } from "./inspector"
import { Editor } from "./Editor"

export class DictEditor extends Editor<DictTopic<string,string>> {

    get template() {
        return `
        <div class="attribute-editor flex-horiz stretch">
            <div id="attribute-name" class="attribute-name"></div>
            <div class="container">
                <div class="container" id="slot_container"></div>
                <div class="container horiz">
                    <input id="key" type="text" class="grow" list="ab">
                    <datalist id="ab">
                        <option value="aht4w">
                        <option value="ahqg">
                        <option value="aqg">
                    </datalist>
                    :
                    <input id="value" type="text" class="grow">
                    <button id="add-button" class="button center-align">+</button>
                </div>
            </div>
        </div>
    `
    }

    get style(): string {
        return super.style + `
        .container{
            display: flex;
            flex-direction: column;
            align-items: stretch;
            flex-grow: 1;
            margin: 4px 10px;
            min-width: 0px;
        }
        .horiz{
            flex-direction: row;
        }
        
        .button{
            height: 20px;
            line-height: 0px;
        }
    `
    }

    private readonly container: HTMLDivElement
    private readonly addButton: HTMLButtonElement
    private readonly keyInput: HTMLInputElement
    private readonly valueInput: HTMLInputElement
    private readonly items: Set<DictEditorItem> = new Set();
    private locked = false;
    private readonly allowedKeys: string[]|null = null

    constructor(displayName: string, editorArgs: any, connectedAttributes:DictTopic<string,string>[]) {
        super()
        this.connectedAttributes = connectedAttributes

        this.container = as(this.htmlItem.getHtmlEl('slot_container'), HTMLDivElement)
        this.keyInput = as(this.htmlItem.getHtmlEl('key'), HTMLInputElement)
        this.valueInput = as(this.htmlItem.getHtmlEl('value'), HTMLInputElement)
        this.addButton = as(this.htmlItem.getHtmlEl('add-button'), HTMLButtonElement)

        for(let input of [this.keyInput, this.valueInput]){
            this.linker.link2(input, 'keydown', (e: KeyboardEvent) => {
                if (e.key === 'Enter') {
                    this.addHandler()
                }
            })
        }

        this.linker.link2(this.addButton, 'click', this.addHandler)

        this.htmlItem.getHtmlEl('attribute-name').innerText = displayName

        for (let attr of connectedAttributes) {
            this.linker.link(attr.onSet, this.updateValue)
        }

        this.updateValue()
    }

    private getCommonKeyValue(maps: Map<string,string>[]): [string,string|null][]{
        let res: [string,string|null][] = []
        if (maps.length === 0) return res
        let firstMap = maps[0]
        for(let key of firstMap.keys()){
            let isCommon = true
            for(let map of maps){
                if(!map.has(key)){
                    isCommon = false
                    break
                }
            }
            if(isCommon){
                let commonValue = firstMap.get(key)!
                for(let map of maps){
                    if(map.get(key) !== firstMap.get(key)){
                        commonValue = null
                        break
                    }
                }
                res.push([key,commonValue])
            }
        }
        return res
    }

    private updateValue() {
        if (this.locked) return
        
        let maps: Map<string,string>[] = []
        for (let attr of this.connectedAttributes) {
            maps.push(attr.getValue())
        }
        let commonKeys = this.getCommonKeyValue(maps)

        // First destroy all items (Sorry, performance)
        for (let item of this.items.values()) {
            item.destroy()
        }
        this.items.clear()
        

        this.container.innerText = ''
        for (let [key,value] of commonKeys) {
            let itemComponent = new DictEditorItem(key, value)
            this.link(itemComponent.valueChanged, this.valueChangedHandler)
            this.link(itemComponent.deleteClicked, this.deleteHandler)
            this.items.add(itemComponent)
            itemComponent.htmlItem.setParent(this.htmlItem, 'container')
        }
        
    }

    private addHandler() {
        let key = this.keyInput.value
        let value = this.valueInput.value
        this.keyInput.value = ''
        this.valueInput.value = ''
        this.locked = true
        try{
            Workspace.instance.record(() => {
                for (let attr of this.connectedAttributes) {
                    attr.add(key,value)
                }
            })
        }catch(e){
            console.warn(e)
            return
        }
        this.locked = false
        this.updateValue() // Manually update value because it was locked when attribute was changed
    }

    private valueChangedHandler(key:string, value: string) {
        this.locked = true
        Workspace.instance.record(() => {
            for (let attr of this.connectedAttributes) {
                attr.changeValue(key,value)
            }
        })
        this.locked = false
    }

    private deleteHandler(item: DictEditorItem) {
        this.locked = true
        Workspace.instance.record(() => {
            for (let attr of this.connectedAttributes) {
                attr.pop(item.key)
            }
        })
        this.items.delete(item)

        this.locked = false
        this.updateValue() // Manually update value because it was locked when attribute was changed
    }
}
class DictEditorItem extends Componentable {

    get template() {
        return `
        <div class="item flex-horiz stretch">
            <div id="dict-editor-item-key"class="text grow"></div>
            <input id="dict-editor-item-value" type="text" class="grow">
            <button id="dict-editor-item-delete" class="button center-align">-</button>
        </div>
        `
    }

    get style(): string {
        return super.style + `
        .item{
            margin: 2px 0px;
            border: 1px outset #373737;
            flex-grow: 1;
            background-color: var(--z2);
            min-width: 0px;
        }
        .text{
            flex-grow: 1;
            margin-left: 5px;
            min-width: 30px; /* prevent too large width when overflow*/
            overflow: hidden;
        }
        #dict-editor-item-value{
            border: gray 1px solid;
        }
        .button{
            height: 20px;
            line-height: 0px;
        }
   `
    }

    readonly key: string

    readonly keyDiv: HTMLDivElement
    readonly valueInput: HTMLInputElement
    public readonly deleteButton: HTMLButtonElement

    public readonly valueChanged = new Action<[string,string]>();
    public readonly deleteClicked = new Action<[DictEditorItem]>();

    private locked = false

    constructor(key: string,value: string) {
        super()
        this.key = key
        this.keyDiv = as(this.htmlItem.getHtmlEl('dict-editor-item-key'), HTMLDivElement)
        this.valueInput = as(this.htmlItem.getHtmlEl('dict-editor-item-value'), HTMLInputElement)
        this.deleteButton = as(this.htmlItem.getHtmlEl('dict-editor-item-delete'), HTMLButtonElement)
        
        this.keyDiv.innerText = key
        if(value === null){
            this.valueInput.placeholder = 'Multiple values'
        }else{
            this.valueInput.value = value
        }
        this.link2(this.valueInput, 'input', this.valueChangedHandler)
        this.link2(this.deleteButton, 'click', this.deleteClickedHandler)
    }

    public changeValue(value: string) {
        this.locked = true
        this.valueInput.value = value
        this.locked = false
    }

    private valueChangedHandler() {
        if (this.locked) return
        this.valueChanged.invoke(this.key,this.valueInput.value)
    }

    private deleteClickedHandler() {
        this.destroy()
        this.deleteClicked.invoke(this)
    }
}
