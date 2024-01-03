import smtplib
from email.header import Header
from email.mime.text import MIMEText


def send_email(content, subject='按罪人名单降下终末', title='白嫖完再取关？什么人啊？拉黑了'):
    # 邮件内容
    body = f'''
    <html>
        <body>
            <h1>{title}</h1><br>
            {content}
        </body>
    </html>
    '''

    # 构建邮件
    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = 'bilibili-message@foxmail.com'
    msg['To'] = 'george_chou@foxmail.com'

    # 发送邮件
    smtp_server = 'smtp.qq.com'
    smtp_port = 587
    sender_email = 'bilibili-message@foxmail.com'
    password = 'plwetxfprimmdjbf'

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, [msg['To']], msg.as_string())

        print('邮件发送成功')

    except smtplib.SMTPException as e:
        print('邮件发送失败:', str(e))
