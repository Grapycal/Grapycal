import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic} from 'objectsync-client'

export abstract class ElementObject extends SObject{
    protected abstract readonly _element: HTMLElement;
    private style = this.getAttribute('style',DictTopic<string,string>);
    constructor(objectsync: ObjectSyncClient, id: string){
        super(objectsync,id);
        this.style.onAdd.add((key:string,value:string) => {
            this._element.style.setProperty(key,value);
        });  
        this.style.onRemove.add((key:string) => {
            this._element.style.removeProperty(key);
        });
        this.style.onChangeValue.add((key:string,newValue:string) => {
            this._element.style.setProperty(key,newValue);
        });
    }
    public get element() {
        return this._element
    }
    onParentChanged(oldParent: SObject, newParent: SObject): void{
        super.onParentChanged(oldParent,newParent);
        let htmlParent = newParent;
        while(!(htmlParent instanceof ElementObject)){
            if (htmlParent.isRoot){
                document.getElementById('Editor')!.appendChild(this.element);
                return;
            }
            htmlParent = htmlParent.parent;
        }
        htmlParent.element.appendChild(this.element);
    }
    onDestroy(): void{
        super.onDestroy();
        this.element.remove();
    }
}
