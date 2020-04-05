
# Code to load raw data from Quandl/SF1
# https://www.quandl.com/data/SF1-Core-US-Fundamentals-Data/
# requires the python Quandl package, and the 
# Quandl API key to be set as an ENV variable QUANDL_API_KEY.

import quandl

from alphacompiler.util.zipline_data_tools import get_ticker_sid_dict_from_bundle
from alphacompiler.util.sparse_data import pack_sparse_data
from alphacompiler.util import quandl_tools
from logbook import Logger
import datetime
from os import listdir


DS_NAME = 'SHARADAR/SF0'   # quandl DataSet code
RAW_FLDR = "raw/"  # folder to store the raw text file
VAL_COL_NAME = "Value"
START_DATE = '2010-01-01'
END_DATE = datetime.datetime.today().strftime('%Y-%m-%d')

BASE = "/Users/jordanvalansi/projects/alpha-compiler/alphacompiler/data/"
FN = "SF0.npy"

log = Logger('load_quandl_sf0.py')


def populate_raw_data(tickers, fields, raw_path):
    """tickers is a dict with the ticker string as the key and the SID
    as the value.  """
    quandl_tools.set_api_key()

    # existing = listdir(RAW_FLDR)

    for ticker, sid in tickers.items():
        # if "%d.csv" % sid in existing:
        #     continue
        try:
            query_str = "%s %s" % (DS_NAME, ticker)
            print("fetching data for: {}".format(query_str))

            # df = quandl.get_table(query_str, start_date=START_DATE, end_date=END_DATE)
            df = quandl.get_table(DS_NAME,
                                  calendardate={'gte': START_DATE, 'lte': END_DATE},
                                  ticker=ticker,
                                  qopts={'columns': ['dimension', 'datekey'] + fields})

            df = df[df.dimension == "ARQ"]  # only use As-Reported numbers

            #  Change column name to field
            df = df.rename(columns={"datekey": "Date"})
            df = df.drop(["dimension"], axis=1)

            # write raw file: raw/
            df.to_csv("{}/{}.csv".format(raw_path, sid))
        except quandl.errors.quandl_error.NotFoundError:
            print("error with ticker: {}".format(ticker))

def demo():
    # demo works on free data

    tickers = {"WMT":3173, "HD":2912, "DOGGY":69, "CSCO":2809}
    fields = ["GP", "CAPEX", "EBIT", "ASSETS"]
    populate_raw_data(tickers, fields)


def all_tickers_for_bundle(fields, bundle_name, raw_path=RAW_FLDR):
    tickers = get_ticker_sid_dict_from_bundle(bundle_name)
    populate_raw_data(tickers, fields, raw_path)


if __name__ == '__main__':

    #demo()
    #fields = ["ROE_ART", "BVPS_ARQ", "SPS_ART", "FCFPS_ARQ", "PRICE"]
    fields = ["marketcap", "pb"]
    all_tickers_for_bundle(fields, 'quantopian-quandl')
    pack_sparse_data(3196,  # number of tickers in buldle + 1
                    BASE + RAW_FLDR,
                    fields,
                    BASE + FN)

    print("this worked boss")
