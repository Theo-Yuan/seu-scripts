# login #
card_num = '*****'
password = '*****'

# main #
interval = 1.5
thread_num = 1


# reserve #
'''
ReserveTimes:
    11:30-12:30
    12:30-13:30
    18:00-19:00
    19:00-20:00
    20:00-21:00
item:
    7: ping-pong，10: badminton
'''
reserve_data = {
    'reservetime': '2021-11-26 11:30-12:30',
    'item': 7,
    'phone': '*****'
}


# daily report #
daily_time = (8, 55)
user_list = [('card_num1', 'password1', 'xxx@xx'),
             ('card_num2', 'password2', 'yyy@yy')]
sender_cfg = {
    'mail_host': 'smtp.xx.com',
    'mail_user': 'xxx',
    'mail_pass': 'xxx',
    'sender': 'xxx@xx'
}
