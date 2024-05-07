from praw.util import token_manager
import json
import os
import datetime

class TokenManager(token_manager.BaseTokenManager):
    def __init__(self, token_file='reddit_Auth_token.json'):
        super().__init__()  #initialization from BaseTokenManager
        self.token_file = token_file

    def post_refresh_callback(self, authorizer):
        #save the refreshed token to a file
        token_data = {
            'access_token': authorizer.access_token,
            'refresh_token': authorizer.refresh_token,
            'scope': authorizer.scope,
            'expires_in': authorizer.expires_at.isoformat()
        }
        with open(self.token_file, 'w') as token_file:
            json.dump(token_data, token_file)

    def pre_refresh_callback(self, authorizer):
        #load the token from a file if it exists and is not expired
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as token_file:
                token_data = json.load(token_file)
                authorizer.access_token = token_data['access_token']
                authorizer.refresh_token = token_data['refresh_token']
                authorizer.scope = token_data['scope']
                authorizer.expires_at = authorizer.expires_at = datetime.fromisoformat(token_data['expires_in'])
