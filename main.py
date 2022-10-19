import wechatsogou

ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)
result = ws_api.search_gzh('惠民保')

for i in result:
    print(i)

