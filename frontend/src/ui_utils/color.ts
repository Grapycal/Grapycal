export class Color{
    r: number;
    g: number;
    b: number;
    a: number;
    get h(): number{
        const max = Math.max(this.r, this.g, this.b);
        const min = Math.min(this.r, this.g, this.b);
        const delta = max - min;
        if (delta == 0){
            return 0;
        }else if (max == this.r){
            return 60 * (((this.g - this.b) / delta)+ (this.g < this.b ? 6 : 0))/360;
        }else if (max == this.g){
            return 60 * (((this.b - this.r) / delta) + 2)/360;
        }else if (max == this.b){
            return 60 * (((this.r - this.g) / delta) + 4)/360;
        }else{
            throw new Error('unreachable');
        }
    }

    get s(): number{
        const max = Math.max(this.r, this.g, this.b);
        const min = Math.min(this.r, this.g, this.b);
        const delta = max - min;
        return this.l > 0.5 ? delta / (2 - max - min) : delta / (max + min);
    }

    // get v(): number{
    //     return Math.max(this.r, this.g, this.b);
    // }

    get l(): number{
        const max = Math.max(this.r, this.g, this.b);
        const min = Math.min(this.r, this.g, this.b);
        return (max + min) / 2;
    }

    static fromHsv(h: number, s: number, v: number, a: number = 1): Color{
        const c = v * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = v - c;
        let r = 0;
        let g = 0;
        let b = 0;
        if (h < 60){
            r = c;
            g = x;
        }else if (h < 120){
            r = x;
            g = c;
        }else if (h < 180){
            g = c;
            b = x;
        }else if (h < 240){
            g = x;
            b = c;
        }else if (h < 300){
            r = x;
            b = c;
        }else if (h < 360){
            r = c;
            b = x;
        }else{
            throw new Error('unreachable');
        }
        return new Color(r + m, g + m, b + m, a);
    }

    static fromHsl(h: number, s: number, l: number, a: number = 1): Color{
        function hueToRgb(p: number, q: number, t: number) {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1/6) return p + (q - p) * 6 * t;
            if (t < 1/2) return q;
            if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
        }

        let r, g, b;
      
        if (s === 0) {
          r = g = b = l; // achromatic
        } else {
          const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
          const p = 2 * l - q;
          r = hueToRgb(p, q, h + 1/3);
          g = hueToRgb(p, q, h);
          b = hueToRgb(p, q, h - 1/3);
        }
      
        return new Color(r, g, b, a);
    }
      
      


    static fromHex(hex: string): Color{
        if (hex.length == 7){
            return new Color(
                parseInt(hex.slice(1,3),16)/255,
                parseInt(hex.slice(3,5),16)/255,
                parseInt(hex.slice(5,7),16)/255,
            );
        }else if (hex.length == 9){
            return new Color(
                parseInt(hex.slice(1,3),16)/255,
                parseInt(hex.slice(3,5),16)/255,
                parseInt(hex.slice(5,7),16)/255,
                parseInt(hex.slice(7,9),16)/255,
            );
        }else{
            throw new Error('invalid hex');
        }
    }

    static fromString(str: string): Color{
        if (str.startsWith('#')){
            return Color.fromHex(str);
        }else if (str.startsWith('rgba')){
            str = str.replace(/\s/g,'');
            const match = str.match(/rgba?\((\d+),(\d+),(\d+)(?:,(\d+))?\)/);
            if (match){
                return new Color(
                    parseInt(match[1])/255,
                    parseInt(match[2])/255,
                    parseInt(match[3])/255,
                    parseInt(match[4])/255,
                );
            }else{
                throw new Error('invalid rgb');
            }
        }else if (str.startsWith('rgb')){
            //remove spaces
            str = str.replace(/\s/g,'');
            const match = str.match(/rgb\((\d+),(\d+),(\d+)\)/);
            if (match){
                return new Color(
                    parseInt(match[1])/255,
                    parseInt(match[2])/255,
                    parseInt(match[3])/255,
                );
            }else{
                throw new Error('invalid rgb');
            }
        }else{
            throw new Error('invalid color string');
        }
    }
    

    constructor(r: number, g: number, b: number, a: number = 1){
        this.r = r;
        this.g = g;
        this.b = b;
        this.a = a;
    }
    toHex(): string{
        // convert [0,1] to [0,255] int
        const r = Math.round(this.r*255);
        const g = Math.round(this.g*255);
        const b = Math.round(this.b*255);
        const a = Math.round(this.a*255);
        return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}${a.toString(16).padStart(2,'0')}`;
    }
    

}

(window as any).co = Color;