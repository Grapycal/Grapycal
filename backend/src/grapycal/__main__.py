from grapycal import GrapycalApp, load_config
import sys

def main():
    if len(sys.argv)<2:
        config_path = 'config/default.yaml'
    else:
        config_path = sys.argv[1]
    config = load_config(config_path
    )
    app = GrapycalApp(config)
    app.run()

if __name__ == '__main__':
    main()

# poetry run python -m grapycal