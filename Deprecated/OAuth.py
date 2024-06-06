from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse

#create a small local server to handle callbacks for OAuth flow
class OAuthCallback(BaseHTTPRequestHandler):
    code = None   #store returned authorization code
    
    def execute_GET_request(self):
        #pasrse query params from request URL to retrieve OAuth code
        query = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        callback_Code= query['code'][0] if 'code' in query else None  

        self.send_response(200) #sends OK response to client
        self.send_header('Content-type', 'text/html') #set context type of response
        self.end_headers()
        self.wfile.write(b"Authentication Complete! You may close this window.") #success message
        
        self.server.shutdown() #close server after request handling.