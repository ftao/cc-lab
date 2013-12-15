import hmac
import hashlib
import base64
import json
import time
import re
import logging
import requests

#from cclab.trade.markets.base import Market

class BtcChinaMarket(object):
    name = "BtcChina"

    exchange_pairs = [
        ('BTC', 'CNY')
    ]

    api_root = 'https://api.btcchina.com/api_trade_v1.php'

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

        self.balance = {}

        self.session = requests.Session()

    def __str__(self):
        return "%s: %s" % (self.name, str(self.balance))

    def get_info(self):
        info = self.get_account_info()
        self.balance['CNY'] = float(info['balance']['cny']['amount'])
        self.balance['BTC'] = float(info['balance']['btc']['amount'])

    def get_balance(self, currency):
        try:
            return float(self.balance.get(currency.upper(), 0))
        except:
            return 0

    def buy(self, amount, price):
        post_data = {}
        post_data['method'] = 'buyOrder'
        post_data['params'] = [price,amount]
        return self._private_request(post_data)

    def sell(self, amount, price):
        post_data = {}
        post_data['method'] = 'sellOrder'
        post_data['params'] = [price,amount]
        return self._private_request(post_data)

    def get_account_info(self):
        post_data = {}
        post_data['method']='getAccountInfo'
        post_data['params']=[]
        return self._private_request(post_data)


    def _get_tonce(self):
        return int(time.time()*1000000)
 
    def _get_params_hash(self,pdict):
        pstring=""
        # The order of params is critical for calculating a correct hash
        fields=['tonce','accesskey','requestmethod','id','method','params']
        for f in fields:
            if pdict[f]:
                if f == 'params':
                    # Convert list to string, then strip brackets and spaces
                    # probably a cleaner way to do this
                    param_string=re.sub("[\[\] ]","",str(pdict[f]))
                    param_string=re.sub("'",'',param_string)
                    pstring+=f+'='+param_string+'&'
                else:
                    pstring+=f+'='+str(pdict[f])+'&'
            else:
                pstring+=f+'=&'
        pstring=pstring.strip('&')
 
        # now with correctly ordered param string, calculate hash
        phash = hmac.new(bytes(self.secret_key, "UTF-8"), bytes(pstring, "UTF-8"), hashlib.sha1).hexdigest()
        return phash

    def _private_request(self, post_data):
        #fill in common post_data parameters
        tonce=self._get_tonce()
        post_data['tonce'] = tonce
        post_data['accesskey'] = self.access_key
        post_data['requestmethod'] = 'post'
 
        # If ID is not passed as a key of post_data, just use tonce
        if not 'id' in post_data:
            post_data['id'] = tonce
 
        pd_hash=self._get_params_hash(post_data)
 
        # must use b64 encode        
        auth_string = 'Basic ' + str(base64.b64encode(bytes(self.access_key+':'+pd_hash, "UTF-8")), "UTF-8")
        headers = {'Authorization' : auth_string, 'Json-Rpc-Tonce' : tonce}
 
        try:
            resp = self.session.post(
                self.api_root, 
                data=bytes(json.dumps(post_data), "UTF-8"),
                headers=headers
            )
            if resp.status_code == 200:
                resp_dict = json.loads(resp.text)
                if str(resp_dict['id']) == str(post_data['id']):
                    if 'result' in resp_dict:
                        return resp_dict['result']
                    elif 'error' in resp_dict:
                        logging.error('Got error when request BTCChina, %s' % resp_dict['error'])
                else:
                    logging.error('Got error when request BTCChina, %s' % "id not match")
        except Exception as err:
            logging.error('Can\'t request BTCChina, %s' % err)

        return None

    def get_trade_history(self, since=0):
        data_url = 'https://data.btcchina.com/data/historydata'
        resp = self.session.get(data_url + "?since=%d" %since)
        return sorted(map(self._convert, resp.json()), key=lambda x:x['id'])

    def _convert(self, trade):
        return {
            #TODO: find a better name 
            "gc" : "BTC",  #the currency as goods
            "cc" : "CNY",  #the currency as money

            "id" : int(trade["tid"]),
            "time" : int(trade["date"]),
            "type" : trade["type"],
            "amount" : trade["amount"],
            "price" : trade["price"],
        }
