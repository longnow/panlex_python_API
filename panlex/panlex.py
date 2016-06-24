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
    """Get into the results of a JSON response from the PanLex API."""
    return json["result"][0][field]

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

@rate_limited(2) #2 calls/sec
def exCount(entry):
    """Count numbers of expressions.
    entry: the expression string you want to count"""
    params = {"tt":entry}
    r = query("ex/count", params)
    return r.json()['count']

"""TODO: 
   more functions for different kinds of counting
   generic count() function
   function for displaying "Which languages have the word x?"
   function "How do you say x in different languages?"
"""

def main():
    print(translate("tree","eng-000","cmn-000"))

if __name__ == "__main__":
    main()

