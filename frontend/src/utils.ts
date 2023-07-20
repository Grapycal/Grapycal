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
}