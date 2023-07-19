import { print } from "../devUtils"
import { Action } from "../utils"
import { Component, IComponentable } from "./component"
import { EventDispatcher } from "./eventDispatcher"
import { SelectionManager } from "./selectionManager"

export class Selectable extends Component{
    selectionManager: SelectionManager
    onSelected: Action<[]> = new Action()
    onDeselected: Action<[]> = new Action()

    private _selected: boolean = false
    get selected(): boolean{
        return this._selected
    }

    constructor(object: IComponentable, selectionManager:SelectionManager){
        super(object)
        this.selectionManager = selectionManager
        this.selectionManager.register(this)
        this.getComponent(EventDispatcher).onClick.add(this.click.bind(this))
    }

    onDestroy(){
        this.selectionManager.unregister(this)
    }

    click(){
        // Let selection manager handle the click
        print('click')
        this.selectionManager.click(this)
    }

    /* Called by selectionManager */
    select_raw(){
        if(this._selected) return;
        this._selected = true;
        this.onSelected.invoke()
    }

    deselect_raw(){
        if(!this._selected) return;
        this._selected = false;
        this.onDeselected.invoke()
    }

    /* Shortcut methods */

    select(){
        this.selectionManager.select(this)
    }

    deselect(){
        this.selectionManager.deselect(this)
    }


}