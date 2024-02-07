import { ObjectSyncClient, ObjectTopic, StringTopic, GenericTopic, IntTopic, DictTopic} from "objectsync-client"
import { CompSObject } from "./compSObject";
import { EventDispatcher, GlobalEventDispatcher } from "../component/eventDispatcher"
import { Editor } from "./editor"
import { SelectionManager } from "../component/selectionManager"
import { Node } from "./node"
import { Edge } from "./edge"
import { Footer } from "../ui_utils/footer"
import { Buffer } from "buffer";
import { print } from "../devUtils"
import { NodeInspector } from "../ui_utils/nodeInspector"
import { PopupMenu } from "../ui_utils/popupMenu/popupMenu"
import { AppNotification } from "../ui_utils/appNotification"
import { ControlPanel } from "../ui_utils/controlPanel"

export class Workspace extends CompSObject{
    public static instance: Workspace
    readonly main_editor = this.getAttribute('main_editor', ObjectTopic<Editor>)
    readonly eventDispatcher = new EventDispatcher(this, document.getElementById('workspace'))
    // This selection manager is for the regular selecting
    readonly selection = new SelectionManager(this) 
    // This selection manager is used by attr editors in the inspector
    readonly functionalSelection = new SelectionManager(this) 
    readonly inspector = new NodeInspector()
    readonly record: ObjectSyncClient['record']
    readonly nodeTypesTopic = this.objectsync.getTopic('node_types',DictTopic<string,any>)
    readonly popupMenu = new PopupMenu()
    
    get clientId(){
        return this.objectsync.clientId
    }
    constructor(objectsync: ObjectSyncClient, id: string) {
        super(objectsync, id);
        (this.selection as any).name = 'selection';
        (this.functionalSelection as any).name = 'functionalSelection'
        this.popupMenu.hideWhenClosed = true
        
        Workspace.instance = this
        this.selection.onSelect.add((selectable)=>{
            let obj = selectable.object
            if(obj instanceof Node){
                this.inspector.addNode(obj)
            }
        })
        this.selection.onDeselect.add((selectable)=>{
            let obj = selectable.object
            if(obj instanceof Node){
                this.inspector.removeNode(obj)
            }
        })
        this.functionalSelection.enabled = false
        this.record = objectsync.record
    }
    protected onStart(): void {
        this.main_editor.getValue().eventDispatcher.onClick.add(()=>{
            if(GlobalEventDispatcher.instance.isKeyDown('Control')) return;
            if(GlobalEventDispatcher.instance.isKeyDown('Shift')) return;
            this.selection.clearSelection()
        })

        new Footer()
        Footer.setStatus('Workspace loaded. Have fun!')
        new AppNotification()
        new ControlPanel()
    }

    public openWorkspace(path:string){
        this.objectsync.emit('open_workspace',{path:path})
    }
}

export class WebcamStream extends CompSObject{
        image: StringTopic
    sourceClient: IntTopic
    stream: MediaStream = null
    interval:number = 200
    timer: NodeJS.Timeout
    
    protected onStart(): void {
        // (navigator.mediaDevices as any).getUserMedia = (navigator.mediaDevices as any).getUserMedia || (navigator.mediaDevices as any).webkitGetUserMedia || (navigator.mediaDevices as any).mozGetUserMedia || (navigator.mediaDevices as any).msGetUserMedia
        
        this.image = this.getAttribute('image', StringTopic)
        this.sourceClient = this.getAttribute('source_client', IntTopic)
        this.sourceClient.onSet.add((sourceClient)=>{
            if(sourceClient == Workspace.instance.clientId){
                this.startStreaming()
            }else{
                this.stopStreaming()
            }
        })
    }

    private startStreaming(){
        if (this.stream) return;
        (navigator.mediaDevices as any).getUserMedia( {video: { width: 480, height: 320 }, audio: false})
        .then((stream: MediaStream) => {
            console.log('got stream')
            this.stream = stream
            // start loop
            this.timer = setInterval(()=>{
                this.publish()
            },this.interval)
            video.srcObject = stream;

            video.setAttribute('autoplay', 'true');
            video.onloadeddata = () => {
            
                video.play();
            }
        })
        .catch(function(err: any) {
            console.error(err);
        })
    }

    private publish(){
        let image = getImageFromStream(this.stream)
        image.then((blob: Blob)=>{
            let reader = new FileReader()
            reader.onload = (event) => {
                let buf =Buffer.from( reader.result as ArrayBuffer)
                var base64String = buf.toString('base64')
                this.image.set(base64String)
            }
            reader.readAsArrayBuffer(blob)
        })
    }

    private stopStreaming(){
        if(this.stream==null) return;
        clearInterval(this.timer)
        this.stream = null
    }


}

const video = document.createElement('video');
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');

//https://stackoverflow.com/questions/62446301/alternative-for-the-imagecapture-api-for-better-browser-support
function getImageFromStream(stream: MediaStream) {

  if (false && 'ImageCapture' in window) {

    const videoTrack = stream.getVideoTracks()[0];
    const imageCapture = new (window as any).ImageCapture(videoTrack);
    return imageCapture.takePhoto({imageWidth: 48, imageHeight: 32});
    
  } else {



    return new Promise((resolve, reject) => {
        //const { videoWidth, videoHeight } = video;
        const { videoWidth, videoHeight } = {videoWidth: 480, videoHeight: 320};
        canvas.width = videoWidth;
        canvas.height = videoHeight;

        try {
          context.drawImage(video, 0, 0, videoWidth, videoHeight);
          canvas.toBlob(resolve, 'image/jpg');
        } catch (error) {
          reject(error);
        }
      });
  }
  
}