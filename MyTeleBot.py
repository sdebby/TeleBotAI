# Telegram Bot
# 18.03.2023
# installing repository pip install pyTelegramBotAPI
# https://github.com/eternnoir/pyTelegramBotAPI
# openAI
# https://platform.openai.com/docs/libraries

import random
import string
import telebot
from telebot import custom_filters
from telebot import formatting
import requests
import openai
import json
import logging, os, ast
from time import gmtime, strftime
from teleHelper import FileHelper

file_path = os.path.dirname(os.path.realpath(__file__))
MsglogFile=file_path+'/chat.log'
ConfFile=file_path+'/telebot2.conf'
UserData=FileHelper.ReadConfigFile(ConfFile) #get configuration from file
if len(UserData)==0:
    logging.error('No data conf in file '+ConfFile)
    quit()
AllowUser=list(map(int,UserData['AllowUser'].split(',')))
# ** openAI
openai.api_key = UserData['OpenAI_api_key']
max_tok=200
temp=0.7
ChatModel="gpt-3.5-turbo"
isize=["1024x1024" , "512x512" , "256x256"]
# **
Passlength=16
NoOfEnhenText=2 # number of enhenc words
Enhancements=['donato giancola','peter mohrbacher','tomasz alen kopera','4K','8K','Avalanche background','digital painting','artstation','concept art','illustration','art by Greg Rutkowski','high quality','highly detailed','high coherence','anatomically correct','digital art','sharp focus','elegant','octane render','concept art','illustration','intricate, elegant','highly detailed','boris vallejo','leyendecker','wlop','centered','digital painting','artgerm']
logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(token=UserData['TelegramToken'], parse_mode=None) 
print (bot.get_me) # test bot token.
message_log=[] # this is ChatGPT message log

# set menu
bot.delete_my_commands(scope=None, language_code=None) # delete previus commands
bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("help", "display help message"),
        telebot.types.BotCommand("getpass", "display a random 16 charecters password"),
        telebot.types.BotCommand("ip", "display local machine ip"),
        telebot.types.BotCommand("chatgpt", "get ChatGPT respond "),
        telebot.types.BotCommand("dalle", "get Dall-E 2 respond ")
    ],
)

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.send_message(message.chat.id, """
    ** Debby Telegram Bot - see commands **
    /getpass - display a random 16 charecters password
    /ip - display local machine ip
    /chatgpt [prompt] get ChatGPT respond 
    /dalle [prompt] get Dall-E2 respond

    USER ID= """+str(message.from_user.id))

@bot.message_handler(chat_id=AllowUser, commands=['getpass']) #sends a random password
def send_welcome(message):
    randomstr = ''.join(random.sample(string.ascii_letters+string.digits,Passlength))
    bot.send_message(message.chat.id,randomstr)

@bot.message_handler(chat_id=AllowUser,commands=['ip']) #get local computer public IP
def send_welcome(message):
    try:
        ip = requests.get('https://api.ipify.org').text
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id,text='The public IP address is: {}'.format(ip))
    except:
        bot.send_message(message.chat.id,'Error getting IP')
    
@bot.message_handler(chat_id=AllowUser,commands=['dalle']) #get Dall-E response
def send_welcome(message):
    userText=message.text[7:]
    EnhanTextLts=[]
    if userText=="":
       bot.send_message(message.chat.id,"No prompt entered \nUse:\n"+
            formatting.mcode('/dalle [prompt]'),parse_mode='MarkdownV2')  
    else:
        bot.send_message(message.chat.id, "Getting image ready")
        bot.send_chat_action(message.chat.id, 'upload_photo')
        for x in range(NoOfEnhenText):
            EnhanTextLts.append(random.choice(Enhancements))
        EnhanText=' ,'.join(EnhanTextLts)
        response = openai.Image.create(prompt=userText+' ,'+EnhanText,n=1,size=isize[2],response_format="url")
        ans=json.loads (str(response))
        MyResult=(ans['data'][0]['url'])
        # saving image
        img_data = requests.get(MyResult).content
        img_name=userText.replace(" ","_")+".jpg"
        try:
            with open(img_name, 'wb') as handler:
                handler.write(img_data)
            photo = open(img_name, 'rb')
            bot.send_photo(message.chat.id, photo,caption=userText)
        except:
            logging.error('Error loading/saving image')
            bot.send_message(message.chat.id,"Error loading/saving image")               

@bot.message_handler(chat_id=AllowUser,commands=['chatgpt']) #get chatGPT response
def send_welcome(message):
    userText=message.text[8:]
    if userText=="":
       bot.send_message(message.chat.id,"No prompt entered \nUse:\n"+
                        formatting.mcode('/chatgpt [prompt]'),parse_mode='MarkdownV2') 
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            message_log.append({"role": "user", "content": userText})
            FileHelper.WriteToFile(MsglogFile,str({"role": "user", "content": userText}))
            response = openai.ChatCompletion.create(
                model=ChatModel,
                temperature=temp,
                max_tokens=max_tok,
                messages=message_log)
            MyResult=response.choices[0].message.content
            message_log.append({"role": "assistant", "content":MyResult})
            FileHelper.WriteToFile(MsglogFile,str({"role": "assistant", "content":MyResult}))
            # print(message_log)
        except openai.error.OpenAIError as e:
            logging.error('Error connecting to OpenAI server')
            MyResult='Error connecting to OpenAI server'
        bot.send_message(message.chat.id,text=MyResult)

@bot.message_handler(chat_id=AllowUser) # Handling all aouther messages
def send_welcome(message):
    bot.send_message(message.chat.id, "Type /help to view commands")

@bot.message_handler() # Handling user ID with no permission
def send_welcome(message):
    bot.send_message(message.chat.id, "User have no permission, this event will be writen in the logs")
    ThisTime=strftime("%Y-%m-%d %H:%M:%S", gmtime())
    logging.warning('User have no permission')
    FileHelper.WriteToFile(file_path+'/log.txt',ThisTime+' User '+str(message.from_user.id)+' try to use system')

def main(): 
    global message_log
    bot.add_custom_filter(custom_filters.ChatFilter())
    if os.path.isfile(MsglogFile): # check if file exsist
        # split to list and convert to dict
        tmpLst=FileHelper.ReadFile(MsglogFile).split('\n')
        for ln in tmpLst:
            if not ln =='':
                message_log.append(ast.literal_eval(ln))
        logging.info('reading from chat message log file')
    else:
        msg={"role": "system", "content": "You are a helpful assistant."}
        message_log.append(msg)
        FileHelper.WriteToFile(MsglogFile,str(msg))
        logging.info('chat log is empty')
    
    bot.infinity_polling()

if __name__ == '__main__':
    main()
