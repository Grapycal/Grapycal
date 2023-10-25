# python -m grapycal

from grapycal import GrapycalApp
import usersettings
import argparse

def main(s: usersettings.Settings):
    """
    Entry function of backend server
    """
    s.load_settings()
    app = GrapycalApp(s)
    app.run()

if __name__ == '__main__':
    #parse arguments
    parser = argparse.ArgumentParser(description='Grapycal backend server')
    parser.add_argument('--port', type=int, help='port to listen on')
    parser.add_argument('--host', type=str, help='host to listen on')
    parser.add_argument('--path', type=str, help='path to workspace file')
    parser.add_argument('--no-serve-webpage', action='store_true', help='if set, the server does not serve the webpage')
    args = parser.parse_args()
    s = usersettings.Settings("Grapycal")
    s.add_setting("port", int, default=8765) #type: ignore
    s.add_setting("host", str, default="localhost") #type: ignore
    s.add_setting("path", str, default="workspace.grapycal") #type: ignore
    s.load_settings()
    if args.port:
        s['port'] = args.port
    if args.host:
        s['host'] = args.host
    if args.path:
        s['path'] = args.path
    s.save_settings()
    s['no_serve_webpage'] = args.no_serve_webpage
    main(s)
