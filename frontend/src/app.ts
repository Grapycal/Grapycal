import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic} from 'objectsync-client'

import { Node } from './sobjects/node'
import { Editor } from './sobjects/editor'
import { Root } from './sobjects/root'
import { expose } from './devUtils'
import { Port } from './sobjects/port'
import { Edge } from './sobjects/edge'
import { SoundManager } from './ui_utils/soundManager';
import { Sidebar } from './sobjects/sidebar'
import { Workspace } from './sobjects/workspace'
import { ExtensionsSetting } from './ui_utils/extensionsSettings'
import { TextControl } from './sobjects/controls/textControl'
import { ButtonControl } from './sobjects/controls/buttonControl'
import { ImageControl } from './sobjects/controls/imageControl'
import { Callback } from 'chatroom-client/src/utils'

export const soundManager = new SoundManager();

let host = location.hostname;
const objectsync = new ObjectSyncClient(`ws://${host}:8765`);

objectsync.register(Root);
objectsync.register(Workspace);
objectsync.register(Editor);
objectsync.register(Node);
objectsync.register(Port);
objectsync.register(Edge);
objectsync.register(Sidebar);

objectsync.register(TextControl)
objectsync.register(ButtonControl)
objectsync.register(ImageControl)

setTimeout(() => { // fix this
    new ExtensionsSetting(objectsync);
}, 200);


document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'z' || event.metaKey && event.key === 'Z') {
        event.preventDefault();
        objectsync.undo(null);
    }
    if (event.ctrlKey && event.key === 'y' || event.metaKey && event.key === 'Y') {
        event.preventDefault();
        objectsync.redo(null);
    }
    if (event.ctrlKey && event.key === 's' || event.metaKey && event.key === 'S') {
        event.preventDefault();
        objectsync.emit('ctrl+s');
    }
    if (event.ctrlKey && event.key === 'q' || event.metaKey && event.key === 'Q') {
        event.preventDefault();
        objectsync.makeRequest('exit');
        //reload page
        setTimeout(() => {
            
            window.location.reload();
        }, 1000);
    }
    if (event.key === 'Tab') {
        event.preventDefault();
        let sidebar = document.getElementById('sidebar-collapse-right').parentElement;
        console.log(sidebar.classList);
        if (sidebar.classList.contains('collapsed')) {
            sidebar.classList.remove('collapsed');
        } else {
            sidebar.classList.add('collapsed');
        }
    }
});

document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
});

function documentReady(callback: Callback): void {
    if (document.readyState === "complete" || document.readyState === "interactive") 
        callback()
    else
        document.addEventListener("DOMContentLoaded", (event: Event) => {
            callback()
        })

  }

documentReady(function(event) {
    document.getElementById('sidebar-collapse-left').addEventListener('click', function(event) {
        let sidebar = document.getElementById('sidebar-collapse-left').parentElement;
        console.log(sidebar.classList);
        if (sidebar.classList.contains('collapsed')) {
            sidebar.classList.remove('collapsed');
        } else {
            sidebar.classList.add('collapsed');
        }   
    });

    document.getElementById('sidebar-collapse-right').addEventListener('click', function(event) {
        let sidebar = document.getElementById('sidebar-collapse-right').parentElement;
        console.log(sidebar.classList);
        if (sidebar.classList.contains('collapsed')) {
            sidebar.classList.remove('collapsed');
        } else {
            sidebar.classList.add('collapsed');
        }
    });  
})



expose('c',objectsync)