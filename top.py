# coding: utf-8

from iss_simple_main import *

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

pd.plotting.register_matplotlib_converters()

import scipy.stats as stats

import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':

    key = 0
    key = 1

    if key == 0:
        now_tqtf = NowTQTF()
        now_tqtf.get_data()

    elif key == 1:
        # https://machinelearningmastery.com/normalize-standardize-time-series-data-python/
        ser = SingleETFReader()
        end_date = datetime.now()

        o1 = "FXRL"
        o2 = "FXTB"

        o1 = "FXRU"
        o2 = "FXRB"

        o1 = "FXUS"
        o2 = "FXCN"

        o1 = "FXRU"
        o2 = "FXRL"
        tickers = [o1, o2]

        ticker_to_data = {}

        # FIXME: scaling?
        # https://stats.stackexchange.com/questions/133155/how-to-use-pearson-correlation-correctly-with-time-series

        for ticker in tickers:
            days = 30 * 3
            data = ser.get_data(ticker, end_date, days=days)

            df = pd.DataFrame(data, columns=ser.get_column_names())

            df['TRADEDATE'] = df['TRADEDATE'].astype('datetime64[ns]')

            df = df[['TRADEDATE', 'CLOSE']]

            df['CLOSE'] -= np.average(df['CLOSE'])
            ticker_to_data[ticker] = df

            # View
            plt.plot(df['TRADEDATE'], df['CLOSE'])
            plt.xticks(rotation='vertical')

        # https://towardsdatascience.com/four-ways-to-quantify-synchrony-between-time-series-data-b99136c4a9c9
        df0 = ticker_to_data[o1]
        df1 = ticker_to_data[o2]

        r, p = stats.pearsonr(df0.dropna()['CLOSE'], df1.dropna()['CLOSE'])
        print("Scipy computed Pearson r: {} and p-value: {}".format(r, p))
        r, p = stats.spearmanr(df0.dropna()['CLOSE'], df1.dropna()['CLOSE'])
        print("Scipy computed Spearmanr r: {} and p-value: {}".format(r, p))

        # print(df0.corr(df1))  # , method='pearson'))

        # plt.plot(df0['CLOSE'], df1['CLOSE'], 'o')

        plt.grid()
        plt.show()
