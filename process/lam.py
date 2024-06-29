import re

def process_action(content:str):

    if re.search("<Debug Command>", content):
        print("LAM Triggered: <Debug Command>")
        return None

    return None