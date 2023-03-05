# Telegram Bot
# 02.02.2023
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

TelegramToken=<TELEGRAM TOKEN>
AllowUser=[123456]
# ** openAI
openai.api_key = <OPENAI SECRET API KEY>
max_tok=200
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
    if userText=="":
       bot.send_message(message.chat.id,"No prompt entered \nUse:\n"+
            formatting.mcode('/dalle [prompt]'),parse_mode='MarkdownV2')  
    else:
        bot.send_message(message.chat.id, "Getting image ready")
        bot.send_chat_action(message.chat.id, 'upload_photo')
        response = openai.Image.create(prompt=userText,n=1,size=isize[2],response_format="url")
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
            print('Error loading/saving image')
            bot.send_message(message.chat.id,"Error loading/saving image")               

@bot.message_handler(chat_id=AllowUser,commands=['chatgpt']) #get chatGPT response
def send_welcome(message):
    userText=message.text[8:]
    if userText=="":
       bot.send_message(message.chat.id,"No prompt entered \nUse:\n"+
                        formatting.mcode('/chatgpt [prompt]'),parse_mode='MarkdownV2') 
    else:
        bot.send_message(message.chat.id, "Getting text ready")
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            response = openai.Completion.create(model="text-davinci-003", prompt=userText, temperature=temp, max_tokens=max_tok)
            ans=json.loads (str(response))
            MyResult=(ans['choices'][0]['text'])
        except openai.error.OpenAIError as e:
            print(e.http_status)
            print(e.error)
            MyResult='Error connecting to OpenAI server'
        bot.send_message(message.chat.id,text=MyResult)

@bot.message_handler(chat_id=AllowUser) # Handling all aouther messages
def send_welcome(message):
    bot.send_message(message.chat.id, "Type /help to view commands")

@bot.message_handler() # Handling user ID with no permission
def send_welcome(message):
    bot.send_message(message.chat.id, "User have no permission !")

def main():    
    bot.add_custom_filter(custom_filters.ChatFilter())
    bot.infinity_polling()

if __name__ == '__main__':
    main()
