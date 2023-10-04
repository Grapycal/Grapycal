import { print } from "../devUtils"
import { Color } from "./color"


export function bloomDiv(borderDiv: HTMLElement,textDiv: HTMLElement) {
    //get border color
    const borderColor = window.getComputedStyle(borderDiv).borderColor
    const maxLightnessGain = 0.1
    const minLightnessGain = -0.2
    const numLayers = 2
    const blurList = [5,40]
    const spreadList = [0,5]
    const size = 15

    const c = Color.fromString(borderColor)

    let brightess;

    let boxShadow = ''
    for (let i = 0; i < numLayers; i++) {
        const lightnessGain = minLightnessGain + (maxLightnessGain - minLightnessGain) * (1-i / (numLayers - 1))
        const color = Color.fromHsl(c.h, c.s, c.l + lightnessGain)
        const blur = 2+size * (i / (numLayers - 1))
        boxShadow += `0px 0px ${blurList[i]}px ${spreadList[i]}px ${color.toHex()},`
        if (i == 0) {
            brightess = color
        }
    }
    
    borderDiv.style.boxShadow = boxShadow.slice(0, -1)
    borderDiv.style.borderColor = brightess.toHex()
    textDiv.style.color = brightess.toHex()
}

export function glowText(text: HTMLElement) {
    //get border color
    const borderColor = window.getComputedStyle(text).color.replace('rgb', 'rgba').replace(')', ', 0.4)')
    const textShadow = `0px 0px 2px ${borderColor}`
    text.style.textShadow = textShadow
}