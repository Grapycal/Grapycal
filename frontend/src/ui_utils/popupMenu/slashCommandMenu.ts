import { DictTopic } from "objectsync-client"
import { AutoCompMenu } from "./autoCompMenu"
import { Editor } from "../../sobjects/editor"
import { Workspace } from "../../sobjects/workspace"
import { MouseOverDetector } from "../../component/mouseOverDetector"
import { GlobalEventDispatcher } from "../../component/eventDispatcher"
import { Vector2 } from "../../utils"

export class SlashCommandMenu extends AutoCompMenu{
    // basically the same as AddNodeMenu, but with a different topic
    private slashCommandsTopic:DictTopic<string,any>
    get style(){
        return super.style+`
            .base{

                background-color: var(--z2);
                border: 1px solid var(--text-low);
                box-shadow: 0px 0px 5px 0px black;
            }
            .search-container{
                border-bottom: 1px solid var(--text-low);
            }
            .search{
                
                height:30px;
                padding: auto 5px;
            }
            .option{
                padding:5px;
            }
        `
    }
    constructor(private editor:Editor){
        super()
        this.link(GlobalEventDispatcher.instance.onAnyKeyDown,this.onKeyDown_)
        this.slashCommandsTopic = Workspace.instance.slashCommandsTopic
        this.link(this.slashCommandsTopic.onSet,this.updateCommands)
        this.hideWhenClosed = true
        this.closeWhenEmpty = true
    }

    private onKeyDown_(e:KeyboardEvent){
        if(!MouseOverDetector.objectsUnderMouse.includes(this.editor)){
            return
        }
        if(document.activeElement==document.body && !this.opened && e.key.length == 1 &&
             (e.key == '/' || e.key.match(/[a-zA-Z0-9_]/))
             &&!e.ctrlKey && !e.altKey && !e.metaKey
        ){
            this.openAt(GlobalEventDispatcher.instance.mousePos.x,GlobalEventDispatcher.instance.mousePos.y)
            this.value = ''
        }
    }

    protected updateCommands(commands:Map<string,any>){
        let options :{key:string,value:string,callback:()=>void,displayName:string}[] = []
        commands.forEach((command,commandName)=>{
            options.push({
                key:command.key,
                value:commandName,
                callback:()=>{
                    let ctx = {
                        editor_id:this.editor.id,
                        mouse_pos:this.editor.getMousePos().toList(),
                    }
                    Workspace.instance.callSlashCommand(commandName,ctx)
                },
                displayName:command.display_name
            })
        })
        this.setOptions(options)
    }
}
