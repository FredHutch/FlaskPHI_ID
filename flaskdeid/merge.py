from collections import defaultdict

MEDLP_KEY = defaultdict('UNKNOWN',
                        {'ANATOMY':'PHYSIOLOGY',
                        'MEDICAL_CONDITION':'PTT',
                        'MEDICATION':'PTT',
                        'PROTECTED_HEALTH_INFORMATION':'PHI',
                        'TEST_TREATMENT_PROCEDURE': 'PTT'
                        })

HUTCHNER_KEY = defaultdict('UNKNOWN',
                           {})

def _match_types(json_blob, type):
    if type is "medlp":
        return _match(json_blob, MEDLP_KEY)
    if type is "hutchner":
        return _match(json_blob, HUTCHNER_KEY)
    raise Exception("Unexpected json type encountered: {}".format(type))

def _match(blob, type_key):
    type_resolved_blob = []
    for b in blob:
        type_resolved_blob.append(_type_resolve(b, type_key))
    return type_resolved_blob

def _type_resolve(chunk, type_key):
    chunk['Category'] = type_key[chunk['Category']]

    return chunk
