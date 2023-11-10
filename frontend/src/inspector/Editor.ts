import { ObjDictTopic, ObjListTopic, ObjSetTopic, ObjectTopic, Topic } from "objectsync-client"
import { Componentable } from "../component/componentable"

export class Editor<T extends Topic<any>|ObjectTopic<any>|ObjListTopic<any>|ObjSetTopic<any>|ObjDictTopic<any>> extends Componentable {
    protected connectedAttributes: T[] = []
    get topic(): T {
        return this.connectedAttributes[0]
    }
}