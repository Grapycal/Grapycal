import { IntTopic, StringTopic } from "objectsync-client"
import { Control } from "./control";
import { HtmlItem } from "../../component/htmlItem"
import { print } from "../../devUtils"

function longestCommonPrefixLength(a: string, b: string): number {
    let i = 0
    while (i < a.length && i < b.length && a[i] == b[i]) {
        i++
    }
    return i
}

export class TextControl extends Control {
    
    textField: HTMLInputElement
    text = this.getAttribute("text", StringTopic)
    label = this.getAttribute("label", StringTopic)
    editable = this.getAttribute("editable", IntTopic)

    protected template = `
    <div class="control flex-horiz">
        <div class="label" id="label">Text</div>
        <input type="text" class="control-text text-field full-height full-width" id="text-field">
    </div>
    `

    protected onStart(): void {
        super.onStart()
        this.textField = this.htmlitem.getEl("text-field", HTMLInputElement)
        this.textField.value = this.text.getValue()
        this.link(this.text.onInsert, (position,insertion) => {
            if (this.text.inStack && this.text.stateManager.isRecording) return   
            const oldSelectionStart = this.textField.selectionStart
            const oldSelectionEnd = this.textField.selectionEnd
            const oldText = this.textField.value
            const newText = oldText.slice(0, position) + insertion + oldText.slice(position)
            this.textField.value = newText
            // if(oldSelectionStart == oldSelectionEnd){
            if(oldSelectionStart >= position){
                this.textField.selectionStart = oldSelectionStart + insertion.length
            }else{
                this.textField.selectionStart = oldSelectionStart
            }
            if(oldSelectionEnd > position){
                this.textField.selectionEnd = oldSelectionEnd + insertion.length
            }else{
                this.textField.selectionEnd = oldSelectionEnd
            }
        })

        this.link(this.text.onDel, (position, deletion) => {
            if (this.text.inStack) return
            const oldSelectionStart = this.textField.selectionStart
            const oldSelectionEnd = this.textField.selectionEnd
            const oldText = this.textField.value
            const newText = oldText.slice(0, position) + oldText.slice(position + deletion.length)
            this.textField.value = newText
            if(oldSelectionStart > position){
                this.textField.selectionStart = oldSelectionStart - deletion.length
            }else{
                this.textField.selectionStart = oldSelectionStart
            }
            if(oldSelectionEnd >= position){
                this.textField.selectionEnd = oldSelectionEnd - deletion.length
            }else{
                this.textField.selectionEnd = oldSelectionEnd
            }
        })

        this.textField.addEventListener("input", (e) => {
            const selectionStart = this.textField.selectionStart
            const selectionEnd = this.textField.selectionEnd
            const oldText = this.text.getValue()
            const newText = this.textField.value
            const lengthDiff = newText.length - oldText.length
            
            // Assume the changes are always right before selectionEnd
            if (lengthDiff > 0) {
                // Text was added
                const addedText = newText.slice(selectionEnd - lengthDiff, selectionEnd)
                // check if added text is actually the same as the text that was added
                const assumedNewText = oldText.slice(0, selectionEnd - lengthDiff) + addedText + oldText.slice(selectionEnd - lengthDiff)
                if (assumedNewText == newText) {
                    this.text.insert(selectionEnd - lengthDiff, addedText)
                    return
                }else{
                }
            }
            if (lengthDiff < 0) {
                // Text was removed
                const removedText = oldText.slice(selectionEnd, selectionEnd - lengthDiff)
                // check if removed text is actually the same as the text that was removed
                const assumedNewText = oldText.slice(0, selectionEnd) + oldText.slice(selectionEnd - lengthDiff)
                if (assumedNewText == newText) {
                    this.text.del(selectionEnd, removedText)
                    return
                }else{
                }
            }

            // maybe some text was removed and some was added

            if (oldText.slice(selectionEnd - lengthDiff) == newText.slice(selectionEnd)) {
                // Find the longest common prefix
                const prefixLength = longestCommonPrefixLength(oldText.slice(0, selectionEnd - lengthDiff), newText.slice(0, selectionEnd))
                const removedText = oldText.slice(prefixLength, selectionEnd - lengthDiff)
                const addedText = newText.slice(prefixLength, selectionEnd)
                this.objectsync.record(() => {
                    this.text.del(prefixLength, removedText)
                    this.text.insert(prefixLength, addedText)
                })
                return
            }

            // Don't know what happened. Maybe magic?
            this.text.set(this.textField.value)
            console.warn("TextControl: Could not determine what happened to the text. Using set instead of insert or del.")
        })

        let labelEl = this.htmlitem.getEl("label")
        this.link(this.label.onSet, (label) => {
            labelEl.textContent = label
        })

        this.link(this.editable.onSet, (editable) => {
            this.textField.disabled = !editable
        })
    }

}