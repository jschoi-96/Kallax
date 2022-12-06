from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc6749 import OAuth2Token
from dotenv import load_dotenv

import os


"""
These are defined here to avoid circular imports that would happen if they were defined in app.py
See https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/#factories-extensions for details
"""

load_dotenv()

# Create database instance
db = SQLAlchemy()
# Create Alembic instance
migrate = Migrate()

# Create OAuth instance
def fetch_token(name, request):
    token = OAuth2Token.find(
        name=name,
        user=request.user
)
    return token.to_token()

oauth = OAuth()
auth0 = oauth.register('auth0',
                    client_id=os.environ['AUTH0_CLIENTID'],
                    client_secret=os.environ['AUTH0_CLIENT_SECRET'],
                    api_base_url=f"https://{os.environ['AUTH0_DOMAIN']}",
                    access_token_url=f"https://{os.environ['AUTH0_DOMAIN']}/oauth/token",
                    authorize_url=f"https://{os.environ['AUTH0_DOMAIN']}/authorize",
                    client_kwargs={'scope': 'openid profile email'},
                    server_metadata_url=f"https://{os.environ['AUTH0_DOMAIN']}/.well-known"f"/openid-configuration",
                    fetch_token=fetch_token,)


                                       
