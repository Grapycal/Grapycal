import { HtmlItem } from "../../component/htmlItem";
import { Node } from "../node";

export interface ControlHost {
    htmlItem: HtmlItem
    ancestorNode: Node
}