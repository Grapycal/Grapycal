# grapycal

import os
from grapycal import GrapycalApp
from .utils import usersettings
import argparse


def main():
    """
    Entry function of backend server
    """
    #parse arguments
    parser = argparse.ArgumentParser(description='Grapycal backend server')
    parser.add_argument('path', type=str, help='path to workspace file', nargs='?', default=None)
    parser.add_argument('--port', type=int, help='port to listen on')
    parser.add_argument('--http-port', type=int, help='http port to listen on (to serve webpage)')
    parser.add_argument('--host', type=str, help='host to listen on')
    parser.add_argument('--no-http', action='store_true', help='if set, the server does not serve the webpage')
    parser.add_argument('--restart', action='store_true', help='if set, the workspace restarts when it exits. Convenient for development')
    args = parser.parse_args()
    s = usersettings.Settings("Grapycal")
    s.add_setting("port", int, default=8765) #type: ignore
    s.add_setting("http_port", int, default=9001) #type: ignore
    s.add_setting("host", str, default="localhost") #type: ignore
    s.add_setting("path", str, default='workspace.grapycal') #type: ignore
    s.load_settings()
    if args.port:
        s['port'] = args.port
    if args.host:
        s['host'] = args.host
    if args.path:
        s['path'] = args.path
    if args.http_port:
        s['http_port'] = args.http_port
    s.save_settings()
    s['no_http'] = args.no_http
    s['restart'] = args.restart

    app = GrapycalApp(s)
    app.run()

if __name__ == '__main__':
    main()
