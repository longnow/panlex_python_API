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
    r = rq.post(url, data=json.dumps(params))
    if r.status_code != rq.codes.ok:
        r.raise_for_status()
    else:
        return r

def extractResult(json, field):
    """Get the results of a JSON response from the PanLex API.
    Most but not all responses use this format, so it's not quite foolproof.
    In particular, responses to hitting the /count endpoints don't have a 'result' field."""
    return json["result"][0][field]

def flatten(queries):
    # give it the same fields as any element in queries...
    retVal = queries[0].json()
    # ... but zero out the resultNum and result fields
    retVal["resultNum"] = 0
    retVal["result"] = []
    for q in queries:
        qdata = q.json()
        retVal["resultNum"] += qdata["resultNum"]
        # get each thing out of the dict in q's result field,
        # and copy it into retVal's result field
        for x in qdata["result"]:
            retVal["result"].append(x)
    return retVal

@rate_limited(2)
def queryAllHelper(ep, params, offset=0):
    """Get all results of a query, and not just the maximum amount of results per query."""
    retVal = []
    params["offset"] = offset
    r = query(ep, params)
    jsonVersion = r.json()
    resultNum = jsonVersion["resultNum"]
    retVal.append(r)
    if resultNum < jsonVersion["resultMax"]:
        # there won't be any more results
        pass
    else:
        # there may be more results
        offset = offset + resultNum
        retVal.extend(queryAllHelper(ep, params, offset))
    return retVal

def queryAll(ep, params):
    return flatten(queryAllHelper(ep, params))
    
@rate_limited(2) #2 calls/sec
def translate(expn, startLang, endLang):
    """Get the best-quality translation of expn, an expression in startLang, into endLang.
    Languages are specified as PanLex UID codes (e.g. eng-000 for English.)"""
    params1 = {"uid":startLang,
               "tt":expn,
               "indent":True}
    r1 = query("ex",params1)
    exid = extractResult(r1.json(),"ex")
    params2 = {"trex":exid,
               "uid":endLang,
               "indent":True,
               "include":"trq",
               "sort":"trq desc",
               "limit":1}
    r2 = query("ex",params2)
    return extractResult(r2.json(),"tt")

def main():
    print(translate("tree","eng-000","cmn-000"))

if __name__ == "__main__":
    main()

