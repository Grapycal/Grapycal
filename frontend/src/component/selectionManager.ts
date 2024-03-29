import { print } from "../devUtils"
import { Action } from "../utils"
import { Component } from "./component"
import { GlobalEventDispatcher } from "./eventDispatcher"
import { Selectable } from "./selectable"

export class SelectionManager extends Component{
    selected: Set<Selectable> = new Set();
    tracking: Set<Selectable> = new Set();

    _enabled = true;
    get enabled(){return this._enabled}
    set enabled(value: boolean){
        if(this._enabled == value) return;
        this._enabled = value;
    }

    onSelect = new Action<[Selectable]>();
    onDeselect = new Action<[Selectable]>();
    onClick = new Action<[Selectable]>();

    register(selectable: Selectable){
        this.tracking.add(selectable)
    }

    unregister(selectable: Selectable){
        this.deselect(selectable)
        this.tracking.delete(selectable)
    }

    select(selectable: Selectable){
        if(!this.enabled) return;
        if(!selectable.enabled) return;
        if(this.selected.has(selectable)) return;
        this.selected.add(selectable)
        selectable.select_raw()
        this.onSelect.invoke(selectable)
    }

    deselect(selectable: Selectable){
        if(!this.enabled) return;
        if(!this.selected.has(selectable)) return;
        this.selected.delete(selectable)
        selectable.deselect_raw()
        this.onDeselect.invoke(selectable)
    }

    selectAll(){
        for(let selectable of this.tracking){
            this.select(selectable)
        }
    }

    clearSelection(){
        for(let selectable of this.selected){
            this.deselect(selectable)
        }
    }

    click(selectable: Selectable){
        // if ctrl is pressed, toggle selection
        if(GlobalEventDispatcher.instance.isKeyDown('Control')){
            if(this.selected.has(selectable)){
                this.deselect(selectable)
            }else{
                this.select(selectable)
            }
        // if shift is pressed, add to selection
        }else if(GlobalEventDispatcher.instance.isKeyDown('Shift')){
            this.select(selectable)
        // otherwise, select only this
        }else{
            this.clearSelection()
            this.select(selectable)
        }
        this.onClick.invoke(selectable)
    }
}