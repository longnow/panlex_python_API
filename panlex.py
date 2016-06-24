import json
import requests as rq
from ratelimit import *

url = "http://api.panlex.org/ex"
extras = {"uid":"eng-000",
          "tt":"tree",
          "indent":True}

def extractResult(json, field):
    """Get into the results of a JSON response from the PanLex API."""
    return json["result"][0][field]

# limited to 2 calls/second
@rate_limited(2)
def translateFromEnglishToMandarin(targetWord):
    url = "http://api.panlex.org/ex"
    ps = {"uid":"eng-000",
          "tt":targetWord,
          "indent":True}
    r1 = rq.post(url, data=json.dumps(extras))
    if r1.status_code != rq.codes.ok:
        r1.raise_for_status()
    else:
        exid = extractResult(r1.json(),"ex")
        r2 = rq.post(url, json.dumps({"trex":exid,
                                      "uid":"cmn-000",
                                      "indent":True,
                                      "include":"trq",
                                      "sort":"trq desc",
                                      "limit":1}))
        if r2.status_code != rq.codes.ok:
            r2.raise_for_status()
        else:
            return extractResult(r2.json(),"tt")

def main():
    print(translateFromEnglishToMandarin("tree"))

if __name__ == "__main__":
    main()
