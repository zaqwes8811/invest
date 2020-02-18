#!/usr/bin/env python
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

from iss_simple_client import Config
from iss_simple_client import MicexAuth
from iss_simple_client import MicexISSClient
from iss_simple_client import MicexISSDataHandler


class MyData:
    """ Container that will be used by the handler to store data.
    Kept separately from the handler for scalability purposes: in order
    to differentiate storage and output from the processing.
    """

    def __init__(self):
        self.history = []

    def print_history(self):
        print "=" * 49
        print "|%15s|%15s|%15s|%15s|" % ("TRADEDATE", "SECID", "CLOSE", "TRADES")
        print "=" * 49
        for sec in self.history:
            print "|%15s|%15s|%15.2f|%15d|" % (sec[0], sec[1], sec[2], sec[3])
        print "=" * 49


class MyDataHandler(MicexISSDataHandler):
    """ This handler will be receiving pieces of data from the ISS client.
    """

    def do(self, market_data):
        """ Just as an example we add all the chunks to one list.
        In real application other options should be considered because some
        server replies may be too big to be kept in memory.
        """
        self.data.history = self.data.history + market_data


def main():
    f = open(expanduser("~") + "/credentials", "r")
    pair = f.read()

    user, password = pair.split(' ')
    user = user.strip()
    password = password.strip()
    my_config = Config(user=user, password=password, proxy_url='')
    my_auth = MicexAuth(my_config)
    if my_auth.is_real_time():
        iss = MicexISSClient(my_config, my_auth, MyDataHandler, MyData)
        # iss.get_history_securities(engine='stock',
        #                            market='shares',
        #                            board='tqtf',
        #                            date='2020-02-12')
        # iss.handler.data.print_history()

        # from=2010-08-23&till=2010-08-24
        iss.get_history_securities_by_range(engine='stock',
                                            market='shares',
                                            board='tqtf',
                                            ticker='FXRU',
                                            start_date='2019-01-12',
                                            stop_date='2020-02-12',
                                            )
        iss.handler.data.print_history()

    # http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqtf/securities.json?from=2018-08-08&till=2018-08-25&interval=24&start=0
    # http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqtf/securities/FXRU/candles.json?from=2018-08-08&till=2018-08-25&interval=24&start=0


if __name__ == '__main__':
    try:
        main()
    except:
        print "Sorry:", sys.exc_type, ":", sys.exc_value
