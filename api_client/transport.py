import time
import traceback

import httpx


class RetryTransport(httpx.HTTPTransport):
    def handle_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:
        retry = 0
        resp = None
        while retry < 5:
            retry += 1
            if retry > 2:
                time.sleep(10)
            try:
                if resp is not None:
                    resp.close()
                resp = super().handle_request(request)
            except Exception as e:
                print("httpx {} exception {} caught - retrying".format(request.url, e))
                continue
            if resp.status_code >= 500 and resp.status_code < 600:
                print("httpx {} 5xx response - retrying".format(request.url))
                continue
            content_type = resp.headers.get("Content-Type")
            if content_type is not None:
                mime_type, _, _ = content_type.partition(";")
                if mime_type == "application/json":
                    try:
                        resp.read()
                        resp.json()
                    except Exception as e:
                        traceback.print_exc()
                        print(
                            "httpx {} response not decodable as json '{}' - retrying".format(
                                request.url, e
                            )
                        )
                        continue
            break
        return resp
