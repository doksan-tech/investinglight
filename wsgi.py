"""Application entry point."""
from web import create_app
import os
print(os.path.abspath(os.path.dirname(__file__)))
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
