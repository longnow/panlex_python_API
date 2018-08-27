# example uses of the PanLex Python API
from panlex import query


def translate(expn, startLang, endLang):
    """Get the best-quality translation of expn, an expression in startLang, into endLang.
    Languages are specified as PanLex UID codes (e.g. eng-000 for English.)"""
    params1 = {"uid": startLang,
               "txt": expn,
               "indent": True}

    expression_result = query("/expr", params1)

    exid = expression_result["result"][0]["id"]

    params2 = {"trans_expr": exid,
               "uid": endLang,
               "indent": True,
               "include": "trans_quality",  # include the field trans_quality, "translation quality"
               "sort": "trans_quality desc",  # sort by descending trans_quality
               "limit": 1  # get only one result (which will be the one with the highest score)}
               }
    translation_result = query("/expr", params2)

    return translation_result["result"][0]["txt"]
