import { Constructor, defined } from "../utils"

// I gonna write Unity code in ts XD

export abstract class Component{
    readonly object: IComponentable;
    constructor(object: IComponentable){
        this.object = object;
        this.object.componentManager.addComponent(this);
    }
    get componentManager(): ComponentManager{
        return this.object.componentManager;
    }
    getComponent<T extends Component>(type:Constructor<T>): T{
        return this.object.componentManager.getComponent<T>(type);
    }
    getComponents<T extends Component>(type:Constructor<T>): T[]{
        return this.object.componentManager.getComponents<T>(type);
    }
    removeComponent(component: Component): void{
        this.object.componentManager.removeComponent(component);
    }
}

export class ComponentManager{
    components: Array<Component> = [];
    addComponent(component: Component): void{
        this.components.push(component);
    }
    getComponent<T extends Component>(type:Constructor<T>): T{
        const component = this.components.find((component) => component.constructor.name === type.name);
        if (component === undefined){
            throw new Error(`Component ${type.name} not found`);
        }
        return defined(component) as T;
    }
    getComponents<T extends Component>(type:Constructor<T>): T[]{
        return this.components.filter((component) => component.constructor.name === type.name) as Array<T>;
    }

    removeComponent(component: Component): void{
        const index = this.components.indexOf(component);
        if (index === -1){
            throw new Error(`Component ${component.constructor.name} not found`);
        }
        this.components.splice(index,1);
    }
    hasComponent<T extends Component>(type:Constructor<T>): boolean{
        return this.components.some((component) => component.constructor.name === type.name);
    }
}

export interface IComponentable{
    componentManager: ComponentManager
}