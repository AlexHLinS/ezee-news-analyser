import pandas as pd
import aux_tools as auts
from typing import Dict, List

def get_uid_list(urls)->Dict[str:List[str]]:
    urls = ds['url'].tolist()
    result = dict()
    for url in urls:
        text = auts.get_text_from_url(url)
        result[url] = auts.get_antiplag_uid(text)
    return result

def main():
    ds = pd.read_excel('./hypotheses/test_sets/test_dataset_1.xlsx')
    urls = ds['url'].tolist()
    urls_and_uids = get_uid_list(urls)


if __name__ == "__main__":
    main()
