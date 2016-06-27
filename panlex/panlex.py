import json
import requests as rq
from ratelimit import *

PANLEX_API_URL = "http://api.panlex.org"

@rate_limited(2) #2 calls/sec
def query(ep, params):
    """Generic query function.
    ep: an endpoint of the PanLex API (e.g. "/ex")
    params: dict of parameters to pass in the HTTP request."""
    url = PANLEX_API_URL + ep
    r = rq.post(url, data=json.dumps(params))
    if r.status_code != rq.codes.ok:
        r.raise_for_status()
    else:
        return r.json()

def extractResult(json, field):
    """Get the results of a JSON response from the PanLex API.
    Most but not all responses use this format, so it's not quite foolproof.
    In particular, responses to hitting the /count endpoints don't have a 'result' field."""
    return json["result"][0][field]

def queryAll(ep, params):
    params = dict.copy(params) # to avoid overwriting elements of caller's params dictionary
    """Generic query function for requests with more than 2000 reults
    ep: an endpoint of the PanLex API (e.g. "/lv")
    params: dict of parameters to pass in the HTTP request."""
    retVal = None
    if "offset" not in params:
        params["offset"] = 0
    while 1:
        r = query(ep, params)
        if not retVal:
            retVal = r
        else:
            retVal["result"].extend(r["result"]) 
            retVal["resultNum"] += r["resultNum"]
            if r["resultNum"] < r["resultMax"]:
                # there won't be any more results
                break
        params["offset"] += r["resultNum"]
    return retVal
    
def translate(expn, startLang, endLang):
    """Get the best-quality translation of expn, an expression in startLang, into endLang.
    Languages are specified as PanLex UID codes (e.g. eng-000 for English.)"""
    params1 = {"uid":startLang,
               "tt":expn,
               "indent":True}
    r1 = query("ex",params1)
    exid = extractResult(r1,"ex")
    params2 = {"trex":exid,
               "uid":endLang,
               "indent":True,
               "include":"trq",
               "sort":"trq desc",
               "limit":1}
    r2 = query("ex",params2)
    return extractResult(r2,"tt")
