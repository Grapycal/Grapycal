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
import { OptionControl } from './sobjects/controls/optionControl'
import { AppNotification } from './ui_utils/appNotification'

export const soundManager = new SoundManager();

function tryReconnect(): void{
    if(Workspace.instance != null)
        Workspace.instance.appNotif.add('Connection to server lost. Reconnecting...',4000)
    fetch(`http://${location.hostname}:8765`, {
        method: "GET",
        signal: AbortSignal.timeout(2000),
        mode: 'no-cors'
    })
    .then((response) => {
        window.location.reload();
    })
    .catch((error) => {
        print('failed to reconnect');
        // wait for 2 seconds before trying again
        setTimeout(tryReconnect, 2000);
    });
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

    let desiredWidth: number = null;
    let prevX: number = null;
    let sidebarRight = document.getElementById('sidebar-right');

    const MIN_WIDTH = 10; // 最小寬度
    const MAX_WIDTH = 500; // 最大寬度
    function resizeSidebar(event: MouseEvent): void {
        event.preventDefault(); // prevents selecting text
        if (desiredWidth != null && sidebarRight) {
            desiredWidth -= event.x - prevX;
            prevX = event.x;
            let newWidth = desiredWidth;
            // 檢查是否超出最小寬度和最大寬度的範圍
            if (newWidth < MIN_WIDTH) {
              newWidth = MIN_WIDTH;
            } else if (newWidth > MAX_WIDTH) {
              newWidth = MAX_WIDTH;
            }
            sidebarRight.style.width = newWidth + 'px';
        }
      }

    if (sidebarRight){
        document.getElementById('sidebar-resize-handle').addEventListener('mousedown', function(event: MouseEvent) {
            desiredWidth = sidebarRight.offsetWidth;
            prevX = event.x;
            document.addEventListener('mousemove', resizeSidebar, false);
        }, false)

        document.addEventListener('mouseup', function(event: MouseEvent) {
            desiredWidth = undefined;
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
    objectsync.register(OptionControl)

    objectsync.register(WebcamStream)

    setTimeout(() => { // fix this
        new ExtensionsSetting(objectsync);
    }, 200);


    document.addEventListener('keydown', function(event) {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() == 'z') {
            event.preventDefault();
            objectsync.undo(null);
        }
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() == 'y') {
            event.preventDefault();
            objectsync.redo(null);
        }
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() == 's') {
            event.preventDefault();
            objectsync.emit('ctrl+s');
        }
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() == 'q') {
            event.preventDefault();
            objectsync.makeRequest('exit');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    },{capture: true});

    // for debugging
    expose('o',objectsync)
}



const fetchWithCache = new FetchWithCache().fetch
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
    // // let loginApi handle login and start ObjectSync

    // const loginApi = new LoginApiClient();
    // loginApi.interact().then((wsUrl: string) => {
    //     print('got ws url from login api', wsUrl);
    //     startObjectSync(wsUrl);
    // });

    // We have not made the api yet, so we will just use the ws url directly
    startObjectSync(`wss://workspace.grapycal.org`)

}else{
    // every thing else will be handled by ObjectSync.
    startObjectSync(`ws://${location.hostname}:${buildConfig.wsPort}`)
}
