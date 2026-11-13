import http.server
import urllib.parse
import webbrowser
import requests

CLIENT_ID = "CLIENT ID HERE"
CLIENT_SECRET = "CLIENT SECRET HERE"
REDIRECT_URI = "http://localhost:8080"

authorization_code = None

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        if "code" in query_params:
            authorization_code = query_params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.w32.write(b"<h1>Authentication successful! You can close this window.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
        
    def log_message(self, format, *args):
        pass

def main():
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&"
        f"response_type=code&scope=https://www.googleapis.com/auth/youtube&"
        f"access_type=offline&prompt=consent"
    )
    print("Opening browser for Google Authentication...")
    webbrowser.open(auth_url)

    server = http.server.HTTPServer(("localhost", 8080), OAuthHandler)
    while authorization_code is None:
        server.handle_request()

    print("\nAuthorization code received! Exchanging for tokens...")
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(token_url, data=payload)
    tokens = response.json()
    print("\n--- RESPONSE TOKENS ---")
    print(tokens)
    if "refresh_token" in tokens:
        print(f"\nYour new Refresh Token is:\n{tokens['refresh_token']}")
    else:
        print("\nRefresh token not found in response.")

if __name__ == "__main__":
    main()