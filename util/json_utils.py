import json


def pretty_print(json_string):
    tree = json.loads(json_string)
    print(json.dumps(tree, sort_keys=True, indent=4, separators=(',', ': ')))
