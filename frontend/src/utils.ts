import { print } from "./devUtils"

export { Action } from "objectsync-client"

export function defined<T>(value: T | undefined| null): T {
    if (value === undefined) {
        throw new Error("Value is undefined");
    }
    if (value === null) {
        throw new Error("Value is null");
    }
    return value as T;
}

export type Constructor<T> = new (...args: any[]) => T;

export function as <T>(value: any, type: Constructor<T>): T {
    if (value instanceof type)
        return value;
    if (value === null)
        return null;
    throw new Error(`Value ${value} is not instance of ${type.name}`);
}

export abstract class ContextManager{
    with(callback: () => void): void{
        this.enter();
        try {
            callback();
        }
        finally {
            this.exit();
        }
    }
    abstract enter(): void;
    abstract exit(): void;
}


type Callback<ARGS extends any[], OUT> = (...args: ARGS) => OUT;



export class Vector2 {

    static get zero(): Vector2{
        return new Vector2(0, 0);
    }

    static get one(): Vector2{
        return new Vector2(1, 1);
    }

    static get up(): Vector2{
        return new Vector2(0, 1);
    }

    static get down(): Vector2{
        return new Vector2(0, -1);
    }

    static get left(): Vector2{
        return new Vector2(-1, 0);
    }

    static get right(): Vector2{
        return new Vector2(1, 0);
    }

    x: number;
    y: number;
    constructor(x: number, y: number){
        this.x = x;
        this.y = y;
    }
    distanceTo(other: Vector2): number{
        return Math.sqrt((this.x - other.x)**2 + (this.y - other.y)**2);
    }
    add(other: Vector2): Vector2{
        return new Vector2(this.x + other.x, this.y + other.y);
    }
    sub(other: Vector2): Vector2{
        return new Vector2(this.x - other.x, this.y - other.y);
    }
    mul(other: Vector2): Vector2{
        return new Vector2(this.x * other.x, this.y * other.y);
    }
    mulScalar(scalar: number): Vector2{
        return new Vector2(this.x * scalar, this.y * scalar);
    }

    static fromString(str: string): Vector2{
        const [x, y] = str.split(',').map(parseFloat);
        return new Vector2(x, y);
    }

    toString(): string{
        return `${this.x},${this.y}`;
    }

    equals(another:Vector2){
        return this.x == another.x && this.y == another.y
    }
}

export function addPrefixToCssClasses(css: string, prefix: string): string{
    return css.replace(/\.([a-zA-Z0-9_-]+)[ ]*\{/g, (match, className) => {
        return `.${prefix}-${className}{`;
    });
}

export function addPrefixToHtmlClasses(html: Element, prefix: string): void{
    let target:Element|DocumentFragment = html;
    if(html instanceof HTMLTemplateElement)
        target = html.content;
    target.querySelectorAll('[class]').forEach(element => {
        const classList = element.classList;
        classList.forEach(className => {
            // The original class is preserved. For example, .class becomes .class .prefix-class
            // The original class is used by the theme css.
            classList.add(`${prefix}-${className}`);
        });
    });
}

export function addCssToDocument(css:string){
    var style = document.createElement('style')
    style.innerHTML = css
    document.head.prepend(style) // allow overriding by theme css
}

export function getStaticField(object: any, fieldName: string): any {
    return object.constructor[fieldName];
}