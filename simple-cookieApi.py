#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# Created by ShoJinto at 2022/12/5

import os
import sys
import json
import base64
import random

import undetected_chromedriver as uc

from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor, as_completed
from quart import Quart, request, jsonify, render_template_string

app = Quart(__name__)

options = Options()
options.add_argument("--disable-popup-blocking")
POOL_SIZE = os.environ.get("POOL_SIZE", default=1)
DRIVER = []  # 全局变量保存driver对象，以便chromedriver复用

response_structure = {
    "status": "suc"
}

response_exception_template = """{{
    "request body missing: {ex}, e.g": {{
        "url": "https://nowsecure.nl/{operate}"
    }}
}}"""

platform = sys.platform
if platform.endswith("win32"):
    driver_executor = "chromedriver.exe"
if platform.endswith("linux"):
    driver_executor = "/usr/bin/chromedriver"
if platform.endswith("darwin"):
    driver_executor = "/usr/bin/chromedriver"


def headers_callback(headers):
    print(headers)


async def init_webdriver(pool_size=int(POOL_SIZE)):
    """
    利用Quart的background_task机制在simple-cookieAPI启动的时候就初始化一个带界面的chromedirver
    引入多线程实现后端chromedriver池化
    """

    def driver_warpper(kwargs):
        """
        其实undetected_chromedriver已经有自动获取chromedriver对应版本的逻辑，但是由于“你懂的”原因这里需要封装一下chrome实例化过程，
        以便ThreadPoolExecutor能够顺利将参数传递给chrome实例对象
        """
        driver = uc.Chrome(**kwargs)
        return driver

    driver_options = {"driver_executable_path": driver_executor,
                      "options": options,
                      "enable_cdp_events": True}

    with ThreadPoolExecutor() as executor:
        tds = []
        for num in range(pool_size):
            td = executor.submit(driver_warpper, kwargs=driver_options)
            tds.append(td)
        for td in as_completed(tds):
            DRIVER.append({"webdriver": td.result(), "state": "init"})
    print("Webdriver pool initialization complated")


async def async_login(drivers, domain, url, cookies):
    for driver in drivers:
        driver = driver.get("webdriver")
        driver.delete_all_cookies()
        _abs_url = ""  # 标志位，domain重复的cookie将跳过driver的get方法
        for cookie in cookies:
            if cookie["domain"].startswith(".") and cookie["domain"] == f".{domain}":
                _url = "https://www" + cookie["domain"]
            elif cookie["domain"].startswith(".") and cookie["domain"] != f".{domain}":
                _url = "https://" + cookie["domain"].strip(".")
            else:
                _url = "https://" + domain
            # chromedriver添加cookie是带domain的所以在添加cookie之前需要先打开页面
            if domain != _abs_url: driver.get(_url)
            driver.add_cookie(cookie)
            _abs_url = domain
        driver.get(url)  # 刷新页面


async def webdriver(state, webdrv=None):
    """
    在异步情况下，为webdriver设置锁，webdriver有三个状态：init、locked、unlock。非locked情况下才能接受新的请求任务
    并发情况下获取一个空闲webdriver对象，默认异步情况下初始化3个webdriver。循环随机获取空闲的webdriver以达到webdriver侧负载均衡的目的
    webdrv 需要解锁的webdriver对象的形参，解锁需要传递此参数
    """
    while True:
        _DRIVER = random.choice(DRIVER)
        locked_webdrv = webdrv if _DRIVER["webdriver"] == webdrv else None
        _state = _DRIVER.get("state")
        driver = _DRIVER.get("webdriver") if _state != 'locked' else locked_webdrv
        if driver:
            # 更新webdriver的状态，类似给当前运行的webdriver加锁🔒
            DRIVER.remove(_DRIVER)
            _DRIVER.update({"state": state})
            DRIVER.append(_DRIVER)
            break
    return driver


@app.before_serving
async def startup():
    app.add_background_task(init_webdriver)


@app.route('/login', methods=['POST'])
async def project_login():
    """
    项目登录，由于登录操作太过花哨，因此采用人工方式进行
    """
    try:
        request_data = await request.get_json()
        url = request_data["url"]

        _DRIVER = random.choice(DRIVER)
        driver = _DRIVER.get("webdriver")
        driver.get(url)
        response_structure["message"] = "logined"

        response_entry = response_structure
    except Exception as ex:
        message = response_exception_template.format(ex=ex, operate="login")
        response_entry = message

    return jsonify(response_entry)


@app.route('/getcookies', methods=['POST'])
async def project_cookies():
    """
    url: 默认为空，要获取只当页面的cookie请传递url
    返回指定页面的cookies默认返回项目登录后的cookie
    """
    try:
        request_data = await request.get_json()
        driver = await webdriver("locked")
        if request_data:
            url = request_data["url"]
            driver.get(url)
        cookies = driver.get_cookies()
        await webdriver("unlock", driver)
        b64_cookies = base64.b64encode(json.dumps(cookies).encode('utf8')).decode('utf8')

        response_structure["cookies"] = cookies
        response_structure["b64_cookies"] = b64_cookies

        response_entry = response_structure
    except Exception as ex:
        message = response_exception_template.format(ex=ex, operate="getcookies")
        response_entry = message

    return jsonify(response_entry)


@app.route('/login_with_cookies', methods=['POST'])
async def login_with_cookies():
    """
    使用现有cookie登录
    """
    try:
        request_data = await request.get_json()

        try:
            url = request_data["url"]
            cookies = request_data["cookies"]
            domain = request_data["domain"]
        except KeyError as ex:
            raise ex

        cookies = json.loads(base64.b64decode(cookies).decode('utf8'))
        await async_login(DRIVER, domain, url, cookies)

        response_structure["message"] = "logined with cookie"
        response_entry = response_structure
    except Exception as ex:
        message = response_exception_template.format(ex=ex, operate="login_with_cookies")
        response_entry = message

    return jsonify(response_entry)


@app.route('/getcontent', methods=['POST'])
async def get_content():
    try:
        data = await request.get_json()
        url = data['url']
        driver = await webdriver("locked")
        driver.get(url)
        content = driver.page_source
        await webdriver("unlock", driver)  # 处理完请求对webdriver进行解锁操作
        response_structure["content"] = content
        response_entry = response_structure
    except Exception as ex:
        message = response_exception_template.format(ex=ex, operate="getcontent")
        response_entry = message

    return jsonify(response_entry)


@app.get("/")
async def index():
    return await render_template_string(source="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple Cookie API</title>
</head>
<body>
<h1>欢迎使用Simple Cookie API</h1>
<div style="text-align:left">
    <span>
    具体用法见demo.py
    </span>
</div>
</body>
</html>
""")


def run() -> None:
    app.run()


if __name__ == "__main__":
    run()
