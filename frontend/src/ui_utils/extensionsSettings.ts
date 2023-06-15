import { DictTopic, ObjectSyncClient } from "objectsync-client"
import { Linker } from "../component/linker"
import { Componentable } from "../component/component"
import { PopupMenu } from "./popupMenu"
import { print } from "../devUtils"
import { EventDispatcher } from "../component/eventDispatcher"

export class ExtensionsSetting extends Componentable{
    objectsync: ObjectSyncClient
    importedExtensionsTopic: DictTopic<string,any>
    avaliableExtensionsTopic: DictTopic<string,any>
    importedDiv = document.getElementById('imported-extensions')
    avaliableDiv = document.getElementById('avaliable-extensions')
    cards: {[key:string]:HTMLElement} = {}
    private readonly linker = new Linker(this);
    cardTemplate = `
    <div class="card">
        <div class="card-image"></div>
        <div class="card-title"></div>
    </div>
    `
    constructor(objectsync:ObjectSyncClient){
        super()

        document.getElementById('settings-page-close').addEventListener('click',()=>{
            document.getElementById('settings-page').classList.toggle('open')
        })

        document.getElementById('settings-page-overlay').addEventListener('click',()=>{
            document.getElementById('settings-page').classList.toggle('open')
        })

        this.objectsync = objectsync

        this.importedExtensionsTopic = this.objectsync.getTopic('imported_extensions',DictTopic<string,any>)
        this.linker.link(this.importedExtensionsTopic.onAdd,(name,newExtension)=>{
            this.addCard(newExtension,'imported')
        })
        this.linker.link(this.importedExtensionsTopic.onRemove,(name,oldExtension)=>{
            this.cards[name].remove()
            delete this.cards[name]
        })
        
        this.avaliableExtensionsTopic = this.objectsync.getTopic('avaliable_extensions',DictTopic<string,any>)
        this.linker.link(this.avaliableExtensionsTopic.onAdd,(name,newExtension)=>{
            this.addCard(newExtension,'avaliable')
        })
        this.linker.link(this.avaliableExtensionsTopic.onRemove,(name,oldExtension)=>{
            this.cards[name].remove()
            delete this.cards[name]
        })
    }

    addCard(newExtension: any, status: 'imported' | 'avaliable'){
        let card: HTMLElement = document.createElement('div')
        card.innerHTML = this.cardTemplate
        card = card.firstElementChild as HTMLElement
        card.querySelector<HTMLDivElement>('.card-title').innerText = newExtension.name
        //card.querySelector<HTMLDivElement>('.card-image').style.backgroundImage = `url(${newExtension.icon})`
        card.querySelector<HTMLDivElement>('.card-image').style.backgroundImage = `url(https://imgur.com/CGgS4FF.png)`

        card.addEventListener('contextmenu',(e)=>{
            e.preventDefault()
            e.stopPropagation()
            let popup = PopupMenu.instance.reset(e.clientX,e.clientY)
            if(status == 'imported'){
                popup.addOption('Reload',()=>{
                    this.objectsync.emit('update_extension',{extension_name:newExtension.name})
                })
                if(!newExtension.name.startsWith('builtin_nodes')){
                    popup.addOption('Remove from workspace',()=>{
                        this.objectsync.emit('unimport_extension',{extension_name:newExtension.name})
                    })
                }
            }else{
                popup.addOption('Import to workspace',()=>{
                    this.objectsync.emit('import_extension',{base_name:newExtension.name})
                })
            }
        })

        this.cards[newExtension.name] = card
        if(status == 'imported'){
            this.importedDiv.appendChild(card)
        }else{
            this.avaliableDiv.appendChild(card)
        }
    }


}