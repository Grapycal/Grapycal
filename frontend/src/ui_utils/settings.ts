import { CompSObject } from "../sobjects/compSObject"
import { Inspector } from "../inspector/inspector"
import { OptionsEditor } from "../inspector/OptionEditor"

export class Settings extends CompSObject{
    inspector: Inspector = new Inspector()

    protected onStart(): void {
        this.inspector.htmlItem.setParentElement(document.getElementById('tab-settings'))
        let editor = new OptionsEditor('theme',{'options':['light','simple','purple','fire']})
        this.inspector.addEditor(editor)
        editor.topic.set('simple')
        editor.topic.onSet.add((value)=>{
            // Seamless theme change
            let old = document.getElementById('custom-css')
            old.id = ''
            let swap: HTMLLinkElement = old.cloneNode(true) as HTMLLinkElement
            swap.id = 'custom-css'
            swap.setAttribute('href',`./css/${value}/main.css`)
            document.head.append(swap)
            setTimeout(() => {
                old.remove()
            }, 200);
        })
    }
}