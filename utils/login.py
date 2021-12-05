import requests
import json
from utils.ids_encrypt import encryptAES
from bs4 import BeautifulSoup

import urls


def login(card_num, password):
    print("开始登陆")
    s = _login(card_num, password)
    while s is False or s is None:
        print("请重新登陆")
        card_num = input("请输入帐号:")
        password = input("请输入密码:")
        print("开始登陆")
        s = _login(card_num, password)
    print("登陆成功")
    return s


# 登录信息门户，返回登录后的session
def _login(card_num, password):
    ss = requests.Session()
    form = {"username": card_num}

    #  获取登录页面表单，解析隐藏值
    url = urls.login_home
    res = ss.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    attrs = soup.select('[tabid="01"] input[type="hidden"]')
    for k in attrs:
        if k.has_attr('name'):
            form[k['name']] = k['value']
        elif k.has_attr('id'):
            form[k['id']] = k['value']
    form['password'] = encryptAES(password, form['pwdDefaultEncryptSalt'])
    # 登录认证
    res = ss.post(url, data=form, allow_redirects=False)
    # 登录ehall
    ss.get(urls.login_service)

    res = ss.get(urls.user_desktop)
    print(res)
    json_res = json.loads(res.text)
    try:
        name = json_res["userName"]
        print(name[0], "** 登陆成功！")
    except Exception:
        print("认证失败！")
        return False

    return ss
