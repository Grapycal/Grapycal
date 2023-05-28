import { ObjectSyncClient, SObject } from "objectsync-client"
import { Component, ComponentManager, IComponentable } from "../component/component"
import { Constructor, as } from "../utils"
import { Null } from "../devUtils"

export class CompSObject extends SObject implements IComponentable {
    componentManager: ComponentManager = new ComponentManager();
    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id);
    }

    public get parent(): CompSObject {
        if (super.parent == null)
            return Null();
        return as(super.parent, CompSObject);
    }

    public getComponentInAncestorsOrThis<T extends Component>(type: Constructor<T>): T | null {
        if (this.hasComponent(type))
            return this.getComponent(type);
        else if (this.isRoot)
            return null;
        else
            return this.parent.getComponentInAncestorsOrThis(type);
    }
    getComponentInAncestors<T extends Component>(type: Constructor<T>): T | null {
        if (this.isRoot)
            return null;
        return this.parent.getComponentInAncestorsOrThis(type);
    }

    public getComponent<T extends Component>(type: Constructor<T>): T {
        return this.componentManager.getComponent(type);
    }
    public hasComponent<T extends Component>(type: Constructor<T>): boolean {
        return this.componentManager.hasComponent(type);
    }
    public onDestroy(): void {
        super.onDestroy();
        this.componentManager.destroy();
    }
}