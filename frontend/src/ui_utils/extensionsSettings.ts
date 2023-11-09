import { DictTopic, ObjectSyncClient } from "objectsync-client"
import { Linker } from "../component/linker"
import { Componentable } from "../component/componentable"
import { SimplePopupMenu } from "./simplePopupMenu"

export class ExtensionsSetting extends Componentable{
    objectsync: ObjectSyncClient
    importedExtensionsTopic: DictTopic<string,any>
    avaliableExtensionsTopic: DictTopic<string,any>
    importedDiv = document.getElementById('imported-extensions')
    avaliableDiv = document.getElementById('avaliable-extensions')
    cardTemplate = `
    <div class="card">
        <div class="card-image"></div>
        <div class="card-title"></div>
    </div>
    `
    cards: {imported:{[name:string]:HTMLElement},avaliable:{[name:string]:HTMLElement}} = {'imported':{},'avaliable':{}}
    constructor(objectsync:ObjectSyncClient){
        super()

        this.objectsync = objectsync

        this.importedExtensionsTopic = this.objectsync.getTopic('imported_extensions',DictTopic<string,any>)
        this.linker.link(this.importedExtensionsTopic.onAdd,(name,newExtension)=>{
            this.addCard(newExtension,'imported')
        })
        this.linker.link(this.importedExtensionsTopic.onPop,(name,oldExtension)=>{
            this.cards.imported[name].remove()
        })
        
        this.avaliableExtensionsTopic = this.objectsync.getTopic('avaliable_extensions',DictTopic<string,any>)
        this.linker.link(this.avaliableExtensionsTopic.onAdd,(name,newExtension)=>{
            this.addCard(newExtension,'avaliable')
        })
        this.linker.link(this.avaliableExtensionsTopic.onPop,(name,oldExtension)=>{
            this.cards.avaliable[name].remove()
        })
    }

    addCard(newExtension: any, status: 'imported' | 'avaliable'){
        let card: HTMLElement = document.createElement('div')
        card.innerHTML = this.cardTemplate
        card = card.firstElementChild as HTMLElement
        card.querySelector<HTMLDivElement>('.card-title').innerText = newExtension.name
        //card.querySelector<HTMLDivElement>('.card-image').style.backgroundImage = `url(${newExtension.icon})`
        card.querySelector<HTMLDivElement>('.card-image').style.backgroundImage = `url(https://imgur.com/xwG2FSr.jpg)`

        card.addEventListener('contextmenu',(e)=>{
            e.preventDefault()
            e.stopPropagation()
            let popup = SimplePopupMenu.instance
            popup.open(e.clientX,e.clientY)
            if(status == 'imported'){
                popup.addOption('Reload',()=>{
                    this.objectsync.emit('update_extension',{extension_name:newExtension.name})
                })
                popup.addOption('Remove from workspace',()=>{
                    this.objectsync.emit('unimport_extension',{extension_name:newExtension.name})
                })
            }else{
                popup.addOption('Import to workspace',()=>{
                    this.objectsync.emit('import_extension',{extension_name:newExtension.name})
                })
            }
        })

        this.cards[status][newExtension.name] = card
        if(status == 'imported'){
            this.importedDiv.appendChild(card)
            this.sortCards(this.importedDiv)
        }else{
            this.avaliableDiv.appendChild(card)
            this.sortCards(this.avaliableDiv)
        }
    }

    sortCards(div:HTMLElement){
        let cards = Array.from(div.querySelectorAll('.card'))
        cards.sort((a,b)=>{
            let aTitle = a.querySelector<HTMLDivElement>('.card-title').innerText
            let bTitle = b.querySelector<HTMLDivElement>('.card-title').innerText
            //always put builtin nodes at the top
            if(aTitle.startsWith('grapycal_builtin')) return -1
            return aTitle.localeCompare(bTitle)
        })
        cards.forEach(card=>div.appendChild(card))
    }


}