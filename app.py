"""Application entry point."""
from web import create_app
from config import Config

server = create_app(dash_debug=Config.dash_debug, dash_auto_reload=Config.dash_auto_reload)

if __name__ == "__main__":
    server.run(host='0.0.0.0', port=5000, debug=Config.flask_debug, threaded=True)