// from 'typescript-cookie' doesn't work. Maybe a bug of the library?
import { getCookie, removeCookie, setCookie } from '../../node_modules/typescript-cookie'
import { WorkspaceSelector } from "./workspaceSelector"

export class LoginApiClient {

    private token: string | null = null;
    private selector: WorkspaceSelector = new WorkspaceSelector();

    get isLoggedIn(): boolean {
        return this.token != null;
    }

    constructor(){
        // check if token is set
        const token = getCookie('token');
        if(token){
            this.token = token;
        }
    }

    async interact(): Promise<string>{
        if(!this.isLoggedIn){
            await this.login();
        }
        await this.getWorkspaceList();
        const workspaceId = await this.selector.waitForSelection();
        const wsUrl = await this.getWsUrl(workspaceId);
        return wsUrl;
    }

    public async login(){
        // login and get ws url and token
        const token = await MockServer.login('username', 'password');
        setCookie('token', token);
    }

    public async logout(){
        // logout and clear token
        await MockServer.logout(this.token!);
        this.token = null;
        setCookie('token', '');
    }

    private async getWorkspaceList(){
        // get list of workspaces and display them
        const workspaceList = await MockServer.getWorkspaceList(this.token!);
        this.selector.setWorkspaceList(workspaceList);
    } 

    private async getWsUrl(workspaceId: string): Promise<string>{
        // get ws url of a workspace
        const result = await MockServer.getWsUrl(this.token!, workspaceId);
        return result;
    }
}

class MockServer{
    static async login(username: string, password: string): Promise<string>{
        return 'token';
    }
    static async logout(token: string): Promise<void>{
        return;
    }

    static async getWorkspaceList(token: string): Promise<any[]>{
        return [
            {id: '1', name: 'workspace 1'},
            {id: '2', name: 'workspace 2'},
            {id: '3', name: 'workspace 3'}
        ];
    }   

    static async getWsUrl(token: string, workspaceId: string): Promise<string>{
        return `ws://${location.hostname}:9001/ws/${workspaceId}`;
    }
}