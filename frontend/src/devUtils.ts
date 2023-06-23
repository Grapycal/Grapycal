export function expose(name:string,object: any): void {
    (window as any)[name] = object;
}

export function print(...args: any[]): void {
    console.log(...args);
}

expose('print', print);