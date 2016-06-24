import json
import requests as rq
from ratelimit import *

PANLEX_API_URL = "http://api.panlex.org/"

@rate_limited(2) #2 calls/sec
def query(ep, params):
    """Generic query function.
    ep: an endpoint of the PanLex API.
    params: dict of parameters to pass in the HTTP request."""
    url = PANLEX_API_URL + ep
    r = rq.post(url, data=json.dumps(objects))
    if r.status_code != rq.codes.ok:
        r.raise_for_status()
    else:
        return r

def extractResult(json, field):
    """Get into the results of a JSON response from the PanLex API."""
    return json["result"][0][field]

@rate_limited(2) #2 calls/sec
def translate(expn, startLang, endLang):
    """Get the best-quality translation of expn, an expression in startLang, into endLang.
    Languages are specified as PanLex UID codes (e.g. eng-000 for English.)"""
    url = PANLEX_API_URL + "ex"
    ps = {"uid":startLang,
          "tt":expn,
          "indent":True}
    r1 = rq.post(url, data=json.dumps(ps))
    if r1.status_code != rq.codes.ok:
        r1.raise_for_status()
    else:
        exid = extractResult(r1.json(),"ex")
        r2 = rq.post(url, json.dumps({"trex":exid,
                                      "uid":endLang,
                                      "indent":True,
                                      "include":"trq",
                                      "sort":"trq desc",
                                      "limit":1}))
        if r2.status_code != rq.codes.ok:
            r2.raise_for_status()
        else:
            return extractResult(r2.json(),"tt")

def main():
    print(translate("tree","eng-000","cmn-000"))

if __name__ == "__main__":
    main()
