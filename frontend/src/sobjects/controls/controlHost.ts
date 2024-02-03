import { HtmlItem } from "../../component/htmlItem";
import { Node } from "../node";

export interface IControlHost {
    htmlItem: HtmlItem
    ancestorNode: Node
}