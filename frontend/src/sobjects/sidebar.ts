import { CompSObject } from './compSObject'
import { HtmlItem } from '../component/htmlItem'
import { HierarchyNode } from '../ui_utils/hierarchyNode'
import { Workspace } from './workspace'
import { as } from '../utils'
import { print } from '../devUtils'

export class Sidebar extends CompSObject {
    private items: HtmlItem[] = []
    nodeLibrary: HierarchyNode = new HierarchyNode('', '',true);
    tabs = new Map<HTMLButtonElement, HTMLDivElement>();
    sidebarContainer: HTMLDivElement;
    onStart() {
        let workspace = as(this.parent,Workspace)
        this.nodeLibrary.htmlItem.setParentElement(document.getElementById('node-list-container'))
        this.sidebarContainer = document.getElementById('left-sidebar-container') as HTMLDivElement;
        let root = document;
        // buttons are #tab-btn-<name>
        // tabs are #tab-<name>
        for (let button of root.getElementsByClassName('sidebar-tab-btn')) {
            let name = button.id.split('tab-btn-')[1];
            let tab = root.getElementById('tab-' + name);
            this.tabs.set(as(button, HTMLButtonElement), as(tab, HTMLDivElement));
            
            this.link2(button, 'click', ()=>this.switchTab(as(button, HTMLButtonElement)));
            tab.style.display = 'none';
        }
        this.switchTab(document.getElementById('tab-btn-node-list') as HTMLButtonElement)
    }

    switchTab(button: HTMLButtonElement) {
        let tab = this.tabs.get(button)
        if(tab.style.display === 'none'){
            tab.style.display = 'block';
            button.classList.add('active');
            this.sidebarContainer.classList.remove('collapsed')
        }else{
            tab.style.display = 'none';
            button.classList.remove('active');
            this.sidebarContainer.classList.add('collapsed')
        }

        this.tabs.forEach((tab_, button) => {
            if (tab_ !== tab) {
                tab_.style.display = 'none';
                button.classList.remove('active');
            }
        });
    }

    addItem(htmlItem: HtmlItem, path: string) {
        this.nodeLibrary.addLeaf(htmlItem, path)
        this.items.push(htmlItem)
    }

    hasItem(htmlItem: HtmlItem) {
        return this.items.includes(htmlItem)
    }

    removeItem(htmlItem: HtmlItem, path: string) {
        this.nodeLibrary.removeLeaf(htmlItem, path)
        this.items.splice(this.items.indexOf(htmlItem), 1)
    }
    
}