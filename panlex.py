#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import json
import requests as rq
from ratelimit import *

VERSION = 2

def set_version(version:int):
    version_dict = {1: '', 2: '/v2'}
    global PANLEX_API_URL
    PANLEX_API_URL = "http://api.panlex.org" + version_dict[version]

set_version(VERSION)

if "PANLEX_API" in os.environ:
    PANLEX_API_URL = os.environ["PANLEX_API"]

MAX_ARRAY_SIZE = 10000

# @rate_limited(2)  # 2 calls/sec
def query(ep:str, params:dict):
    """Generic query function.
    ep: an endpoint of the PanLex API (e.g. "/expr")
    params: dict of parameters to pass in the HTTP request."""
    
    if ep.startswith('/'):
        url = PANLEX_API_URL + ep
    else:
        url = ep
    
    r = rq.post(url, data=json.dumps(params))
    if r.status_code != rq.codes.ok:
        if r.status_code == 409:
            raise PanLexError(r.json())
        else:
            r.raise_for_status()
    else:
        return r.json()

def query_all(ep:str, params={}):
    """Generic query function for requests with more than the maximum results
    per API query (2000 at time of writing).
    ep: an endpoint of the PanLex API (e.g. "/langvar")
    params: dict of parameters to pass in the HTTP request."""
    retVal = None
    params = dict.copy(params)  # to avoid overwriting elements of caller's params dict
    if "offset" not in params:
        params["offset"] = 0
    while True:
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
        if "limit" in params:
            params["limit"] -= r["resultNum"]
            if params["limit"] <= 0:
                # limit was hit
                break
    return retVal


def query_iter(ep:str, params={}):
    """Generic query function that creates an iterator for requests with more
    than the maximum results per API query (2000 at time of writing).
    ep: an endpoint of the PanLex API (e.g. "/langvar")
    params: dict of parameters to pass in the HTTP request."""
    params = dict.copy(params)  # to avoid overwriting elements of caller's params dict
    
    if "offset" not in params:
        params["offset"] = 0
    
    while True:
        result = query(ep, params)
        for record in result["result"]:
            yield record
        if result["resultNum"] < result["resultMax"]:
            break

        params["offset"] += result["resultNum"]
        if "limit" in params:
            params["limit"] -= result["resultNum"]
            if params["limit"] <= 0:
                break

def queryAll(ep, params):
    return query_all(ep, params)

def query_norm(ep:str, params):
    """
    Generic query function for normalization queries, able to handle >10,000 element arrays.
    ep: either "/norm/expr/<langvar>" or "/norm/definition/<langvar>"
    params: dict of paramaters to pass in HTTP request, including an array to normalize"""
    retVal = None
    params = dict.copy(params) # to avoid overwriting elements of caller's params dict
    params["cache"] = 0
    temp = dict.copy(params)
    start = 0
    while True:
        end = max(start + MAX_ARRAY_SIZE, len(params["txt"]))
        temp["txt"] = params["txt"][start:end]
        r = query(ep, temp)
        if not retVal:
            retVal = r
        else:
            retVal["norm"].update(r["norm"])
        start += MAX_ARRAY_SIZE
        if start > len(params["txt"]):
            break
    return retVal

def queryNorm(ep, params):
    return query_norm(ep, params)

class PanLexError(Exception):
    def __init__(self, body):
        self.code = body['code']
        self.message = body['message']

def get_translations(expn:str, startLang:str, endLang:str, distance=1, limit=0):
    """Get all translations of expn from startLang into endLang. distance is
    translation distance (1 or 2, default 1). limit is number of translations
    returned (default, no limit).
    Languages are specified as PanLex UID codes (e.g. eng-000 for English.)"""
    params1 = {"uid":startLang,
               "txt":expn}
    r1 = query_all("/expr",params1)
    if not r1["result"]:
        raise PanLexError({"code":0,"message":"{}: not a valid exp in {}".format(expn, startLang)})
    exid = r1["result"][0]["id"]
    params2 = {"trans_expr":exid,
               "uid":endLang,
               "include":"trans_quality", # include the field trq, "translation quality"
               "trans_distance":distance,
               "sort":"trans_quality desc"}
    if limit:
        params2["limit"] = limit
    r2 = query_all("/expr",params2)
    
    return r2["result"]
