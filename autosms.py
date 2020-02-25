from webbot import Browser
from bs4 import BeautifulSoup as bf4
import time
from slackclient import SlackClient
    
#crawler data
def crawler_data(phonenumber):
    result = ''
    web.type( phonenumber, tag= 'input', id = 'txtNumber')
    web.click(tag= 'input', id = 'SubmitButton2')
    source_web = web.get_page_source()
    if web.get_title() == 'CM. - SMS Logging':
        data_web = bf4(source_web, 'html.parser') 
        texts = data_web.select(".messageCell")
        print(texts)
        if len(texts) == 0: 
            return 'MXN chưa có! vui lòng gửi lại sau ít phút. Thanks'
        elif len(texts) > 0:
            for text in range(len(texts)):
                print(texts[text].get_text().replace('\n', ''))
                if 'Khoan vay cua ban duoc phe duyet' in texts[text].get_text():
                    result = texts[text].get_text().replace('\n', '')
                    print(result)
                    break
                if len(texts[text].get_text().replace('\n', '').split(' ')[0]) == 4 and texts[text].get_text().replace('\n', '').split(' ')[0].isdigit():
                    if result == '' or len(result.split(' ')[0]) == 6 and result.split(' ')[0].isdigit():
                        result = texts[text].get_text().replace('\n', '')
                if len(texts[text].get_text().replace('\n', '').split(' ')[0]) == 6 and texts[text].get_text().replace('\n', '').split(' ')[0].isdigit():
                    if result == '':
                        result = texts[text].get_text().replace('\n', '')
            if len(result.split(' ')[0]) == 4 and result.split(' ')[0].isdigit() :
                return result
            elif len(result.split(' ')[0]) == 6 and result.split(' ')[0].isdigit():
                return 'OTP code incorect! Please try again.'
            else:
                return result   
    if web.get_title() == 'SMS logging - Login page': #relogin website
        web.type('user', tag= 'input', id= 'tbUserName' )
        web.type('passlogin',  tag= 'input', id= 'tbPassword' )
        web.click( tag= 'input', id= 'btnLogin')
        web.click(tag= 'input', id= 'ShowFullMessageCheckBox', text= 'Show full message')
        result = 'Server time out! please try again.'
        return result

#login web SMS
web = Browser(showWindow= True)
web.go_to('''https://secure.cm.nl/smslogging/logging.aspx''')
web.type('user', tag= 'input', id= 'tbUserName' )
web.type('passlogin',  tag= 'input', id= 'tbPassword' )
web.click( tag= 'input', id= 'btnLogin')
web.click(tag= 'input', id= 'ShowFullMessageCheckBox')
#slack connection
client = SlackClient (token= 'your token')
if client.rtm_connect(with_team_state= False):
    print("Connection Successfully ")
    while True: #clean and filter data (phonenumber) from mess of user slack
        duplicate_phonenumber = []
        for mess_from_user in client.rtm_read():#read real_time_meessage
            if len(mess_from_user) > 0 :
                if 'client_msg_id' in mess_from_user.keys():
                    check_phonenumber_customer = mess_from_user['text'].lower()
                    for i in check_phonenumber_customer:
                        if i.isalpha():
                            check_phonenumber_customer = check_phonenumber_customer.replace(i, ' ')
                    print(check_phonenumber_customer)
                    for phonenumber in check_phonenumber_customer.split(' '):
                        if len(phonenumber) >= 11:
                            if phonenumber[phonenumber.find('84'):phonenumber.find('84') + 11].isdigit():
                                phonenumber = phonenumber[phonenumber.find('84'):phonenumber.find('84') + 11]
                                print(phonenumber)
                                if phonenumber not in duplicate_phonenumber: #check duplicache phonenumber 
                                    print(duplicate_phonenumber)
                                    duplicate_phonenumber.append(phonenumber)
                                    text_mess = crawler_data(phonenumber)
                                    respose = client.api_call(                  # call API post message
                                        'chat.postMessage',
                                        channel = '#sms-code',
                                        text = ('%s, %s, <@%s>'%(text_mess ,phonenumber , mess_from_user['user']))
                                        )
                            else:
                                respose = client.api_call(                  # call API post message
                                    'chat.postMessage',
                                    channel = '#sms-code',
                                    text = ('Phonenumber %s incorect!Please try again <@%s>'%( phonenumber , mess_from_user['user']))
                                    )
                                break
                        elif len(phonenumber) == 10:
                            if phonenumber[phonenumber.find('0'):phonenumber.find('0') + 10].isdigit():
                                phonenumber = '84' + phonenumber[phonenumber.find('0') + 1:phonenumber.find('0') + 10]
                                print(phonenumber)
                                if phonenumber not in duplicate_phonenumber: #check duplicache phonenumber
                                    duplicate_phonenumber.append(phonenumber) 
                                    text_mess = crawler_data(phonenumber)
                                    respose = client.api_call(                  # call API post message
                                        'chat.postMessage',
                                        channel = '#sms-code',
                                        text = ('%s, %s, <@%s>'%(text_mess ,phonenumber , mess_from_user['user']))
                                        )
                            else:
                                respose = client.api_call(                  # call API post message
                                    'chat.postMessage',
                                    channel = '#sms-code',
                                    text = ('Phonenumber %s incorect!Please try again <@%s>'%( phonenumber , mess_from_user['user']))
                                    )
                                break
else:
    print('connection failed')
