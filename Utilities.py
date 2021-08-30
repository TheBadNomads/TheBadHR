import json


def isNotBot(member):
    return not member.bot

def ConvertJsonToDic(json_string):
    return json.loads(json_string)