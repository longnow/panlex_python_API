# example uses of the PanLex Python API
from panlex import *

def translate(expn, startLang, endLang):
    """Get the best-quality translation of expn, an expression in startLang, into endLang.
    Languages are specified as PanLex UID codes (e.g. eng-000 for English.)"""
    params1 = {"uid":startLang,
               "tt":expn,
               "indent":True}
    r1 = query("/ex",params1)
    exid = extractResult(r1,"ex")
    params2 = {"trex":exid,
               "uid":endLang,
               "indent":True,
               "include":"trq", # include the field trq, "translation quality",
               "sort":"trq desc", # sort by descending trq,
               "limit":1} # get only one result (which will be the one with the highest score)}
    r2 = query("/ex",params2)
    return extractResult(r2,"tt")
