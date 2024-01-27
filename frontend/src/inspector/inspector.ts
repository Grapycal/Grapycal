import { ObjDictTopic, ObjListTopic, ObjSetTopic, ObjectTopic, Topic } from "objectsync-client"
import { ComponentManager, IComponentable } from "../component/component"
import { HtmlItem } from "../component/htmlItem"
import { Node } from "../sobjects/node"
import { Constructor, as } from "../utils"
import { HierarchyNode } from "../ui_utils/hierarchyNode"
import { Linker } from "../component/linker"
import { Workspace } from "../sobjects/workspace"
import { TextEditor } from "./TextEditor"
import { ListEditor } from "./ListEditor"
import { IntEditor } from "./IntEditor"
import { FloatEditor } from "./FloatEditor"
import { ObjSetEditor } from "./ObjSetEditor"
import { print } from "../devUtils"
import { ButtonEditor } from "./ButtonEditor"
import { OptionsEditor as OptionsEditor } from "./OptionEditor"
import { Componentable } from "../component/componentable"
import { Editor } from "./Editor"
import { DictEditor } from "./DictEditor"

export function object_equal(a:any,b:any){
    return JSON.stringify(a) === JSON.stringify(b);
}

export class Inspector extends Componentable{
    componentManager = new ComponentManager();
    linker = new Linker(this);
    hierarchy: HierarchyNode;

    static nameEditorMap: {[key:string]:Constructor<Editor<any>>}={
        'text':TextEditor,
        'list':ListEditor,
        'int':IntEditor,
        'float':FloatEditor,
        'objSet':ObjSetEditor,
        'button':ButtonEditor,
        'options':OptionsEditor,
        'dict':DictEditor

    }

    protected get template(): string {return `
        <div class="full-height flex-vert" id="slot_default">
        </div>
        `;
    }

    constructor(){
        super()
        this.hierarchy = new HierarchyNode('', '',true);
        this.hierarchy.htmlItem.setParent(this.htmlItem);
    }

    update(exposedAttributes: Map<string,ExposedAttributeInfo[]>, acceptAmount: number=1){

        this.hierarchy.clear();
        // add groups to hierarchy
        for(const [name,infos] of exposedAttributes){
            let comparingEditorArgs = infos[0].editor_args;
            let accept = true;
        
            // all node should have the attribute
            if(infos.length !== acceptAmount){
                accept = false;
            }
        
            // the attributes from all nodes should have the same editor_args
            for(let info of infos){
                if(!object_equal(info.editor_args,comparingEditorArgs)){
                    accept = false;
                    break;
                }
            }
            
            if(accept){
                let editorArgs = infos[0].editor_args;
                let path = infos[0].display_name.split('/');
                let displayName = path.pop();
                let editorType = Inspector.nameEditorMap[editorArgs.type]
                let connectedAttributes :(Topic<any>|ObjectTopic<any>|ObjListTopic<any>|ObjSetTopic<any>|ObjDictTopic<any>)[] = [];
                for(let info of infos){
                    connectedAttributes.push(this.getTopicForEditor(info.name,editorType));
                }
                let editor = new editorType(displayName,editorArgs,connectedAttributes);
                this.hierarchy.addLeaf(editor.htmlItem,path);
            }
            
        }
    }

    private getTopicForEditor(topicName:string,editorType:Constructor<any>){
        if(editorType === ObjSetEditor){
            return Workspace.instance.objectsync.getTopic(topicName,ObjSetTopic);
        }else{
            return Workspace.instance.objectsync.getTopic(topicName);
        }
    }

    public addEditor<T extends Topic<any>|ObjectTopic<any>|ObjListTopic<any>|ObjSetTopic<any>|ObjDictTopic<any>>(editor:Editor<T>,category:string|string[]='',id=''): T{
        this.hierarchy.addLeaf(editor.htmlItem,category,id);
        return editor.topic;
    }

    public removeEditorById(id:string){
        this.hierarchy.removeLeafById(id);
    }
}


export class ExposedAttributeInfo {
    name: string
    display_name: string
    editor_args: {type: keyof typeof Inspector.nameEditorMap}
}

