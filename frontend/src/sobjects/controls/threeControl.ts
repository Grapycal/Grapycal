import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';
import { Control } from './control'
import { ListTopic } from 'objectsync-client'
import { print } from '../../devUtils'
import { EventDispatcher } from '../../component/eventDispatcher'
import { Vector2 } from '../../utils'

export class ThreeControl extends Control{
    protected template = `<div class="control"></div>`
    private scene: THREE.Scene
    private camera: THREE.PerspectiveCamera
    private renderer: THREE.WebGLRenderer
    private baseObject: THREE.Object3D
    private dirty = false;

    private points = this.getAttribute('points', ListTopic<[number,number,number]>)
    private lines = this.getAttribute('lines', ListTopic<[number,number,number,number,number,number]>)
    disc: THREE.Texture

    private eventDispatcher: EventDispatcher;
    pointCloud: THREE.Points<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.PointsMaterial>
    line: THREE.LineSegments<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.LineBasicMaterial>

    protected onStart(): void {
        super.onStart();
        this.eventDispatcher = new EventDispatcher(this, this.htmlItem.baseElement as HTMLDivElement);
        
        this.points.onSet.add(()=>this.dirty = true)

        this.disc = new THREE.TextureLoader().load( 'disc.png' );
        this.disc.colorSpace = THREE.SRGBColorSpace;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color( 0x222222 );
        this.camera = new THREE.PerspectiveCamera( 60, 320/180, 0.1, 2000 );

        this.renderer = new THREE.WebGLRenderer();
        this.renderer.setSize(320,180);
        this.htmlItem.baseElement.appendChild( this.renderer.domElement );

        this.baseObject = new THREE.Object3D();
        this.baseObject.scale.set(300,300,300)
        this.baseObject.position.set(0,0,0)
        const geo = new THREE.PlaneGeometry(3,3, 8, 8);
        const mat = new THREE.MeshBasicMaterial({ color: 0x604530 });
        const plane = new THREE.Mesh(geo, mat);
        plane.rotateX( - Math.PI / 2);
        plane.position.set(0,-1,0);
        this.baseObject.add(plane);

        const axesHelper = new THREE.AxesHelper( 1 );
        axesHelper.position.set(-1,-0.9,-1);
        this.baseObject.add( axesHelper );


        this.scene.add( this.baseObject );

        //light
        const light = new THREE.DirectionalLight( 0xffffff, 0.5 );
        light.position.set( 1, 1, 1 );
        this.scene.add( light );


        this.camera.position.z = 800;

        requestAnimationFrame( this.animate.bind(this) );

        this.link(this.eventDispatcher.onDrag,(e:MouseEvent,begin:Vector2,end:Vector2)=>{
            //rotate the base object
            const delta = end.sub(begin);
            this.baseObject.rotation.y += delta.x/100;
            this.baseObject.rotation.x += delta.y/100;
            // this.baseObject.rotateOnWorldAxis(new THREE.Vector3(0,-1,0),delta.x/100);
            // this.baseObject.rotateOnWorldAxis(new THREE.Vector3(-1,0,0),delta.y/100);
        })
       
    }
    private animate(): void {
        if(this.destroyed) return;
        requestAnimationFrame( this.animate.bind(this) );
        if(this.dirty){
            this.updateObjects();
            this.dirty = false;
        }
        const rect = (this.htmlItem.baseElement as HTMLDivElement).getBoundingClientRect()
        const nodeScale = this.node.transform.getAbsoluteScale().x;
        const w = nodeScale*320;
        const h = nodeScale*180;
        // this.baseObject.rotation.y += 0.01;
        // this.camera.position.set(
        //     // -(rect.x-window.innerWidth/2+w/2)/nodeScale,
        //     // (rect.y-window.innerHeight/2+h/2)/nodeScale,
        //     0,0,
        //     500/nodeScale
        // );
        // this.camera.fov = 2*Math.atan(180/2/(500/nodeScale))*180/Math.PI;
        this.renderer.setSize( w,h );
        this.renderer.domElement.style.transform = `translate(${-w/2}px,${-h/2}px)  scale(${1/nodeScale}) translate(${w/2}px,${h/2}px) `;
        (this.htmlItem.baseElement as HTMLDivElement).style.width = '320px';
        (this.htmlItem.baseElement as HTMLDivElement).style.height = '180px';
        this.renderer.render( this.scene, this.camera );
    }

    private updateObjects(): void {
        this.baseObject.remove(this.pointCloud);
        this.baseObject.remove(this.line);
        
        const points = this.points.getValue();
        const lines = this.lines.getValue();

        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(points.length*3);
        for(let i=0; i<points.length; i++){
            positions[i*3] = points[i][0];
            positions[i*3+1] = points[i][1];
            positions[i*3+2] = points[i][2];
        }

        geometry.setAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
        geometry.computeBoundingSphere();
        const material = new THREE.PointsMaterial( { color: 0x918532,size:20,map:this.disc,alphaTest: 0.5,transparent:true} );
        this.pointCloud = new THREE.Points( geometry, material );
        this.baseObject.add( this.pointCloud );

        const lineGeometry = new THREE.BufferGeometry();
        const linePositions = new Float32Array(lines.length*3*2);

        for(let i=0; i<lines.length; i++){
            linePositions[i*6] = lines[i][0];
            linePositions[i*6+1] = lines[i][1];
            linePositions[i*6+2] = lines[i][2];
            linePositions[i*6+3] = lines[i][3];
            linePositions[i*6+4] = lines[i][4];
            linePositions[i*6+5] = lines[i][5];
        }

        lineGeometry.setAttribute( 'position', new THREE.BufferAttribute( linePositions, 3 ) );
        lineGeometry.computeBoundingSphere();
        const lineMaterial = new THREE.LineBasicMaterial( { color: 0x888888 } );
        this.line = new THREE.LineSegments( lineGeometry, lineMaterial );
        this.baseObject.add( this.line );
    }
}