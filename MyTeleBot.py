# Telegram Bot
# installing repository pip install pyTelegramBotAPI
# https://github.com/eternnoir/pyTelegramBotAPI

# openAI
# https://platform.openai.com/docs/libraries

import random
import string
import telebot
import requests
import openai
import json

TelegramToken=<TELEGRAM TOKEN>
# ** openAI
openai.api_key = <OPENAI SECRET API KEY>
max_tok=50
temp=0.7
isize=["1024x1024" , "512x512" , "256x256"]
# **
Passlength=16

bot = telebot.TeleBot(TelegramToken, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

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

print (bot.get_me) # test bot token.

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, """
    ** Debby Telegram Bot - see commands **
    /getpass - display a random 16 charecters password
    /ip - display local machine ip
    /chatgpt [prompt] get ChatGPT respond 
    /dalle [prompt] get Dall-E2 respond
    """)

@bot.message_handler(commands=['getpass']) #sends a random password
def send_welcome(message):
    chat_id = message.chat.id
    randomstr = ''.join(random.sample(string.ascii_letters+string.digits,Passlength))
    bot.send_message(chat_id,randomstr)

@bot.message_handler(commands=['ip']) #get local computer public IP
def send_welcome(message):
    length=16
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    ip = requests.get('https://api.ipify.org').text
    bot.send_message(chat_id,text='The public IP address is: {}'.format(ip))

@bot.message_handler(commands=['dalle']) #get Dall-E response
def send_welcome(message):
    chat_id = message.chat.id
    userText=message.text[7:]
    if userText=="":
       bot.send_message(chat_id,"No prompt entered \nUse:\n/dalle [prompt]") 
    else:
        bot.reply_to(message, "Getting image ready")
        bot.send_chat_action(chat_id, 'upload_photo')
        response = openai.Image.create(prompt=userText,n=1,size=isize[2],response_format="url")
        ans=json.loads (str(response))
        MyResult=(ans['data'][0]['url'])
        # saving image
        img_data = requests.get(MyResult).content
        img_name=userText.replace(" ","_")+".jpg"
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
        # sending photo to chat
        photo = open(img_name, 'rb')
        bot.send_photo(chat_id, photo)

@bot.message_handler(commands=['chatgpt']) #get chatGPT response
def send_welcome(message):
    chat_id = message.chat.id
    userText=message.text[8:]
    if userText=="":
       bot.send_message(chat_id,"No prompt entered \nUse:\n/chatgpt [prompt]") 
    else:
        bot.reply_to(message, "Getting text ready")
        bot.send_chat_action(chat_id, 'typing')
        response = openai.Completion.create(model="text-davinci-003", prompt=userText, temperature=temp, max_tokens=max_tok)
        ans=json.loads (str(response))
        MyResult=(ans['choices'][0]['text'])
        bot.send_message(chat_id,text=MyResult)

bot.infinity_polling()
