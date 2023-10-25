import { Action } from "objectsync-client"
import { print } from "./devUtils"

export { Action } from "objectsync-client"

export function defined<T>(value: T | undefined| null): T {
    if (value === undefined) {
        throw new Error("Value is undefined");
    }
    if (value === null) {
        throw new Error("Value is null");
    }
    return value as T;
}

export type Constructor<T> = new (...args: any[]) => T;

export function as <T>(value: any, type: Constructor<T>): T {
    if (value instanceof type)
        return value;
    if (value === null)
        return null;
    throw new Error(`Value ${value} is not instance of ${type.name}`);
}

export abstract class ContextManager{
    with(callback: () => void): void{
        this.enter();
        try {
            callback();
        }
        finally {
            this.exit();
        }
    }
    abstract enter(): void;
    abstract exit(): void;
}


type Callback<ARGS extends any[], OUT> = (...args: ARGS) => OUT;



export class Vector2 {

    static get zero(): Vector2{
        return new Vector2(0, 0);
    }

    static get one(): Vector2{
        return new Vector2(1, 1);
    }

    static get up(): Vector2{
        return new Vector2(0, 1);
    }

    static get down(): Vector2{
        return new Vector2(0, -1);
    }

    static get left(): Vector2{
        return new Vector2(-1, 0);
    }

    static get right(): Vector2{
        return new Vector2(1, 0);
    }

    static angle(a: Vector2, b: Vector2): number{
        return Math.atan2(b.y - a.y, b.x - a.x);
    }

    static fromPolar(r: number, theta: number): Vector2{
        return new Vector2(r * Math.cos(theta), r * Math.sin(theta));
    }

    x: number;
    y: number;
    get length(): number{
        return Math.sqrt(this.x**2 + this.y**2);
    }
    constructor(x: number, y: number){
        this.x = x;
        this.y = y;
    }
    distanceTo(other: Vector2): number{
        return Math.sqrt((this.x - other.x)**2 + (this.y - other.y)**2);
    }
    add(other: Vector2): Vector2{
        return new Vector2(this.x + other.x, this.y + other.y);
    }
    sub(other: Vector2): Vector2{
        return new Vector2(this.x - other.x, this.y - other.y);
    }
    mul(other: Vector2): Vector2{
        return new Vector2(this.x * other.x, this.y * other.y);
    }
    mulScalar(scalar: number): Vector2{
        return new Vector2(this.x * scalar, this.y * scalar);
    }
    dot(other: Vector2): number{
        return this.x * other.x + this.y * other.y;
    }

    static fromString(str: string): Vector2{
        const [x, y] = str.split(',').map(parseFloat);
        return new Vector2(x, y);
    }

    toString(): string{
        return `${this.x},${this.y}`;
    }

    equals(another:Vector2){
        return this.x == another.x && this.y == another.y
    }

    angle(): number{
        return Math.atan2(this.y, this.x);
    }

    normalized(): Vector2{
        return new Vector2(this.x / this.length, this.y / this.length);
    }

    rotate(angle: number): Vector2{
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        return new Vector2(this.x * cos - this.y * sin, this.x * sin + this.y * cos);
    }
}



export function getStaticField(object: any, fieldName: string): any {
    return object.constructor[fieldName];
}


export class ActionDict<K,ARGS extends any[], OUT=void> {
    private actions = new Map<K,Action<ARGS,OUT>>()
    add(key:K,callback: Callback<ARGS, OUT>) {
        if(!this.actions.has(key))this.actions.set(key,new Action<ARGS,OUT>())
        this.actions.get(key).add(callback)
    }
    
    remove(key:K,callback: Callback<ARGS, OUT>) {
        this.actions.get(key).remove(callback)
        if(this.actions.get(key).numCallbacks==0)this.actions.delete(key)
    }

    invoke(key:K, ...args: ARGS): OUT[] {
        if(!this.actions.has(key))return []
        return this.actions.get(key).invoke(...args)
    }

    slice(key:K):ActionDictSlice<K,ARGS,OUT>{
        return new ActionDictSlice(this,key)
    }
}

class ActionDictSlice<K,ARGS extends any[], OUT=void> {
    constructor(private actionDict:ActionDict<K,ARGS,OUT>,private key:K){}
    add(callback: Callback<ARGS, OUT>) {
        this.actionDict.add(this.key,callback)
    }
    
    remove(callback: Callback<ARGS, OUT>) {
        this.actionDict.remove(this.key,callback)
    }

    invoke(...args: ARGS): OUT[] {
        return this.actionDict.invoke(this.key,...args)
    }

}

export function eatEvents(el:HTMLTextAreaElement|HTMLInputElement){
    let f = (e:Event)=>{
        if(el==document.activeElement||e.type=="pointerdown"||e.type=="mousedown")
            e.stopPropagation()
    }
    for(let key in el){
        if(key.startsWith("on")){
            el.addEventListener(key.slice(2),f)
        }
    }
}

export function textToHtml(text:string){
    return text.replace(/\n/g,"<br>").replace(/ /g,"&nbsp;")
}

export class TextBox{
    public readonly textarea = document.createElement("textarea")
    private sizeSimulator = document.createElement("div")
    public onResize = new Action<[number,number]>()
    set value(value:string){
        this.textarea.value = value
        this.resize()
    }
    get value(){
        return this.textarea.value
    }
    get selectionStart(){
        return this.textarea.selectionStart
    }
    get selectionEnd(){
        return this.textarea.selectionEnd
    }
    set selectionStart(value:number){
        this.textarea.selectionStart = value
    }
    set selectionEnd(value:number){
        this.textarea.selectionEnd = value
    }
    get placeholder(){
        return this.textarea.placeholder
    }
    set placeholder(value:string){
        this.textarea.placeholder = value
    }
    get disabled(){
        return this.textarea.disabled
    }
    set disabled(value:boolean){
        this.textarea.disabled = value
    }
    constructor(parent:HTMLElement=document.body){
        this.textarea.classList.add('grow')
        this.sizeSimulator.style.width = 0 + 'px';
        this.sizeSimulator.style.position = 'absolute';
        this.sizeSimulator.style.visibility = 'hidden';
        //no wrap
        this.sizeSimulator.style.whiteSpace = 'nowrap';
        eatEvents(this.textarea)
        this.textarea.addEventListener("input",()=>{
            this.resize()
        })
        parent.appendChild(this.textarea)
        parent.appendChild(this.sizeSimulator)
    }

    private prevHeight = 0
    private prevWidth = 0
    resize (){
        setTimeout(() => {
            this.sizeSimulator.style.font = window.getComputedStyle(this.textarea).font;
            //sync padding
            this.sizeSimulator.style.padding = window.getComputedStyle(this.textarea).padding;
            this.sizeSimulator.innerHTML = textToHtml(this.textarea.value);
            let calculatedWidth =this.sizeSimulator.scrollWidth+ 10 // I don't know why it needs more 10px
            this.textarea.style.width = calculatedWidth+ 'px';
            
            this.textarea.style.height = '0';
            this.textarea.style.height = this.textarea.scrollHeight + 'px';

            // if(this.textarea.value=='' && this.textarea.disabled){
            //     this.textarea.style.height='0px'
            // }

            if(this.textarea.scrollHeight!=this.prevHeight||this.textarea.clientWidth!=this.prevWidth){
                this.onResize.invoke(this.textarea.scrollHeight,this.prevHeight)
                this.prevHeight = this.textarea.scrollHeight
                this.prevWidth = this.textarea.scrollWidth
            }
        }, 0);
    }

    addEventListener(eventName:string,callback:EventListenerOrEventListenerObject){
        this.textarea.addEventListener(eventName,callback)
    }

    removeEventListener(eventName:string,callback:EventListenerOrEventListenerObject){
        this.textarea.removeEventListener(eventName,callback)
    }
    
}