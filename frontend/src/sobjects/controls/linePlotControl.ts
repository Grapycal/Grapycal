import * as THREE from 'three';
import { Control } from './control'
import { DictTopic, ListTopic } from 'objectsync-client'
import { print } from '../../devUtils'
import { EventDispatcher } from '../../component/eventDispatcher'
import { Vector2 } from '../../utils'

enum YAxisType {
    Linear,
    Log
}
    
export class LinePlotControl extends Control{
    protected template = `
        <div class="control">
            <div class="label-container"></div>
        </div>
    `
    protected css = `
    .control{
        position:relative;
    }
    .label-container{
        position:absolute;
        top:0;
        left:0;
        width:100%;
        height:100%;
        transform:translate(50%,50%);
    }
    .label-container .label{
        color:var(--text-high);
        position:absolute;
        font-size:7px;
    }
    `
    private scene: THREE.Scene
    private camera: THREE.OrthographicCamera
    private renderer: THREE.WebGLRenderer
    private baseObject: THREE.Object3D
    private objectsDirty = false;
    private renderDirty = false;

    private linesTopic = this.getAttribute('lines', ListTopic<string>)
    disc: THREE.Texture

    private eventDispatcher: EventDispatcher;
    pointCloud: THREE.Points<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.PointsMaterial>
    lines: Map<string,THREE.Line<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.LineBasicMaterial>> = new Map()
    grid: THREE.LineSegments<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.LineBasicMaterial>
    labelContainer: HTMLDivElement

    yaxisType: YAxisType = YAxisType.Linear;

    debugSphere: THREE.Mesh<THREE.SphereGeometry, THREE.MeshBasicMaterial>

    size = new THREE.Vector3(320,180);

    boundary: Map<string,THREE.Box3> = new Map()
    fitting = true

    protected onStart(): void {
        super.onStart();
        if(this.node.isPreview) return;
        this.eventDispatcher = new EventDispatcher(this, this.htmlItem.baseElement as HTMLDivElement);
        this.labelContainer = this.htmlItem.getHtmlElByClass('label-container') as HTMLDivElement;

        this.disc = new THREE.TextureLoader().load( 'disc.png' );
        this.disc.colorSpace = THREE.SRGBColorSpace;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color( 0x222222 );
        this.camera = new THREE.OrthographicCamera( this.size.x / - 2, this.size.x / 2, this.size.y / 2, this.size.y / - 2, 1, 1000 );
        this.camera.position.z = 800;

        this.renderer = new THREE.WebGLRenderer();
        this.renderer.setSize(320,180);
        this.htmlItem.baseElement.prepend( this.renderer.domElement );

        this.baseObject = new THREE.Object3D();
        this.baseObject.scale.set(300,300,300)
        this.baseObject.position.set(0,0,0)

        const axesHelper = new THREE.AxesHelper( 2 );
        axesHelper.position.set(0,0,0);
        this.baseObject.add( axesHelper );

        // this.debugSphere = new THREE.Mesh( new THREE.SphereGeometry( 0.02, 8, 8 ), new THREE.MeshBasicMaterial( { color: 0xff0000 } ) );
        // this.debugSphere.position.set(0,0,0);
        // this.baseObject.add( this.debugSphere );

        this.addGrid();
        this.addAxis();

        this.scene.add( this.baseObject );

        this.setRenderDirty();

        for(const name of this.linesTopic.getValue()){
            this.addLine(name);
        }
        this.link(this.linesTopic.onInsert,this.addLine)

        this.on('add_points',({name,xs,ys}:{name:string,xs:number[],ys:number[]})=>{
            const boundary = this.boundary.get(name);
            const line = this.lines.get(name)
            const positionAttribute = line.geometry.getAttribute( 'position' );
            const orig_length = line.geometry.drawRange.count;
            for(let i=0; i<xs.length; i++){
                positionAttribute.setXYZ(orig_length+i,xs[i],ys[i],0);
                boundary.expandByPoint(new THREE.Vector3(xs[i],ys[i],0))
            }
            line.geometry.setDrawRange(0,orig_length+xs.length)
            this.setRenderDirty();
            line.geometry.attributes.position.needsUpdate = true;
            line.geometry.computeBoundingSphere();
            this.fitBoundary();
        })

        this.on('clear',({name}:{name:string})=>{
            const line = this.lines.get(name)
            line.geometry.setDrawRange(0,0)
            line.geometry.attributes.position.needsUpdate = true;
            line.geometry.computeBoundingSphere();
            this.boundary.set(name,new THREE.Box3());
            this.fitBoundary();
            this.setRenderDirty();
        })

        this.linesTopic.onPop.add((name:string)=>{
            const line = this.lines.get(name)
            this.baseObject.remove(line);
            this.lines.delete(name);
            this.boundary.delete(name);
            this.fitBoundary();
            this.setRenderDirty();
        })

        this.link(this.eventDispatcher.onDrag,(e:MouseEvent,begin:Vector2,end:Vector2)=>{
            //move the base object
            const nodeScale = this.node.transform.getAbsoluteScale().x;
            const delta = end.sub(begin).mulScalar(1/nodeScale);
            this.baseObject.translateX(-delta.x);
            this.baseObject.translateY(delta.y);
            this.fitting = false;
            this.updateGrid();
            this.setRenderDirty();
        })

        this.link(this.eventDispatcher.onScroll,(e:WheelEvent)=>{
            //rotate the base object
            const delta = e.deltaY;
            const zoom = 10**(-delta/1000);
            const originalMousePos = this.getMousePos(e);
            if(e.ctrlKey){
                this.baseObject.scale.multiply(new THREE.Vector3(zoom,1,1));
            }
            if(e.shiftKey){
                this.baseObject.scale.multiply(new THREE.Vector3(1,zoom,1));
            }
            if(e.ctrlKey || e.shiftKey){

                //move the base object so that the mouse position is fixed
                const newMousePos = this.getMousePos(e);
                const delta = newMousePos.sub(originalMousePos).multiply(this.baseObject.scale);
                this.baseObject.position.add(delta);

                e.stopPropagation();
                e.preventDefault();
                this.fitting = false;
                this.updateGrid();
                this.setRenderDirty();
            }
        })

        this.link(this.node.editor.transform.scaleChanged,(scale:number)=>{
            //this.updateGrid();
            this.setRenderDirty();
        })
        this.link(this.eventDispatcher.onDoubleClick,()=>{
            this.fitting = true;
            this.fitBoundary();
        })
    }

    getMousePos(e:MouseEvent): THREE.Vector3 {
        let tmp = this.node.transform.WroldToEl(this.eventDispatcher.mousePos,this.renderer.domElement)
        const originalMousePos = new THREE.Vector3(tmp.x,tmp.y,0).sub(this.size.clone().divideScalar(2))
        .multiply(new THREE.Vector3(1,-1,1))
        .sub(this.baseObject.position).divide(this.baseObject.scale);
        return originalMousePos;
    }

    addGrid(): void {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(500*3);
        geometry.setAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
        geometry.setDrawRange(0,0)
        
        const material = new THREE.LineBasicMaterial( { color: 0x444444 } );
        const grid = new THREE.LineSegments( geometry, material );
        this.grid = grid;
        this.scene.add(grid);
        this.updateGrid();
    }

    addAxis(){
        // x and y axis, two lines

        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array([
            -10000,0,0,
            10000,0,0,
            0,-10000,0,
            0,10000,0,
        ]);
        geometry.setAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
        geometry.setDrawRange(0,4)

        const material = new THREE.LineBasicMaterial( { color: 0x888888, linewidth:2 } );
        const axis = new THREE.LineSegments( geometry, material );
        this.baseObject.add(axis);
    }

    updateGrid(): void {
        const geometry = this.grid.geometry;
        const positionAttribute = geometry.getAttribute( 'position' );

        this.labelContainer.innerHTML = '';
        let i = 0;
        i = this.updateGridOneAxis('y',positionAttribute,i);
        i = this.updateGridOneAxis('x',positionAttribute,i);
        
        this.grid.geometry.computeBoundingSphere();
        this.grid.geometry.attributes.position.needsUpdate = true;
    }

    private removeTrailingZeros(str:string): string {
        while(str[str.length-1] == '0'){
            str = str.slice(0,str.length-1);
        }
        if(str[str.length-1] == '.'){
            str = str.slice(0,str.length-1);
        }
        return str;
    }

    private toScientificNotation(x:number,zeroThres:number=1e-14): string {
        if(Math.abs(x) < zeroThres) return '0';
        const exponent = Math.floor(Math.log10(Math.abs(x)));
        const mantissa = x/Math.pow(10,exponent);


        if(Math.abs(exponent) < 3) return this.removeTrailingZeros(x.toFixed(2));
        
        let mantissaStr = mantissa.toFixed(2);
        mantissaStr = this.removeTrailingZeros(mantissaStr);

        
        return mantissaStr + 'e' + exponent;
    }

    updateGridOneAxis(axis:'x'|'y',positionAttribute:THREE.BufferAttribute|THREE.InterleavedBufferAttribute,bufferStartPos:number,desity = 4): number {
        const nodeScale = this.node.transform.getAbsoluteScale().x;
        //desity = desity*nodeScale;
        const start = (-this.size[axis]/2-this.baseObject.position[axis])/this.baseObject.scale[axis]
        const end = (this.size[axis]/2-this.baseObject.position[axis])/this.baseObject.scale[axis]
        const logGap = Math.log10(200/this.baseObject.scale[axis]/desity)
        let logGapQuantized = Math.floor(logGap)
        // increase yGap to 2 or 5 if possible
        const log2 = Math.log10(2)
        const log5 = Math.log10(5)
        if(logGap-logGapQuantized > log5){
            logGapQuantized = logGapQuantized + log5
        } 
        else if(logGap-logGapQuantized > log2){
            logGapQuantized = logGapQuantized + log2
        }
        const gap = Math.pow(10,logGapQuantized)

        const screenGap = gap*this.baseObject.scale[axis]
        const screenStart = Math.floor(start/gap)*gap*this.baseObject.scale[axis]+this.baseObject.position[axis]
        const screenEnd = Math.ceil(end/gap)*gap*this.baseObject.scale[axis]+this.baseObject.position[axis]

        let i = bufferStartPos;
        for(let x=screenStart; x<=screenEnd; x+=screenGap){
            if(axis == 'x'){
                positionAttribute.setXYZ(i++,x,-this.size.y/2,0);
                positionAttribute.setXYZ(i++,x,this.size.y/2,0);
                const newLabel = document.createElement('div');
                newLabel.classList.add('LinePlotControl-label');
                newLabel.innerText = this.toScientificNotation((x-this.baseObject.position[axis])/this.baseObject.scale[axis],gap*1e-10)
                newLabel.style.transform = `translate(${x+2}px,${this.size.y/2-8}px)`;
                this.labelContainer.appendChild(newLabel);
            }
            else{
                positionAttribute.setXYZ(i++,-this.size.x/2,x,0);
                positionAttribute.setXYZ(i++,this.size.x/2,x,0);
                const newLabel = document.createElement('div');
                newLabel.classList.add('LinePlotControl-label');
                newLabel.innerText = this.toScientificNotation((x-this.baseObject.position[axis])/this.baseObject.scale[axis],gap*1e-10)
                newLabel.style.transform = `translate(${-this.size.x/2+2}px,${-x-8}px)`;
                this.labelContainer.appendChild(newLabel);
            }
        }
        this.grid.geometry.setDrawRange(0,i)
        return i;
    }

    addLine(name:string): void {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(500*3);
        geometry.setAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
        geometry.setDrawRange(0,0)
        
        const material = new THREE.LineBasicMaterial( { color: 0x33ff33 } );
        const line = new THREE.Line( geometry, material );
        this.baseObject.add( line );
        this.lines.set(name,line);
        this.boundary.set(name,new THREE.Box3());
    }

    setRenderDirty(): void {
        if(this.renderDirty) return;
        this.renderDirty = true;
        requestAnimationFrame(()=>{
            this.render();
            this.renderDirty = false;
        });
    }

    private render(): void {
        const nodeScale = this.node.transform.getAbsoluteScale().x;
        const w = nodeScale*320;
        const h = nodeScale*180;
        this.renderer.setSize( w,h );
        this.renderer.domElement.style.transform = `translate(${-w/2}px,${-h/2}px)  scale(${1/nodeScale}) translate(${w/2}px,${h/2}px) `;
        (this.htmlItem.baseElement as HTMLDivElement).style.width = '320px';
        (this.htmlItem.baseElement as HTMLDivElement).style.height = '180px';
        this.renderer.render( this.scene, this.camera );
    }

    private fitBoundary(): void {
        if(!this.fitting) return;
        const boundary = new THREE.Box3();
        for(const b of this.boundary.values()){
            boundary.union(b);
        }
        //padding
        boundary.expandByVector(boundary.getSize(new THREE.Vector3()).multiplyScalar(0.05));
        if(boundary.isEmpty()) return;
        const size = boundary.getSize(new THREE.Vector3());
        const scale = this.size.clone().divide(size)
        this.baseObject.scale.set(scale.x,scale.y,1);
        const pos = boundary.min.multiply(scale).multiplyScalar(-1).sub(this.size.clone().divideScalar(2))
        this.baseObject.position.set(pos.x,pos.y,0);
        this.updateGrid();
        this.setRenderDirty();
    }

}