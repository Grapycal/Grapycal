import { Componentable } from "../component/componentable"
import { Workspace } from "../sobjects/workspace"

export class Header extends Componentable{
    protected get template(): string{
        return `
            <div class="header">
                <img src="icon.png" alt="icon" width="27" height="27"></img>
                <div class="spacer"></div>
                <div class="options">
                    <div class="option" id="file">File</div>
                    <div class="option" id="edit">Edit</div>
                    <div class="option" id="view">View</div>
                    <div class="option" id="about">About</div>
                </div>
            </div>
            `;
        }

    protected get style(): string{
        return `
            .header{
                font-size: 16px;
                padding: 0px 0px 0px 15px;
                display: flex;
                align-items: center;
                height: 100%;
            }
            .float-left{
                margin-left: auto;
            }
            .spacer{
                width:20px;
            }
            .options{
                display: flex;
                gap: 0px;
                align-items: center;
                height: 100%;
            }
            .option{
                cursor: pointer;
                height: 100%;
                display: flex;
                align-items: center;
                padding: 0px 7px;
                user-select: none;
                webkit-user-select: none;
            }
            `;
        }
    
    file: HTMLDivElement
    edit: HTMLDivElement
    view: HTMLDivElement
    about: HTMLDivElement
    constructor(){
        super();
        this.htmlItem.setParentElement(document.body.getElementsByTagName('header')[0]);
        this.file = this.htmlItem.getEl('file', HTMLDivElement);
        this.edit = this.htmlItem.getEl('edit', HTMLDivElement);
        this.view = this.htmlItem.getEl('view', HTMLDivElement);
        this.about = this.htmlItem.getEl('about', HTMLDivElement);
        this.file.addEventListener('click', () => {
            document.getElementById('settings-page').classList.toggle('open')
            Workspace.instance.objectsync.emit('refresh_extensions')
        })

    }
}