import { print } from "../devUtils"

export function glowDiv(div: HTMLElement) {
    //get border color
    const borderColor = window.getComputedStyle(div).borderColor
    const boxShadow = `0 0 6px 0px ${borderColor}`
    div.style.boxShadow = boxShadow
}

export function glowText(text: HTMLElement) {
    //get border color
    const borderColor = window.getComputedStyle(text).color.replace('rgb', 'rgba').replace(')', ', 0.4)')
    const textShadow = `0px 0px 2px ${borderColor}`
    text.style.textShadow = textShadow
}