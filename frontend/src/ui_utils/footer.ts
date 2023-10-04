import { Componentable } from "../component/componentable"

export class Footer extends Componentable{
    static ins: Footer
    static setStatus(status: string){
        Footer.ins.setStatus(status);
    }
    protected get template(): string{
        return `
            <div class="footer">
                <p id="workspace-name"></p>
                <p id="status"></p>
                <p class="float-left">Grapycal v0.4.0</p>
            </div>
            `;
        }

    protected get style(): string{
        return `
            .footer{
                padding: 0 15px;
                display: flex;
                align-items: center;
                height: 100%;
                gap: 20px;
            }
            .float-left{
                margin-left: auto;
            }
            `;
        }

    workspaceName: HTMLParagraphElement
    status: HTMLParagraphElement
    constructor(){
        super();
        Footer.ins = this;
        this.htmlItem.setParentElement(document.body.getElementsByTagName('footer')[0]);
        this.workspaceName = this.htmlItem.getEl('workspace-name', HTMLParagraphElement);
        this.status = this.htmlItem.getEl('status', HTMLParagraphElement);

        this.status.innerHTML = 'Loading workspace...';

        this.workspaceName.innerHTML = 'workspace.grapycal';
    }

    setStatus(status: string){
        this.status.innerHTML = status;
    }
}