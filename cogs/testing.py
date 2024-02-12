import json
from datetime import datetime
from api.intra import IntraAPIClient
from rich import print
from rich.json import JSON
from pprint import pprint

payload = {
        "filter[future]": "true",
}


def get_evals():
        ic = IntraAPIClient(progress_bar=False)
        results = ic.pages_threaded("campus/47/exams", params=payload)
        print(results)


get_evals()