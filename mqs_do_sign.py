import requests
from lxml import etree
import smtplib, os
from datetime import datetime
from email.mime.text import MIMEText

import pytz

data = {
    'action': 'user_login',
    'username': os.getenv('USERNAME'),
    'password': os.getenv('PASSWORD'),
    'rememberme': '1',
}

response = requests.post('https://www.manqushe.com/wp-admin/admin-ajax.php',
                         data=data)
print(response.json())
cookies = response.cookies.get_dict()['wordpress_logged_in_01ba427a8d5e6f5a50b63c670bf1dea6']
cookies_ = {
    'wordpress_logged_in_01ba427a8d5e6f5a50b63c670bf1dea6': cookies
}
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

response = requests.get('https://www.manqushe.com/user', cookies=cookies_, headers=headers)
tree = etree.HTML(response.text)
nonce = ''.join(tree.xpath(f'//div[@class="card-body"][1]//button//@data-nonce'))
data = {
    'action': 'user_qiandao',
    'nonce': nonce,
}
response = requests.post('https://www.manqushe.com/wp-admin/admin-ajax.php', cookies=cookies_, headers=headers,
                         data=data)
print(response.json())
res = ''
if response.json()['status'] == '0':
    res += response.json()['msg']
elif response.json()['status'] == '1':
    res += response.json()['msg']
else:
    res += '签到失败'


def get_beijing_time():
    # 设置UTC和北京时间的时区
    utc_zone = pytz.utc
    beijing_zone = pytz.timezone('Asia/Shanghai')
    # 获取当前的UTC时间，并添加UTC时区信息
    utc_time = datetime.now(utc_zone)
    # 将UTC时间转换为北京时间
    beijing_time = utc_time.astimezone(beijing_zone)
    # 格式化北京时间为 "年-月-日 星期几 时:分" 格式
    return beijing_time.strftime('%Y-%m-%d %A %H:%M')


def send_QQ_email_plain(content):
    sender = user = '1781259604@qq.com'
    passwd = 'tffenmnkqsveccdj'

    # 格式化北京时间为 "年-月-日 星期几 时:分" 格式
    formatted_date = get_beijing_time()

    # 纯文本内容
    msg = MIMEText(f'签到结果：{content}', 'plain', 'utf-8')

    # 设置邮件主题为今天的日期和星期
    msg['From'] = f'{sender}'
    msg['To'] = os.getenv('EMAIL_ADDRESS')
    # msg['To'] = '2951509921@qq.com'
    msg['Subject'] = f'{formatted_date}'  # 设置邮件主题

    try:
        # 建立 SMTP 、SSL 的连接，连接发送方的邮箱服务器
        smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)

        # 登录发送方的邮箱账号
        smtp.login(user, passwd)

        # 发送邮件：发送方，接收方，发送的内容
        smtp.sendmail(sender, os.getenv('EMAIL_ADDRESS'), msg.as_string())

        print('邮件发送成功')

        smtp.quit()
    except Exception as e:
        print(e)
        print('发送邮件失败')


send_QQ_email_plain(res)
