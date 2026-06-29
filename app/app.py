from flask import Flask
from .database import init_db

# Create Flask application
app = Flask(
    __name__,
    static_folder="../static"
)

# Secret key for session management
app.secret_key = "super_secret_key"

# Initialize database
init_db()

@app.route("/")
def home():
    return app.send_static_file("login.html")

# Import routes after app creation
from .routes.admin_routes import *
from .routes.issuer_routes import *
from .routes.verifier_routes import *

if __name__ == "__main__":
    app.run(debug=True)