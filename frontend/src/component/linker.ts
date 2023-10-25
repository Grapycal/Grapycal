
import { Component } from "./component"
import { print } from "../devUtils"

type Callback<ARGS extends any[] = any[], OUT = any> = (...args: ARGS) => OUT;
interface IInvokeable<ARGS extends any[] = any[], OUT = any>{
    invoke(...args: ARGS): OUT;
    add(callback: Callback<ARGS, OUT>): void;
    remove(callback: Callback<ARGS, OUT>): void;
}

interface IHasAddEventListener{
    addEventListener(eventName: string, callback: Callback): void;
    removeEventListener(eventName: string, callback: Callback): void;
}

export class Linker extends Component{

    static staticLinkedCallbacks: {action: IInvokeable<any>, callback: Callback}[] = []
    static staticLinkedCallbacks2: {element: Node, eventName: string, callback: Callback}[] = []
    static link(action: IInvokeable<any>, callback: Callback): void{
        callback = callback.bind(this);
        this.staticLinkedCallbacks.push({action: action, callback: callback});
        action.add(callback);
    }


    linkedCallbacks: {action: IInvokeable<any>, callback: Callback, bindedCallback: Callback}[] = []
    linkedCallbacks2: {element: IHasAddEventListener, eventName: string, callback: Callback}[] = []
    /**
     * Use this method to link a callback to an action. 
     * The callback will be automatically bound to this object.
     * The callback will be automatically removed when the object is destroyed.
     * @param action 
     * @param callback 
     */
    public link(action: IInvokeable<any>, callback: Callback, bindTarget:any=null): void{
        let bindedCallback = callback.bind(bindTarget || this.object);
        action.add(bindedCallback);
        this.linkedCallbacks.push({action: action, callback: callback, bindedCallback: bindedCallback});
    }

    public unlink(action: IInvokeable<any,any>|Callback,throwIfNotExist:boolean=false): void{
        // check if action is IInvokeable
        if ('add' in action && 'remove' in action){
            this.unlinkAction(action,throwIfNotExist);
        }else{
            this.unlinkCallback(action,throwIfNotExist);
        }
    }
    
    public unlinkAction(action: IInvokeable<any,any>,throwIfNotExist:boolean=false): void{
        for(let i=0;i<this.linkedCallbacks.length;i++){
            if (this.linkedCallbacks[i].action == action){
                action.remove(this.linkedCallbacks[i].bindedCallback);
                this.linkedCallbacks.splice(i,1);
                return;
            }
        }
        if (throwIfNotExist){
            throw new Error('action not found');
        }
    }

    public unlinkCallback(callback: Callback,throwIfNotExist:boolean=false): void{
        for(let i=0;i<this.linkedCallbacks.length;i++){
            if (this.linkedCallbacks[i].callback == callback){
                this.linkedCallbacks[i].action.remove(this.linkedCallbacks[i].bindedCallback);
                this.linkedCallbacks.splice(i,1);
            }
        }
        if (throwIfNotExist){
            throw new Error('callback not found');
        }
    }


    public link2(element: IHasAddEventListener,eventName: string , callback: Callback, bindTarget:any=null): void{
        callback = callback.bind(bindTarget || this.object);
        this.linkedCallbacks2.push({element: element, eventName: eventName, callback: callback});
        element.addEventListener(eventName,callback);
    }
    
    public unlink2(element: IHasAddEventListener, eventName: string): void{
        for(let i=0;i<this.linkedCallbacks2.length;i++){
            if (this.linkedCallbacks2[i].element == element && this.linkedCallbacks2[i].eventName == eventName){
                element.removeEventListener(eventName,this.linkedCallbacks2[i].callback);
                this.linkedCallbacks2.splice(i,1);
                return;
            }
        }
    }
    onDestroy(): void {
        for(let {action,callback,bindedCallback} of this.linkedCallbacks){
            action.remove(bindedCallback);
        }
        for(let {element,eventName,callback} of this.linkedCallbacks2){
            element.removeEventListener(eventName,callback);
        }
    }
}