
from modules.course import *
from modules.api.crypto_compare.download_courses import main_routine_download_course_list_cc

if __name__ == "__main__":
    """ # Explanation
    There are 2 sources where it is defined which symbols are downloaded:
      - from yaml: course selection in a self-defined file - course_selection.yaml
      - from api: a downloaded csv list of all available symbols at Cryptocompare. These can be downloaded via the file cc_api_load_symbols.py
        - Parameters: 
          - amount of symbols to request
          - order (file, newest, oldest)

        # Instructions
    - file cc_symbols_api.csv available (if not, then run the file cc_api_load_symbols.py)
    - set source
    - set order and n, if source = api
    - (if existing symbols should be requested completely new (overwrite) and should not only be updated: set self.allow_update = False)
    """

    source = 'api' # [list, api]

    match source:
        case 'list':                    # self-defined in a list
            symbols = ['BTC', 'ETH', 'ADA', 'LINK']
        case 'api':                     # symbols from crypto compare saved in a csv
            n = 10                      # amount symbols for api calls (None if download all)
            asset_type = 'BLOCKCHAIN'   # asset_type [None - all, 'BLOCKCHAIN', 'TOKEN', 'FIAT', 'INDEX']
            order = 0                   # [0 - default, 1 - newest, 2 - oldest]
            symbols = get_symbols_list_from_api_csv_cc(n, asset_type, order)
        case _:
            raise ValueError(f'Wrong source: {source}')

    main_routine_download_course_list_cc(symbols)







