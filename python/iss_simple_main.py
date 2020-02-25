# coding: utf-8
# !/usr/bin/env python
"""
    Small example of interaction with Moscow Exchange ISS server.

    Version: 1.1
    Developed for Python 2.6

    Requires iss_simple_client.py library.
    Note that the valid username and password for the MOEX ISS account
    are required in order to perform the given request for historical data.

    @copyright: 2016 by MOEX
"""

import sys

from os.path import expanduser
from datetime import datetime
from datetime import timedelta

import pandas as pd

from iss_simple_client import Config
from iss_simple_client import MicexAuth
from iss_simple_client import MicexISSClient
from iss_simple_client import MicexISSDataHandler


class Auth(object):
    def __init__(self):
        f = open(expanduser("~") + "/credentials", "r")
        pair = f.read()

        user, password = pair.split(' ')
        user = user.strip()
        password = password.strip()
        self.my_config = Config(user=user, password=password, proxy_url='')
        self.my_auth = MicexAuth(self.my_config)

        class MyDataHandler(MicexISSDataHandler):
            """ This handler will be receiving pieces of data from the ISS client.
            """

            def do(self, market_data):
                """ Just as an example we add all the chunks to one list.
                In real application other options should be considered because some
                server replies may be too big to be kept in memory.
                """
                self.data.history = self.data.history + market_data

        self.MyDataHandler = MyDataHandler


class SingleETFReader(Auth):
    def __init__(self):
        # http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqtf/securities.json?from=2018-08-08&till=2018-08-25&interval=24&start=0
        # http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqtf/securities/FXRU/candles.json?from=2018-08-08&till=2018-08-25&interval=24&start=0
        Auth.__init__(self)

    def get_column_names(self):
        return ("TRADEDATE", "SECID", "CLOSE", "TRADES")

    def get_data(self, etf_name, end_date, board, days=365):
        class CandlesData:
            """ Container that will be used by the handler to store data.
            Kept separately from the handler for scalability purposes: in order
            to differentiate storage and output from the processing.
            """

            def __init__(self):
                self.history = []

            def print_history(self):
                print "=" * 49
                print "|%15s|%15s|%15s|%15s|" % self.get_column_names()
                print "=" * 49
                for sec in self.history:
                    print "|%15s|%15s|%15.2f|%15d|" % (sec[0], sec[1], sec[2], sec[3])
                print "=" * 49

        if self.my_auth.is_real_time():
            iss = MicexISSClient(self.my_config, self.my_auth, self.MyDataHandler, CandlesData)
            end_date_str = end_date.strftime("%Y-%m-%d")
            start_date = (end_date - timedelta(days=days)).strftime("%Y-%m-%d")

            iss.get_history_securities_by_range(engine='stock',
                                                market='shares',
                                                board=board,
                                                ticker=etf_name,
                                                start_date=start_date,
                                                stop_date=end_date_str,
                                                )

            df = pd.DataFrame(iss.handler.data.history, columns=self.get_column_names())

            df['TRADEDATE'] = df['TRADEDATE'].astype('datetime64[ns]')

            df = df[['TRADEDATE', 'CLOSE']]

            return df
        return []


class NowTQTF(Auth):
    def __init__(self):
        Auth.__init__(self)

    def get_data(self, forced_date):
        class FinExEtfData:
            """ Container that will be used by the handler to store data.
            Kept separately from the handler for scalability purposes: in order
            to differentiate storage and output from the processing.
            """

            def __init__(self):
                self.history = []

            def print_history(self):
                print "=" * 49
                print "|%15s|%15s|" % ("SECID", "CLOSE")
                print "=" * 49
                for sec in self.history:
                    # if 'FX' in sec[0]:
                    print "|%15s|%15.2f|" % (sec[0], sec[1])
                print "=" * 49

        # Q: точность до скольки знаков? 2-х достаточно
        if self.my_auth.is_real_time():
            iss = MicexISSClient(self.my_config, self.my_auth, self.MyDataHandler, FinExEtfData)
            date = datetime.now().strftime("%Y-%m-%d")
            if forced_date:
                date = forced_date
            iss.get_history_securities(engine='stock',
                                       market='shares',
                                       board='tqtf',
                                       date=date)
            iss.handler.data.print_history()


class AllETFs(Auth):
    def __init__(self):
        Auth.__init__(self)
        self.boards = ['tqtf'.upper(), 'tqtd'.upper()]

    def get_names(self, tickets_filter=[], boards_filter=[]):
        class FinExEtfData:
            """ Container that will be used by the handler to store data.
            Kept separately from the handler for scalability purposes: in order
            to differentiate storage and output from the processing.
            """

            def __init__(self):
                self.history = []
                self.ticker_to_board = {}

            def print_history(self):
                print "=" * 49
                print "|%15s|%15s|%15s" % ("SECID", "CLOSE", "BOARD")
                print "=" * 49

                ticker_to_board = {}

                for sec in self.history:
                    t = sec[0]
                    b = sec[3]
                    print "|%15s|%15.2f|%15s" % (sec[0], sec[1], sec[3])

                    def read_add():
                        if not t in ticker_to_board:
                            ticker_to_board[t] = []
                        ticker_to_board[t].append(b)

                    good = False

                    if tickets_filter or boards_filter:
                        if tickets_filter and boards_filter:
                            for f in tickets_filter:
                                if f in t:
                                    for b_ in boards_filter:
                                        if b_ == b:
                                            good = True

                        elif tickets_filter:
                            for f in tickets_filter:
                                if f in t:
                                    good = True
                        elif boards_filter:
                            for b_ in boards_filter:
                                if b_ == b:
                                    good = True
                    else:
                        good = True

                    if good:
                        read_add()
                print "=" * 49
                self.ticker_to_board = ticker_to_board

        # Q: точность до скольки знаков? 2-х достаточно
        if self.my_auth.is_real_time():
            iss = MicexISSClient(self.my_config, self.my_auth, self.MyDataHandler, FinExEtfData)
            for board in self.boards:
                iss.get_all_by_board(engine='stock',
                                     market='shares',
                                     board=board)
            iss.handler.data.print_history()

            return iss.handler.data.ticker_to_board


def main():
    now_tqtf = NowTQTF()
    now_tqtf.get_data()


if __name__ == '__main__':
    try:
        main()
    except:
        print "Sorry:", sys.exc_type, ":", sys.exc_value
