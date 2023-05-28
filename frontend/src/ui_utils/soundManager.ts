import { as } from "../utils"

export class SoundManager {
    click: HTMLAudioElement;
    constructor() {
        this.click = new Audio("click.mp3");
        this.click.volume = 0.2;
    }
    playClick() {
        let tmp = as(this.click.cloneNode(true),HTMLAudioElement)
        tmp.volume = 0.2;
        tmp.play()
    }
}