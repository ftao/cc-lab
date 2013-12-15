'''
Fetch / Analyse Trade History

Usage: 
  cclab-history fetch -m <market> -o <output> [-s <since>] [-v]

Options:
  -m <market> --market <market>  Market name to fetch data from
  -o <output> --output <output>  Output file [default:-]
  -s <since> --since <since>     Fetch data after since
  -v --verbose  Be verbose, more logging

'''

import sys
import json
import logging

from docopt import docopt

from cclab.trade.common import setup_logging
from cclab.trade.markets.btcchina import BtcChinaMarket

def dump(path, records):
    if path == '-':
        _dump(sys.stdout, records)
    else:
        with open(path, 'a') as fp:
            _dump(fp, records)

def _dump(fp, records):
    for rec in records:
        fp.write(json.dumps(rec))
        fp.write("\n")

def fetch(since=0):
    m = BtcChinaMarket(None, None)
    while True:
        trades = m.get_trade_history(since=since)
        if len(trades) == 0:
            break
        for item in trades:
            yield item
        since = trades[-1]['id']
        logging.debug("fetch %d records since %s", len(trades), since)

def main():
    args = docopt(__doc__, help=True)
    market = args.get("--market")
    output = args.get("--output")
    since = args.get("--since")
    if args.get("--verbose"):
        setup_logging(True)
    else:
        setup_logging(False)

    if since is None:
        since = 0
    else:
        since = int(since)

    assert market.lower() == "btcchina"
    dump(output, fetch(since))

if __name__ == "__main__":
    main()



