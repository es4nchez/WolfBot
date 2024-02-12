
from api.intra import IntraAPIClient

payload = {
        "filter[future]": "true",
}


def get_evals():
        ic = IntraAPIClient(progress_bar=False)
        results = ic.pages_threaded("campus/47/exams", params=payload)
        print(results)


get_evals()