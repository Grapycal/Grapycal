import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic} from 'objectsync-client'

import { Node } from './sobjects/node'
import { Editor } from './ui_utils/editor'
import { Root } from './sobjects/root'
import { expose } from './devUtils'
import { Port } from './sobjects/port'
import { Edge } from './sobjects/edge'
import { SoundManager } from './ui_utils/soundManager';
import { Sidebar } from './sobjects/sidebar'
import { Workspace } from './sobjects/workspace'
import { ExtensionsSetting } from './ui_utils/extensionsSettings'
import { TextControl } from './sobjects/controls/textControl'

export const editor = new Editor();

export const soundManager = new SoundManager();

//const objectsync = new ObjectSyncClient('ws://192.168.245.187:8765');
const objectsync = new ObjectSyncClient('ws://localhost:8765');
objectsync.register(Root);
objectsync.register(Workspace);
objectsync.register(Node);
objectsync.register(Port);
objectsync.register(Edge);
objectsync.register(Sidebar);

objectsync.register(TextControl)


new ExtensionsSetting(objectsync);


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
});

document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
});

expose('c',objectsync)