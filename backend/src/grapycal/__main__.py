# python -m grapycal

from grapycal import GrapycalApp
import usersettings

def main():
    """
    Entry function of backend server
    """
    s = usersettings.Settings("Grapycal")
    s.add_setting("port", int, default=8765) #type: ignore
    s.add_setting("host", str, default="localhost") #type: ignore
    s.load_settings()
    #TODO: enable override from command line
    s.save_settings()
    app = GrapycalApp(s)
    app.run()

if __name__ == '__main__':
    main()
