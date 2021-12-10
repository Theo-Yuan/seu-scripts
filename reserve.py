import ssl
import pytesseract
from PIL import Image

from utils.login import login
import config
import urls


def main():
    ssl._create_default_https_context = ssl._create_unverified_context

    card_num = config.card_num
    print(card_num)
    print("请输入密码:")
    password = config.password
    print('*'*len(password))
    print("开始登陆")
    s = login(card_num, password)

    res = s.get(urls.res_val_image, allow_redirects=True)
    # print(res)
    # return
    res = s.get(str(res.content).split(".href='")[-1].split("'</script>")[0])
    with open('validateimage.jpg', 'wb') as file:
        file.write(res.content)

    img = Image.open('validateimage.jpg')
    valid_s = pytesseract.image_to_string(img)

    postdata = {
        'orderVO.useTime': config.reserve_data['reservetime'],
        'orderVO.itemId': config.reserve_data['item'],
        'orderVO.useMode': '2',
        'orderVO.phone': config.reserve_data['phone'],
        'orderVO.remark': '',
        'validateCode': valid_s,
    }

    res = s.post(urls.res_url, data=postdata, allow_redirects=False)
    print(res.status_code)
    print(res.text)


if __name__ == '__main__':
    main()
