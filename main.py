# coding: utf-8
import requests
import os
from urllib.parse import quote
from collections import deque
from shutil import make_archive, copy, rmtree


class YaDiskException(Exception):
    code = None

    def __init__(self, code, text):
        super(YaDiskException, self).__init__(text)
        self.code = code

    def __str__(self):
        return f"{self.code}. {super(YaDiskException, self).__str__()}"


class YaDisk:
    client_id = '16d12faa3bde4e31830bf05fecc00e7a'
    client_secret = 'b7a8d9b4a22648c682c0e60e2289355d'
    token = None
    url = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token):
        self.token = token
        resp = self._sendRequest("GET")
        if resp.status_code == 401:
            raise YaDiskException(401, "Wrong token")
        elif resp.status_code != 200:
            raise YaDiskException(resp.status_code, resp.json)

    def _sendRequest(self, type_request, add_url="/"):
        headers = {
            "Accept": "application/json",
            "Authorization": f"OAuth {self.token}"
        }
        url = self.url + add_url
        return requests.request(type_request, url, headers=headers)

    def download(self, path, file):
        url = f"/resources/download?path={quote(path)}"
        resp = self._sendRequest("GET", url)
        if resp.status_code == 200:
            r = requests.get(resp.json()["href"])
            with open(file, 'wb') as code:
                code.write(r.content)
        else:
            raise YaDiskException(resp.status_code, resp.json())

    def ls(self, path='/'):
        url = f"/resources?path={quote(path)}"
        resp = self._sendRequest("GET", url)
        if resp.status_code == 200:
            return [elem['path'] for elem in resp.json()['_embedded']['items']]
        else:
            raise YaDiskException(resp.status_code, resp.json())

    def upload(self, file, path):
        if os.path.isdir(file):
            self.upload_dir(file)
            return
        url = f"/resources/upload?path={quote(path)}"
        resp = self._sendRequest("GET", url)
        if resp.status_code == 200:
            with open(file, "rb") as f:
                respons = requests.put(resp.json()["href"], data=f)
                if respons.status_code != 201:
                    raise YaDiskException(respons.status_code, respons.json())
        else:
            raise YaDiskException(resp.status_code, resp.json())

    def upload_dir(self, direction):
        queue = deque()
        queue.append(os.path.basename(direction))
        basement_direction = os.path.dirname(direction)
        self.make_direction('/' + os.path.basename(direction))
        while len(queue) > 0:
            local = queue.popleft()
            direction = os.path.join(basement_direction, local)
            for file in os.listdir(direction):
                new_path = os.path.join(direction, file)
                if os.path.isfile(new_path):
                    self.upload(new_path,
                                '/' + os.path.join(local, file).replace('\\', '/'))
                if os.path.isdir(new_path):
                    self.make_direction('/' + os.path.join(local, file).replace('\\', '/'))
                    queue.append(os.path.join(local, file))

    def make_direction(self, path):
        url = f"/resources?path={quote(path)}"
        resp = self._sendRequest("PUT", url)
        if resp.status_code != 201:
            if resp.status_code == 409:
                raise YaDiskException(409, f"Path {path} already exists")
            else:
                raise YaDiskException(resp.status_code, resp.content)

    def upload_zip(self, path, root_dir):
        if os.path.isfile(root_dir):
            os.mkdir('copy')
            copy(root_dir, 'copy')
            make_archive('copy', 'zip', 'copy')
            self.upload('copy.zip', path)
            os.remove('copy.zip')
            rmtree('copy')
        else:
            make_archive('copy', 'zip', root_dir)
            self.upload('copy.zip', path)
            os.remove('copy.zip')

    def remove(self, path):
        url = f"/resources?path={quote(path)}"
        resp = self._sendRequest("DELETE", url)
        if not (resp.status_code == 204 or resp.status_code == 202):
            raise YaDiskException(resp.status_code, resp.json())
