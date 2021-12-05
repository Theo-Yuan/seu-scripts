import smtplib
from email.mime.text import MIMEText


def send_email(mail_host, mail_user, mail_pass, sender, receivers, messageText):
    message = MIMEText(messageText, 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = messageText
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP()
        # 连接到服务器
        smtpObj.connect(mail_host, 25)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(sender, receivers, message.as_string())
        # 退出
        smtpObj.quit()
    except smtplib.SMTPException as e:
        print('send email error', e)  # 打印错误
    except Exception as e:
        print(e)
