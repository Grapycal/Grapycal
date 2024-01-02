import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic} from 'objectsync-client'

import { Node } from './sobjects/node'
import { Editor } from './sobjects/editor'
import { Root } from './sobjects/root'
import { expose, print } from './devUtils'
import { Port } from './sobjects/port'
import { Edge } from './sobjects/edge'
import { SoundManager } from './ui_utils/soundManager';
import { Sidebar } from './sobjects/sidebar'
import { WebcamStream, Workspace } from './sobjects/workspace'
import { ExtensionsSetting } from './ui_utils/extensionsSettings'
import { TextControl } from './sobjects/controls/textControl'
import { ButtonControl } from './sobjects/controls/buttonControl'
import { ImageControl } from './sobjects/controls/imageControl'
import { Footer } from './ui_utils/footer'
import { Header } from './ui_utils/header'
import { ThreeControl } from './sobjects/controls/threeControl'
import { LinePlotControl } from './sobjects/controls/linePlotControl'
import { Settings } from './sobjects/settings'
import { FetchWithCache } from './utils'
import { FileView } from './sobjects/fileView'
import { LoginApiClient } from './loginApi/loginApi'

export const soundManager = new SoundManager();

function tryReconnect(): void{
    // test websocket availability every 1 second
    const ws = new WebSocket(`ws://${location.hostname}:8765`);
    const to = setTimeout(() => {
        ws.close();
        tryReconnect();
    }, 1000);
    ws.onopen = () => {
        ws.close();
        clearTimeout(to);
        window.location.reload();
    };
}

function configureHtml(){
    
    document.addEventListener('contextmenu', function(event) {
        event.preventDefault();
    });
    
    function documentReady(callback: Function): void {
        if (document.readyState === "complete" || document.readyState === "interactive") 
            callback()
        else
            document.addEventListener("DOMContentLoaded", (event: Event) => {
                callback()
            })
    
      }
    
    let m_pos: number | undefined;
    let sidebarRight = document.getElementById('sidebar-right');
    
    const MIN_WIDTH = 10; // 最小寬度
    const MAX_WIDTH = 500; // 最大寬度  
    function resizeSidebar(event: MouseEvent): void {
        if (m_pos !== undefined) {
          const dx = m_pos - event.x;
          m_pos = event.x;
          if (sidebarRight) {
            let newWidth = sidebarRight.offsetWidth + dx;
            // 檢查是否超出最小寬度和最大寬度的範圍
            if (newWidth < MIN_WIDTH) {
              newWidth = MIN_WIDTH;
            } else if (newWidth > MAX_WIDTH) {
              newWidth = MAX_WIDTH;
            }
            sidebarRight.style.width = newWidth + 'px';
          }
        }
      }
    
    if (sidebarRight){
        sidebarRight.addEventListener('mousedown', function(event: MouseEvent) {
            if (event.offsetX < 10) {
                m_pos = event.x;
                document.addEventListener('mousemove', resizeSidebar, false);
            }
        }, false)
    
        document.addEventListener('mouseup', function(event: MouseEvent) {
            m_pos = undefined;
            document.removeEventListener('mousemove', resizeSidebar, false);
        }, false);
    }
    
    documentReady(function(event: Event) {
        document.getElementById('sidebar-collapse-right').addEventListener('click', function(event) {
            let sidebar = document.getElementById('sidebar-collapse-right').parentElement;
            if (sidebar.classList.contains('collapsed')) {
                sidebar.classList.remove('collapsed');
                document.getElementById('sidebar-collapse-right').innerText = '>'
            } else {
                sidebar.classList.add('collapsed');
                document.getElementById('sidebar-collapse-right').innerText = '<'
            }
        });  
        
        // new Header()
    })
    
    
    
}

function startObjectSync(wsUrl:string){
    const objectsync = new ObjectSyncClient(wsUrl,null,tryReconnect);

    objectsync.register(Root);
    objectsync.register(Workspace);
    objectsync.register(Editor);
    objectsync.register(Settings)
    objectsync.register(FileView)
    objectsync.register(Node);
    objectsync.register(Port);
    objectsync.register(Edge);
    objectsync.register(Sidebar);

    objectsync.register(TextControl)
    objectsync.register(ButtonControl)
    objectsync.register(ImageControl)
    objectsync.register(ThreeControl)
    objectsync.register(LinePlotControl)

    objectsync.register(WebcamStream)

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
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
        if (event.key === 'Tab') {
            event.preventDefault();
            let sidebarRight = document.getElementById('sidebar-collapse-right').parentElement;
            if (sidebarRight.classList.contains('collapsed')) {
                sidebarRight.classList.remove('collapsed');
            } else {
                sidebarRight.classList.add('collapsed');
            }
        }
    });
    
    // for debugging
    expose('o',objectsync)
}



let fetchWithCache = new FetchWithCache().fetch
export {fetchWithCache}

configureHtml();

// from webpack config files
declare var __BUILD_CONFIG__: {
    isService: boolean,
    wsPort: number
}

// webpack define plugin will replace __BUILD_CONFIG__ with the injected value
const buildConfig = __BUILD_CONFIG__ 

if (buildConfig.isService){
    // let loginApi handle login and start ObjectSync

    const loginApi = new LoginApiClient();
    loginApi.interact().then((wsUrl: string) => {
        print('got ws url from login api', wsUrl);
        startObjectSync(wsUrl);
    });
    
}else{
    // every thing else will be handled by ObjectSync.
    startObjectSync(`ws://${location.hostname}:${buildConfig.wsPort}`)
}