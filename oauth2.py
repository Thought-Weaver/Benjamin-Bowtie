from http.server import HTTPServer, BaseHTTPRequestHandler

import binascii
import os
import requests
import time
import urllib
import webbrowser

# Adapted from: https://pyquestions.com/oauth-and-redirect-uri-in-offline-python-script
class OAuth2:
    def __init__(self, auth_url, token_url, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret
        self._server, self._port = "localhost", 8080
        self._redirect_uri = f"http://{self._server}:{self._port}"
        self._last_request_time = 0
        self._auth_url = auth_url
        self._token_url = token_url

        self.token = None
        self.refresh_token = None
        self.code = ""
        self.state = binascii.hexlify(os.urandom(20)).decode("utf-8")

    class RequestHandler(BaseHTTPRequestHandler):
        def set_outer_class(self, outer_class_instance):
            self._outer_class_instance = outer_class_instance

        def do_GET(self):
            self.close_connection = True
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if not query["state"] or query["state"][0] != self._outer_class_instance.state:
                raise RuntimeError("State argument missing or invalid")
            self._outer_class_instance.code = query["code"]

    def auth(self, *args):
        scope = " ".join(args)
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "scope": scope,
            "state": self.state
        }
        request = requests.Request("GET", self._auth_url, params).prepare()
        request.prepare_url(self._auth_url, params)
        webbrowser.open(request.url)
        request_handler = OAuth2.RequestHandler
        request_handler.set_outer_class(request_handler, self)
        server = HTTPServer((self._server, self._port), request_handler)
        server.handle_request()
        params = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "authorization_code",
            "code": self.code,
            "redirect_uri": self._redirect_uri
        }
        self._get_token(params)
    
    def _get_token(self, params):
        data = requests.get(self._token_url, params).json()
        self.token = data["access_token"]
        self.refresh_token = data["refresh_token"]

    def _refresh_token(self):
        params = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        self._get_token(params)
    
    def _request(self, func, url, params, sleep=5, cooldown=600):
        t = time.time()
        if t - self._last_request_time < sleep:
            time.sleep(sleep - t + self._last_request_time)
        self._last_request_time = t
        max_sleep = 16 * sleep
        params["access_token"] = self.token
        while True:
            try:
                response = func(url, params)
                data = response.json()
                if data.get("error_code") == 429:
                    sleep *= 2
                    time.sleep(sleep)
                    if sleep > max_sleep:
                        raise ConnectionError("Request timed out - server is busy.")
                elif data.get("error") == "user_api_threshold":
                    raise ConnectionError("Too many requests")
                elif data.get("error") == 'invalid_token':
                    self._refresh_token()
                    params["access_token"] = self.token
                else:
                    return response
            except ConnectionError:
                time.sleep(cooldown)

    def get(self, url, params):
        return self._request(requests.get, url, params)

    def post(self, url, params):
        return self._request(requests.post, url, params)
