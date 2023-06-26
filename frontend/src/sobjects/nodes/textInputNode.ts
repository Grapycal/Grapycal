import { ObjectSyncClient, StringTopic } from "objectsync-client"
import { Node } from "../node"
import { expose } from "../../devUtils"
import { print } from "objectsync-client/src/devUtils"

export class TextInputNode extends Node{
    protected readonly templates: {[key: string]: string} = {
    block: 
    `<div class="node block-node flex-horiz space-between">
        <div id="slot_input_port" class="no-width flex-vert space-evenly"></div>
        <div class="NodeContent full-width flex-horiz space-evenly">
            <div id="label" class="center" ></div>
            <input id="input" type="text" style=" min-width:4ch; height:100%; text-align: center; border: none; outline: none; background: none;"/>
            <div id="fake_input"></div>
        </div>
        <div id="slot_output_port" class="no-width flex-vert space-evenly"></div>
    </div>`
    }
    text: StringTopic = null
    inputField: HTMLInputElement = null
    fakeInput: HTMLElement = null
    compositioning: boolean = false

    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id)
        this.text = this.getAttribute('text', StringTopic)
    }

    protected onStart(): void {
        super.onStart()
        this.link(this.text.onSet, (text)=>{this.inputField.value = text})
        this.fakeInput = this.htmlItem.getEl('fake_input')
        this.fakeInput.style.position = 'absolute'
        this.fakeInput.style.visibility = 'hidden'
        this.fakeInput.style.font = this.inputField.style.font
        this.fakeInput.style.fontSize = this.inputField.style.fontSize
        this.fakeInput.style.fontFamily = this.inputField.style.fontFamily
        //padding
        this.fakeInput.style.setProperty('padding-left', window.getComputedStyle(this.inputField).getPropertyValue('padding-left'))
        this.fakeInput.style.setProperty('padding-right', window.getComputedStyle(this.inputField).getPropertyValue('padding-right'))

        this.resizeInput()
    }

    reshape(shape: string): void {
        if(this.inputField != null){
            this.unlink2(this.inputField,'input')
        }
        super.reshape(shape)
        this.inputField = this.htmlItem.getEl('input',HTMLInputElement)
        this.inputField.value = this.text.getValue()
        this.inputField.addEventListener('input', (e)=>{
            if(!this.compositioning){
                this.text.set(this.inputField.value)
            }
            this.resizeInput()
        })
        this.inputField.addEventListener('compositionstart', (e)=>{
            this.compositioning = true
        })
        this.inputField.addEventListener('compositionend', (e)=>{
            this.compositioning = false
            this.text.set(this.inputField.value)
        })
    }

    private resizeInput(): void {
        this.fakeInput.innerHTML = this.inputField.value
        this.inputField.style.width = this.fakeInput.clientWidth + 'px'
        for(let port of this.in_ports){
            port.moved.invoke()
        }
        for(let port of this.out_ports){
            port.moved.invoke()
        }
    }
}