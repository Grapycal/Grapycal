import { Action, ObjectSyncClient, StringTopic } from "objectsync-client"
import { Component, IComponentable } from "../component/component"
import { Linker } from "../component/linker"
import { print } from "../devUtils"
import { TextBox } from "../utils"

export function inputFinished(input: HTMLInputElement){
    let action = new Action<[],void>()
    input.addEventListener("blur", () => {
        action.invoke()
    })
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            action.invoke()
        }
    })
    return action
}


function longestCommonPrefixLength(a: string, b: string): number {
    let i = 0
    while (i < a.length && i < b.length && a[i] == b[i]) {
        i++
    }
    return i
}

export class BindInputBoxAndTopic extends Component{
    private input: HTMLInputElement|HTMLTextAreaElement|TextBox
    private topics: StringTopic[]
    private objectsync: ObjectSyncClient
    private linker: Linker
    private locked = false
    constructor(object:IComponentable, input: HTMLInputElement|HTMLTextAreaElement|TextBox, topic: StringTopic|StringTopic[], objectsync:ObjectSyncClient, updateEveryInput: boolean = false){
        super(object)
        this.input = input
        this.topics = topic instanceof Array ? topic : [topic]
        this.objectsync = objectsync
        if (!this.hasComponent(Linker)) {
            this.linker = new Linker(this.object)
        }else{
            this.linker = this.getComponent(Linker)
        }

        this.linker.link2(this.input, "blur", this.inputChanged, this)
        this.linker.link2(this.input, "keydown", (e) => {
            if (e.key === "Enter") {
                this.inputChanged()
            }
        }, this)
        
        if (updateEveryInput) {
            this.linker.link2(this.input, "input", this.inputChanged, this)
        }

        if(this.topics.length == 1){
            this.linker.link(this.topics[0].onInsert, this.onInsert, this)
            this.linker.link(this.topics[0].onDel, this.onDel, this)
        }
        else // can't manage selection of multiple topics
            for(let topic of this.topics){
                this.linker.link(topic.onSet, this.onSet, this)
            }
        this.onSet()
        
    }
    private inputChanged(){
        this.locked = true
        const selectionStart = this.input.selectionStart
        const selectionEnd = this.input.selectionEnd
        const oldtopic = this.topics[0].getValue()
        const newtopic = this.input.value
        const lengthDiff = newtopic.length - oldtopic.length

        if (this.topics.length > 1) {
            // just set
            this.objectsync.record(() => {
                for(let topic of this.topics){
                    topic.set(this.input.value)
                }
            })
            this.locked = false
            return
        }

        if (lengthDiff == 0) {
            if (oldtopic == newtopic) {
                // nothing changed
                this.locked = false
                return
            }
        }
        
        // Assume the changes are always right before selectionEnd
        if (lengthDiff > 0) {
            // topic was added
            const addedtopic = newtopic.slice(selectionEnd - lengthDiff, selectionEnd)
            // check if added topic is actually the same as the topic that was added
            const assumedNewtopic = oldtopic.slice(0, selectionEnd - lengthDiff) + addedtopic + oldtopic.slice(selectionEnd - lengthDiff)
            if (assumedNewtopic == newtopic) {
                this.objectsync.record(() => {
                    for(let topic of this.topics){
                    topic.insert(selectionEnd - lengthDiff, addedtopic)
                    }
                })
                this.locked = false
                return
            }else{
            }
        }
        if (lengthDiff < 0) {
            // topic was removed
            const removedtopic = oldtopic.slice(selectionEnd, selectionEnd - lengthDiff)
            // check if removed topic is actually the same as the topic that was removed
            const assumedNewtopic = oldtopic.slice(0, selectionEnd) + oldtopic.slice(selectionEnd - lengthDiff)
            if (assumedNewtopic == newtopic) {
                this.objectsync.record(() => {
                    for(let topic of this.topics){
                        topic.del(selectionEnd, removedtopic)
                    }
                })
                this.locked = false
                return
            }else{
            }
        }

        // maybe some topic was removed and some was added

        if (oldtopic.slice(selectionEnd - lengthDiff) == newtopic.slice(selectionEnd)) {
            // Find the longest common prefix
            const prefixLength = longestCommonPrefixLength(oldtopic.slice(0, selectionEnd - lengthDiff), newtopic.slice(0, selectionEnd))
            const removedtopic = oldtopic.slice(prefixLength, selectionEnd - lengthDiff)
            const addedtopic = newtopic.slice(prefixLength, selectionEnd)
            this.objectsync.record(() => {
                this.objectsync.record(() => {
                    for(let topic of this.topics){
                        topic.del(prefixLength, removedtopic)
                        topic.insert(prefixLength, addedtopic)
                    }
                })
            })
            this.locked = false
            return
        }

        // Don't know what happened. Maybe magic?
        this.objectsync.record(() => {
            for(let topic of this.topics){
                topic.set(this.input.value)
            }
        })
        console.warn("topicControl: Could not determine what happened to the topic. Using set instead of insert or del.")
        this.locked = false
    }

    private onInsert(position: number, insertion: string) {
        if (this.locked) return
        const oldSelectionStart = this.input.selectionStart
        const oldSelectionEnd = this.input.selectionEnd
        const oldText = this.input.value
        const newText = oldText.slice(0, position) + insertion + oldText.slice(position)
        this.input.value = newText
        if (document.activeElement != this.input) {
            return
        }
        if(oldSelectionStart >= position){
            this.input.selectionStart = oldSelectionStart + insertion.length
        }else{
            this.input.selectionStart = oldSelectionStart
        }
        if(oldSelectionEnd > position){
            this.input.selectionEnd = oldSelectionEnd + insertion.length
        }else{
            this.input.selectionEnd = oldSelectionEnd
        }
    }

    private onDel(position: number, deletion: string) {
        if (this.locked) return
        const oldSelectionStart = this.input.selectionStart
        const oldSelectionEnd = this.input.selectionEnd
        const oldText = this.input.value
        const newText = oldText.slice(0, position) + oldText.slice(position + deletion.length)
        this.input.value = newText
        if (document.activeElement != this.input) {
            return
        }
        if(oldSelectionStart > position){
            this.input.selectionStart = oldSelectionStart - deletion.length
        }else{
            this.input.selectionStart = oldSelectionStart
        }
        if(oldSelectionEnd >= position){
            this.input.selectionEnd = oldSelectionEnd - deletion.length
        }else{
            this.input.selectionEnd = oldSelectionEnd
        }
    }

    private onSet() {
        if (this.locked) return
        let value: string = null
        for (let topic of this.topics) {
            if (value === null) {
                value = topic.getValue()
            } else {
                if (value !== topic.getValue()) {
                    value = null
                    break
                }
            }
        }
        if (value === null) {
            this.input.value = ''
            this.input.placeholder = 'multiple values'
        } else {
            this.input.value = value.toString()
        }
    }

}