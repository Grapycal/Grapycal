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

export class Action<ARGS extends any[], OUT=void> {
    private _callbacks: Callback<ARGS, OUT>[] = [];

    add(callback: Callback<ARGS, OUT>) {
        this._callbacks.push(callback);
    }
    
    remove(callback: Callback<ARGS, OUT>) {
        const index = this._callbacks.indexOf(callback);
        if (index >= 0) {
            this._callbacks.splice(index, 1);
        }
    }

    invoke(...args: ARGS): OUT[] {
        return this._callbacks.map((callback) => callback(...args));
    }
}