# cookieApi

## 缘起

为什么会有这个项目呢？偶然间遇到要获取某个网站上数据的需求。经过分析发现他的反爬说简单也简单，说复杂呢？你又说不上来，为什么呢？他的一些请求参数根本就不是在客户端生成。比如，我要拿`/data/detial/conent`
的内容他的请求参数是：`/data/detial/conent?paramid=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
后面的参数是通过请求接口`/doc/xxx/yyy/bbb?aaid=xxxxxxxxxx`和`/aaa/xxx/yyy/bbb?aaid=xxxxxxxxxx`
...后面的接口是302跳转，respons的header中含有下一个接口地址以及他会更新cookie信息，以至于最终的请求header和cookie难以跟踪至于最终要302几次我觉得应该是取决于网站开发者。尝试了很久最终选择放弃，进而谋生本项目。

## 更新日志

- 在上一版本的基础上调整了URL，将单一视图函数才分成多个视图，降低视图函数的逻辑复杂度。
- 实现了chromedriver的多线程，以满足异步爬虫调用发生后端chrome实例阻塞的情况，默认单chrome实例。
- 实现cookie登录功能，以满足多线程情况下不同chrome实例需要重复登录或者单chrome实例重启后需要重新登录的情况。
- 新增dome脚本

## 项目介绍

大家都知道selenium速度慢，所以大佬的爬虫都是去逆向原站的js获取起加密算法已过掉原站的反爬机制。但是别人的js机密不是那么好逆向的，而selenium可以伪装成真正的浏览器从而可以拿到最终的html代码。本项目利用selenium的特性拿到浏览器中的cookie信息，再通过`quart`
提供的webAPI能力将其公布出来方便requests调用。通过这种简单的封装可以实现所有网站不需要js逆向也可以获取他的的cookie，至于速度问题：拿数据用requests，当cookie失效的时候再来接口上取一下cookie。

- 项目依赖

```shell
0. python3.8.x 
1. selenium
2. undetected_chromedriver # 屏蔽chromedriver 浏览器指纹
3. qurat # flask的异步实现，都是同一个团队的作品
4. docker # 容器化方便部署
```

- 项目结构

```shell
├── Dockerfile
├── requirements.txt
├── simple-cookieApi.conf 
└── simple-cookieApi.py
```

- 运行项目

```shell
root@7197f225bd7d:/# git clone https://github.com/shojinto/simple-cookieApi.git
root@7197f225bd7d:/# docker build -t <yourdockerimagename> .
root@7197f225bd7d:/# docker run -d -p 8080:8080 -p 5900:59000 <yourdockerimagename>
root@7197f225bd7d:/# docker run -d -e POOL_SIZE=3 -p 8080:8080 -p 5900:59000 <yourdockerimagename> #多线程chrome后端启动
```

- 功能介绍

目前只实现了手动登录和获取cookie两个接口
> 操作步骤：
>
> 1 启动项目，使用vnc客户端工具登录容器，默认密码：secret。登录到容器GUI界面后你会看到 https://bot.sannysoft.com/ 的主页展示了可能会被侦测到的浏览器指纹。你有可以在浏览器地址栏输入：https://nowsecure.nl 是否通过指纹检测进行验证。
>
> 2 调用接口，或者直接浏览器地址连输入http://127.0.0.1:8000 查看接口用法

- 效果展示

```shell
root@7197f225bd7d:/# echo '{
>     "url": "https://domain.net",
>     "operate":"getcookies"
> }' |  \
>   http POST http://127.0.0.1:8000/jbos \
>   Content-Type:application/json \
>   Postman-Token:c870ddc9-e512-42a9-9364-d9efd2ab02d8 \
>   cache-control:no-cache
HTTP/1.1 200
content-length: 3071
content-type: application/json
date: Wed, 07 Dec 2022 06:08:02 GMT
server: hypercorn-h11

{
    "b64_cookies": "W3siZG9tYWluIjogIi5jbmtpLm5ldCIsICJleHBpcnkiOiAxNjcxMjY4NDQ3LCAiaHR0cE9ubHkiOiBmYWxzZSwgIm5hbWUiOiAiY19tX2V4cGlyZSIsICJwYXRoIjogIi8iLCAic2VjdXJlIjogdHJ1ZSwgInZhbHVlIjogIjIwMjItMTItMTclMjAxNyUzQTE0JTNBMDcifSwgeyJkb21haW4iOiAIjogIi8iLCAic2VjdXJlIjogdHJ1ZSw.....lLCAidmFsdWUiOiAidHJ1ZSJ9XQ=="
    "cookies": [
        {
            "domain": ".domain.net",
            "httpOnly": false,
            "name": "Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac",
            "path": "/",
            "secure": false,
            "value": "1670393282"
        },
        {
            "domain": "www.domain.net",
            "expiry": 1670395077,
            "httpOnly": true,
            "name": "acw_tc",
            "path": "/",
            "secure": false,
            "value": "276077ca16703932768538537e1a4e16c84b962fe713e14cb36c005c5d9dde"
        },
        {
            "domain": ".domain.net",
            "expiry": 1685945278,
            "httpOnly": false,
            "name": "ssxmod_itna",
            "path": "/",
            "secure": false,
            "value": "YqUx0DBDnD2034Qq0L9mxjgexgedYKNHHDl2DWueiODUxn4iaDT=OQ=7QGIiWRThreQKtELYqq3KW4x5so=th0eDQxY6FDfqDzDDhd4QD/4w+oYIDYYDtxBAfD3RdDWCqB6MDtqDkLD0+HD7pFlx08DeFdz2DDUerwKWyQDCyaD7KDn=qDAhYDm64DRgPDe64D91PDw6Rm8xG7DAyAyxi3cODHK0LxDQmxpKv69K7p7UEvhbSv+zPfw8koB6vszxib6j8wcr1sL7dt3WRDv1u=ACbeQBm4KQnO4=GerGRDq02PAAiqqBDVmBC9iDD==="
        }
    ],
    "status": "suc"
}

```

## 特别说明

本项目仅限于学习，请勿用于商业用途，产生法律风险自负

