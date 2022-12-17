#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# Created by ShoJinto at 2022/12/17
"""
这是simplie-cookieApi的示例代码，其中login部分由于需要手动操作所以没有给出示例
"""

import requests
import json


def get_cookies(url=None):
    cookies = {}
    if url:
        data = {"url": url}
        r = requests.post(url="http://127.0.0.1:5000/getcookies", data=json.dumps(data),
                          headers={'Content-Type': 'application/json'})
    else:
        r = requests.post(url="http://127.0.0.1:5000/getcookies")
    data = r.json()
    for item in data['cookies']:
        cookies[item["name"]] = item["value"]
    return cookies


def get_content(url):
    """
    对于js加密特别恶心的情况可以用这个
    """
    data = {"url": url}
    r = requests.post(url="http://127.0.0.1:5000/getcontent", data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})
    data = r.json()["content"]
    return data


def login_with_cookie(url):
    """
    url:登录成功后需要跳转的页面url
    """
    data = {"url": url}
    r = requests.post(url="http://127.0.0.1:5000/login_with_cookies", data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})
    data = r.json()
    return data

