#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# Created by ShoJinto at 2022/12/5

import os
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from quart import Quart, request, jsonify

app = Quart(__name__)

options = Options()
options.add_argument("--disable-popup-blocking ")
DEVELOPMENT = os.environ.get("DEVELOPMENT", default=True)
driver_executor = "chromedriver.exe" if DEVELOPMENT is True else None

DRIVER = {}  # 全局变量保存driver对象，以便chromedriver复用

result_structure = {
    "status": "suc"
}


async def init_webdirver():
    """
    利用Quart的background_task机制在simple-cookieAPI启动的时候就初始化一个带界面的chromedirver
    """
    if DEVELOPMENT is True:
        driver = uc.Chrome(driver_executable_path=driver_executor, options=options)
    else:
        driver = uc.Chrome(options=options)
    driver.get("https://bot.sannysoft.com/")
    DRIVER.setdefault("webdriver", driver)
    print('webdriver Initialization complete')


async def project_login(url):
    """
    项目登录，由于登录操作太过花哨，因此采用人工方式进行
    """
    driver = DRIVER.get("webdriver")
    driver.get(url)
    return driver


async def project_cookies(driver, url=None):
    """
    url: 默认为空，要获取只当页面的cookie请传递url
    返回指定页面的cookies默认返回项目登录后的cookie
    """
    cookies = driver.get_cookies()
    if url is not None:
        driver.get(url)
        cookies = driver.get_cookies()
    return cookies


@app.before_serving
async def startup():
    app.add_background_task(init_webdirver)


@app.route('/jbos', methods=['POST'])
async def create_job():
    try:
        data = await request.get_json()
        url = data['url']
        operate = data['operate']
        driver = DRIVER.get("webdriver")
        if operate != "getCookies":
            raise "operate optional error"
        if operate == "login":
            driver = await project_login(url)
        result = await project_cookies(driver, url)
    except Exception as ex:
        result = {
            f'request body missing {ex}, e.g': {
                "operate": "login",
                "url": "https://nowsecure.nl"
            }, 'notes': "operate optional: [login|getCookies]"
        }
    result_structure["result"] = result
    return jsonify(result_structure)


@app.get("/")
async def index():
    result_structure["result"] = "welcome to simple cookie api"
    return jsonify(result_structure)


def run() -> None:
    app.run()


if __name__ == "__main__":
    run()

