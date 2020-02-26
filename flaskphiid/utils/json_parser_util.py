import json


def pull_notes_from_amalga_blob(json_blob):
    if "NOTES_TEXT" in json_blob:
        #pull text
        print("foo")
    else:
        raise("No note in this blob")


def xform_dict_to_json(dictionary):
    return json.dumps(dictionary)