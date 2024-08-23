from io import BytesIO
from pathlib import Path
from urllib.request import url2pathname

import requests
import requests.adapters


class FileResponse(BytesIO):
    """
    A dummy response for reading a file.

    Status is always 200 - if file cannot be read, we don't get to the point
    of creating the `FileResponse`.

    Original idea from:
    https://github.com/ambv/requests-testadapter/blob/master/src/requests_testadapter.py
    """

    def __init__(self, stream):
        super().__init__(stream)
        self.headers = None
        self.reason = "ok"
        self.status = 200


class LocalFileAdapter(requests.adapters.HTTPAdapter):

    """
    A `requests` transport adapter to read local files.

    Based on SO answer: https://stackoverflow.com/a/22989322
    An alternative would be: https://pypi.org/project/requests-file/

    Note: need to mount this adapter in the session:
    ```
        with requests.Session() as session:
            session.mount("file://", LocalFileAdapter())
            html = session.get(url)
    ```
    See comment in `requests.api.request()` for reasoning behind
    with-statement.
    """

    def build_response_from_file(self, req: requests.Request):
        url: str = req.url
        pth = Path(url2pathname(url.removeprefix("file:")))
        with pth.open("rb") as file:
            buff = bytearray(pth.stat().st_size)
            file.readinto(buff)
            resp = FileResponse(buff)
            r = self.build_response(req, resp)

            return r

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):

        requests.session

        return self.build_response_from_file(request)
