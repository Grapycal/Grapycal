export class WorkspaceSelector{
    private select: HTMLSelectElement;
    private workspaceList: {id: string, name: string}[] = [];

    constructor(){
        this.select = document.createElement('select');
        // mount select to html
        document.body.appendChild(this.select);
    }

    setWorkspaceList(workspaceList: {id: string, name: string}[]){
        //display workspace list in html 
        this.workspaceList = workspaceList;  
        this.select.innerHTML = '';
        for(const workspace of workspaceList){
            const option = document.createElement('option');
            option.value = workspace.id;
            option.text = workspace.name;
            this.select.appendChild(option);
        }  
    }

    async waitForSelection(): Promise<string>{
        // wait for user to select workspace and return workspace id
        return new Promise((resolve, reject) => {
            this.select.onchange = () => {
                resolve(this.select.value);
            }
        })
    }
}