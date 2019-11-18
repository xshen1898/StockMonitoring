#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author shen.charles@hotmail.com
 
import time
import logging
import random

import requests
import urllib
import urllib3
from lxml import etree

from PIL import Image
from io import BytesIO


class AuthenticationException(Exception):
    def __init__(self):
        super().__init__('Authentication Failed!')


class StockTradeService(object):
    def __init__(self, *, uid, password):
        self.uid = uid
        self.password = password
        self.sess = requests.session()
        self.validatekey = ''

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if not self.authentication():
            raise AuthenticationException()
 
    def get_identify_code(self):
        randNumber = random.random()-0.00000000000000009
        url = 'https://jy.xzsec.com/Login/YZM?randNum='+str(randNumber)
        headers = {
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'jy.xzsec.com',
            'Referer': 'https://jy.xzsec.com/',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        }
        response = self.sess.get(url, headers=headers, verify=False)
        image = Image.open(BytesIO(response.content))
        image.show()
        identifyCode = input('输入验证码: ')
        return randNumber, identifyCode

    def authentication(self):
        url = 'https://jy.xzsec.com/Login/Authentication?validatekey='
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '112',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'jy.xzsec.com',
            'Origin': 'https://jy.xzsec.com',
            'Referer': 'https://jy.xzsec.com/',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        randNumber, identifyCode = self.get_identify_code()
        data = {
            'userId': self.uid,
            'password': self.password,
            'randNumber': randNumber,
            'identifyCode': identifyCode,
            'duration': 1800,
            'authCode': '',
            'type': 'Z'
        }
        response = self.sess.post(url, data=data, headers=headers, verify=False)
        if response.status_code == 200:
            r_json = response.json()
            if r_json['Status'] == 0:
                self.validatekey = self.get_validate_key()
                result = True
            else:
                result = False
        else:
            result = False
        return result
 
    def get_validate_key(self):
        url = 'https://jy.xzsec.com/Trade/Buy'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'jy.xzsec.com',
            'Referer': 'https://jy.xzsec.com/',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        }
        response = self.sess.get(url, headers=headers, verify=False)
        html = etree.HTML(response.text)
        em_validatekey = html.xpath('//input[@id="em_validatekey"]')[0].get('value')
        return em_validatekey
 
    def get_stock_list(self):
        url = 'https://jy.xzsec.com/Search/GetStockList?validatekey={}'.format(self.validatekey)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '14',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'jy.xzsec.com',
            'Origin': 'https://jy.xzsec.com',
            'Referer': 'https://jy.xzsec.com/Trade/Buy',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = {
            'qqhs': 1000,
            'dwc': ''
        }
        response = self.sess.post(url, data=data, headers=headers, verify=False)
        r_json = response.json()
        stock_list = r_json['Data']
        return stock_list

    def submit_trade(self, zqdm, price, amount, trade_type, zqmc, gddm):
        url = 'https://jy.xzsec.com/Trade/SubmitTrade?validatekey={}'.format(self.validatekey)
        r_data = {
            'code': zqdm,
            'name': zqmc,
            'moneytype': '元',
            'type': '',
            'zqlx': 0,
            'mt': 2,
        }
        if trade_type == 'B':
            r_data['type'] = 'buy'
            referer = 'https://jy.xzsec.com/Trade/Buy?{}'.format(urllib.parse.urlencode(r_data))
        elif trade_type == 'S':
            r_data['type'] = 'sale'
            r_data['gddm'] = gddm
            referer = 'https://jy.xzsec.com/Trade/Sale?{}'.format(urllib.parse.urlencode(r_data)).replace('&', '&amp;')
        else:
            referer = 'https://jy.xzsec.com/'
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '101',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'jy.xzsec.com',
            'Origin': 'https://jy.xzsec.com',
            'Referer': referer,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = {
            'stockCode': zqdm,
            'price': price,
            'amount': amount,
            'tradeType': trade_type,
            'zqmc': zqmc
        }
        if trade_type == 'S':
            data['gddm'] = gddm
        output = {}
        output['data'] = data
        response = self.sess.post(url, data=data, headers=headers, verify=False)
        output['result'] = response.json()
        return output

    def get_revoke_list(self):
        url = 'https://jy.xzsec.com/Trade/GetRevokeList?validatekey={}'.format(self.validatekey)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'jy.xzsec.com',
            'Origin': 'https://jy.xzsec.com',
            'Referer': 'https://jy.xzsec.com/Trade/Revoke',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        response = self.sess.post(url, headers=headers, verify=False)
        r_json = response.json()
        revoke_list = r_json['Data']
        return revoke_list

    def submit_revoke(self, zqmc, wtrq, wtbh):
        url = 'https://jy.xzsec.com/Trade/RevokeOrders?validatekey={}'.format(self.validatekey)
        headers = {
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '21',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'jy.xzsec.com',
            'Origin': 'https://jy.xzsec.com',
            'Referer': 'https://jy.xzsec.com/Trade/Revoke',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = {
            'revokes': '{}_{}'.format(wtrq, wtbh)
        }
        output = {}
        output['Zqmc'] = zqmc
        output['data'] = data
        response = self.sess.post(url, data=data, headers=headers, verify=False)
        output['result'] = response.text
        return output

    def get_hold(self):
        t = round(time.time() * 1000)
        url = 'https://jy.xzsec.com/AccountAnalyze/Asset/GetHold?v={}'.format(t)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'jy.xzsec.com',
            'Referer': 'https://jy.xzsec.com/AccountAnalyze/Asset',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        response = self.sess.get(url, headers=headers, verify=False)
        r_json = response.json()
        fund_avl = r_json['ResultObj'][0]['FundAvl']
        return fund_avl
