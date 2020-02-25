# coding: utf-8
from __future__ import print_function

import sys
import os

from iss_simple_main import *

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

pd.plotting.register_matplotlib_converters()

import scipy.stats as stats

import matplotlib.pyplot as plt
import numpy as np


class Indexer(object):
    def __init__(self, n, horizon):
        self.n = n
        self.horizon = horizon
        self.start = 0
        self.end = min(self.n, self.start + horizon)

    def move(self):
        self.start += 1
        self.end += 1
        if self.end >= self.n:
            return False
        return True

    def range(self):
        return self.start, self.end


def main():
    key = 0
    # key = 1  # corr
    # key = 1001
    # key = 2
    # key = 2

    if key == 0:
        now_tqtf = NowTQTF()
        now_tqtf.get_data(forced_date=None)#forced_date='2020-02-12')

    elif key == 1:
        now_tqtf = AllETFs()
        ticker_to_board = now_tqtf.get_names()
        print(ticker_to_board)

    elif key == 1001:
        now_tqtf = AllETFs()
        ticker_to_board = now_tqtf.get_names(boards_filter=['TQTF'], tickets_filter=['FX'])
        # ticker_to_board = now_tqtf.get_names(boards_filter=['TQTD'])

        ser = SingleETFReader()
        end_date = datetime.now()

        tickers = ticker_to_board.keys()

        ticker_to_data = {}
        for ticker in tickers:
            days = 28 * 12
            boards = ticker_to_board[ticker]
            for board in boards:
                df = ser.get_data(ticker, end_date, board=board, days=days)
                ticker_to_data[ticker] = df['CLOSE'].copy()

                # View
                dff = df['CLOSE']
                dff = (dff - dff.min()) / (dff.max() - dff.min())
                plt.plot(df['TRADEDATE'], dff)
                plt.xticks(rotation='vertical')

        row = 'NAME,'
        for ti in tickers:
            row += ti + ','

        print(row)

        for ti in tickers:
            row = ti + ","
            if ti not in ticker_to_data:
                continue

            for tj in tickers:
                r = -1
                if tj not in ticker_to_data:
                    pass
                else:
                    a, b = ticker_to_data[ti], ticker_to_data[tj]
                    if len(a) != len(b):
                        r = -1  # impossible
                    else:
                        r, p = stats.spearmanr(a, b)

                row += "{0:.2f}".format(r) + ','
                # print("Spearmanr r: {} Ti : {} Tj : {}".format(r, ti, tj))
            print(row)

        # FIXME: print nicely

        plt.grid()
        plt.show()

    elif key == 2:
        # https://machinelearningmastery.com/normalize-standardize-time-series-data-python/
        ser = SingleETFReader()
        end_date = datetime.now()

        now_tqtf = AllETFs()
        ticker_to_board = now_tqtf.get_names(boards_filter=['TQTF'])  # , tickets_filter=['FX'])

        o1 = "VTBB"
        o2 = "FXRU"
        o3 = "FXRB"
        # o3 = "SBGB"
        # o4 = "FXUS"
        tickers = [o1, o2, o3]  # , o4]

        ticker_to_data = {}

        # FIXME: scaling?
        # https://stats.stackexchange.com/questions/133155/how-to-use-pearson-correlation-correctly-with-time-series

        for ticker in tickers:
            days = 28 * 12
            # board = 'TQTD'
            board = 'TQTF'
            df = ser.get_data(ticker, end_date, board=board, days=days)

            # df['CLOSE'] -= np.average(df['CLOSE'])
            ticker_to_data[ticker] = df

            # View
            dff = df['CLOSE']
            dff = (dff - dff.min()) / (dff.max() - dff.min())
            plt.plot(df['TRADEDATE'], dff, label=ticker)
            plt.xticks(rotation='vertical')
            plt.legend()

        # https://towardsdatascience.com/four-ways-to-quantify-synchrony-between-time-series-data-b99136c4a9c9
        df0 = ticker_to_data[o1]
        df1 = ticker_to_data[o2]

        r, p = stats.pearsonr(df0.dropna()['CLOSE'], df1.dropna()['CLOSE'])
        print("Scipy computed Pearson r: {} and p-value: {}".format(r, p))
        r, p = stats.spearmanr(df0.dropna()['CLOSE'], df1.dropna()['CLOSE'])
        print("Scipy computed Spearmanr r: {} and p-value: {}".format(r, p))

        # print(df0.corr(df1))  # , method='pearson'))

        # plt.plot(df0['CLOSE'], df1['CLOSE'], 'o') # BAD VISUZL

        plt.grid()
        plt.show()

    elif key == 3:
        # Definition Historical Volatility (HV)
        # https://www.investopedia.com/terms/h/historicalvolatility.asp
        #   correlation is important to calclate
        # https://www.ally.com/do-it-right/investing/what-is-volatility-and-how-to-calculate-it/
        # https://www.investopedia.com/ask/answers/021015/how-can-you-calculate-volatility-excel.asp

        # CV https://www.investopedia.com/terms/c/coefficientofvariation.asp
        # COV - https://www.investopedia.com/terms/c/covariance.asp

        # LN ?? https://finopedia.ru/kak-rasscitat-istoriceskuu-volatilnost

        # Q: как посчитать риск портфеля

        # https://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe/48539196

        ser = SingleETFReader()
        end_date = datetime.now()

        o1 = "FXRU"  # Волатильность в годовом измерении* 20.24%

        #  trading days per year,
        days = 252
        data = ser.get_data(o1, end_date, days=days)

        df = pd.DataFrame(data, columns=ser.get_column_names())

        df['TRADEDATE'] = df['TRADEDATE'].astype('datetime64[ns]')

        df = df[['TRADEDATE', 'CLOSE']]
        df = df['CLOSE']
        df = df.div(df.shift(1)).dropna(how='all')
        # np.log(df.price) - np.log(df.price.shift(1))

        df = np.log(df)
        df -= 1
        n = len(df)

        horizon = days

        indexer = Indexer(n, horizon)

        while True:
            r = indexer.range()
            df_sel = df[r[0]:r[1]]
            std = df_sel.std()
            v = np.sqrt(days) * std
            print(v * 100, "%")

            if not indexer.move():
                break

    elif key == 4:
        # https://financetrainingcourse.com/education/2011/04/market-risk-metrics-portfolio-volatility/
        # https://www.investopedia.com/terms/p/portfolio-variance.asp
        #
        # https://bcs-express.ru/novosti-i-analitika/sostavlenie-investitsionnogo-portfelia-po-markovitsu-dlia-chainikov
        pass
    elif key == 5:
        # Multiplicators
        # https://bcs-express.ru/novosti-i-analitika/gid-po-rynochnym-mul-tiplikatoram-kak-otsenit-kompanii-po-analogii
        pass


if __name__ == '__main__':
    main()
