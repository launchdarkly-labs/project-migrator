import requests
import json
import time

class RestAdapter:
    url = ""
    url_int = ""
    api_token = ""

    def __init__(self, hostname, version, api_token):
        self.url = f"https://{hostname}/api/{version}"
        self.url_int = f"https://{hostname}/internal"
        self.api_token = api_token
        self.headers = {
            "Authorization": f"{self.api_token}",
            "Content-Type": "application/json"
        }
    
    def get(self, path, params=None, json=None, beta=False, internal=False):
        return self.request("GET", path, params=params, json=json, beta=beta, internal=internal)

    def post(self, path, params=None, json=None, beta=False, internal=False):
        return self.request("POST", path, params=params, json=json, beta=beta, internal=internal)

    def put(self, path, params=None, json=None, beta=False, internal=False):
        return self.request("PUT", path, params=params, json=json, beta=beta, internal=internal)

    def delete(self, path, params=None, json=None, beta=False, internal=False):
        return self.request("DELETE", path, params=params, json=json, beta=beta, internal=internal)

    def patch(self, path, params=None, json=None, beta=False, internal=False):
        return self.request("PATCH", path, params=params, json=json, beta=beta, internal=internal)

    def request(self, http_method, path, params=None, json=None, beta=False, internal=False):
        new_path = path
        if not new_path.startswith("/"):
            new_path = "/" + new_path

        url = f"{self.url}{new_path}"
        if internal:
            url = f"{self.url_int}{new_path}"
        temp_headers = self.headers.copy()
        if beta:
            temp_headers["LD-API-Version"] = "beta"
                
        retry = 0
        while retry < 5:
            try:
                response = requests.request(
                    method=http_method,
                    url=url,
                    headers=temp_headers,
                    params=params,
                    json=json if json else None
                )
                break
            except requests.exceptions.RequestException as e:
                print("!!! Request failed. Retrying...")
                time.sleep(3)
            retry += 1

        #########################
        # Rate limiting Logic
        #########################

        if "X-Ratelimit-Route-Remaining" in response.headers:
            call_limit = 5
            delay = 5
            tries = 5
            limit_remaining = response.headers["X-Ratelimit-Route-Remaining"]

            if int(limit_remaining) <= call_limit:
                resetTime = int(response.headers["X-Ratelimit-Reset"])
                currentMilliTime = round(time.time() * 1000)
                if resetTime - currentMilliTime > 0:
                    delay = round((resetTime - currentMilliTime) // 1000)
                else:
                    delay = 0

                if delay < 1:
                    delay = 0.5

                tries -= 1
                print(
                    " --- Rate limit reached. Waiting for "
                    + str(delay)
                    + " seconds. Remaining tries: "
                    + str(tries)
                )
                time.sleep(delay)
                if tries == 0:
                    return "Rate limit exceeded. Please try again later."
            else:
                tries = 5

        return response
