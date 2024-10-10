# todo:
#   - write file with users instances
#   - store tree_original in a google spreadsheet
#   - write prompts into a separate map
#   - add yes/no buttons
# todo:
#   - put on the server
#   - write tests
# imports
import ast
import asyncio
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CallbackQueryHandler, CallbackContext, filters, MessageHandler, Updater

def token_reader():  # reads the file with the telegram bot token
    with open('telegram_bot_token', 'r') as file:
        content = file.read()
        return content

# Bot info
TOKEN: Final = token_reader()
BOT_USERNAME: Final = '@guess_an_animal_game_bot'
# todo: add path
tree_original_russian = 'tree_original_russian'
tree_original_english = 'tree_original_english'

russian_dictionary = {
        'positive_response' : 'да',
        'negative_response' : 'нет',
        'ask_to_think_and_first_question' : 'Загадайте животное. Оно {}?',
        'didnt_understand_you' : 'К сожалению я вас не понял',
        'error_message_to_the_user' : 'Ошибка',
        'feature_question' : 'Оно {}?',
        'animal_question' : 'Это {}?',
        'won_message' : 'Я выиграл! Сыграем ещё раз?',
        'lose_message' : 'Я проиграл. Что это было?',
        'new_feature_question' : 'Какой признак который имеет {} и которого у {} нет? Используйте 1 прилагательное в среднем роде',
        'suggestion_to_play_again' : 'Сыграем ещё раз?',
}

english_dictionary = {
        'positive_response' : 'yes',
        'negative_response' : 'no',
        'ask_to_think_and_first_question' : 'Think about an animal. Is it {}?',
        'didnt_understand_you' : 'I did not understand you',
        'error_message_to_the_user' : 'error',
        'feature_question' : 'Is it {}?',
        'animal_question' : 'Is it a {}?',
        'won_message' : "I Won! Do you want play again?",
        'lose_message' : 'I lost! What is it?',
        'new_feature_question' : 'What is the feature that {} has and {} doesn\'t have? Use 1 adjective',
        'suggestion_to_play_again' : 'Lets play again!'
}

# Stores all classes User. Allows multiple users to play simultaneously
# outside the class use users.create_User(*get id somehow with telegram api*)
class all_Users:
    def __init__(self):
        self.ids = {}

    def create_User(self, id): #creates a class User for each user
        if not id in self.ids:
            self.ids[id] = User()
        return self.ids[id]
users = all_Users() # makes it shorter

# commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE): # starts the bot and allows it to choose language
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data='Language chosen: English'),
            InlineKeyboardButton("Русский", callback_data= 'Выбранный язык: Русский')
        ],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Please, choose the language:\n Пожалуйста, выбирете язык:', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): #about info
    await update.message.reply_text(
        'This is a machine learning based bot that can guess animals\\. For this purpose it'
        ' will ask you questions\\. If the animal you thought about is not in the database'
        ' you can add it there\\.\n'
        '*RULES*\n'
        '1\\. _ONlY THE TRUTH_\\. Do not enter non\\-existent animals with non\\-existent features,'
        ' because all the information goes to the single database and false information '
        'can damage the functionality of the program\\.\n'
        '2\\. _Use ADJECTIVES_ for features\n\n'
        'If you have any problems, questions, or you\'ve noticed any issues in the program you can text \\@l\\_asinus\n'
        'You can find the bot\'s code on github\\.com/l\\-asinus/guesser\n\n'
        'Эта программа основанна на машинном обучении, и она может угадывать животных, для чего будет задавать вопросы\\.'
        'Если вы загадаете животное, которого нет в базе данных, вы можете добавить его туда\n'
        '*Правила*\n'
        '1\\. _ТОЛЬКО ПРАВДА_ не вводите несуществующих животных с несуществующими свойствами, так как это будет засорять'
        'базу данных\n'
        '2\\. _ИСПОЛЬЗУЙТЕ ПРИЛАГАТЕЛЬНЫЕ В СРЕДНЕМ РОДЕ ДЛЯ ХАРАКТЕРИСТИК животных_\n\n'
        'Если у вас есть проблемы или вопросы связанные с игрой, пожалуйста задавайте их по \\@l\\_asinus'
        'Вы можете найти код бота на github\\.com/l\\-asinus/guesser', parse_mode='MarkdownV2')

def file_reader(language): #reads the required file with the tree of assigned language. gets language as an input
    if language == 'russian':
        file = tree_original_russian
    if language == 'english':
        file = tree_original_english
    with open(file, 'r') as file:
        return ast.literal_eval(file.read())



class User: # stores info for each user
    def __init__(self):  # self = variable we are currently working with
        self.state = 1 #state of the game, could ve from 0 to 4. defines the bot's next action
        self.branch = 0 #could be either 1 or 2. one is for user's answer yes, 2 is for the answer no
        self.tree_original = [] # data that is read from the tree_original_language file
        self.language = '' # language, required for work of file_writer
        self.current_dictionary = {}
        

    def file_writer(self, language):  # writes the file if a user adds a new animal into the database
        if language == 'russian':
            file_name = tree_original_russian
        if language == 'english':
            file_name = tree_original_english
        with open(file_name, 'w') as file:
            file.write(str(self.tree_original))

    def replay(self, text): #bot's logic is here
        processed = text.lower()
        if self.state == 0: #first question
            self.state = 1
            return self.current_dictionary['ask_to_think_and_first_question'].format(self.tree[0])
        if self.state == 1: #repeating question. navigates in the tree until the final brunch
            if self.current_dictionary['positive_response'].lower() in processed:
                self.branch = 1
            elif self.current_dictionary['negative_response'].lower() in processed:
                self.branch = 2
            else:
                return self.current_dictionary['didnt_understand_you']
            if isinstance(self.tree[self.branch], list): #returns to the beginning of the state 1
                self.tree = self.tree[self.branch]
                self.state = 1
                return self.current_dictionary['feature_question'].format(self.tree[0])
            elif isinstance(self.tree[self.branch], str):
                self.state = 2 #changes state to 2
                return self.current_dictionary['animal_question'].format(self.tree[self.branch])
            else:
                print('error')
                return self.current_dictionary['error_message_to_the_user']

        elif self.state == 2: #asks if the guess is correct
            if self.current_dictionary['positive_response'].lower()in processed:
                self.state = 0 #if it guesses the animal correctly it restarts the game
                self.tree = self.tree_original
                return self.current_dictionary['won_message']
            elif self.current_dictionary['negative_response'].lower() in processed:
                self.state = 3 #if the guess is wrong, it changes state to 3
                return self.current_dictionary['lose_message']
            else:
                return self.current_dictionary['error_message_to_the_user']

        elif self.state == 3: # gets info about the new animals' new feature
            self.new_animal = processed
            self.old_animal = self.tree[self.branch]
            self.state = 4
            return self.current_dictionary['new_feature_question'].format(self.new_animal, self.old_animal)

        elif self.state == 4: #writes new info into the tree_original_language and restarts the game
            old_animal = self.tree[self.branch]
            self.tree[self.branch] = [processed, self.new_animal, old_animal]
            self.file_writer(self.language)
            self.state = 0
            self.tree = self.tree_original
            return self.current_dictionary['suggestion_to_play_again']
        else: # error handling
            print ('state out of range')
            return 'state out of range'

# button handler
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE): #handles the response to the language choice buttons from start_command and writes the about message
    query = update.callback_query #shortening
    id = query.from_user.id #shortening
    await query.answer() #waits until it gets the answer
    await query.edit_message_text(text=f"{query.data}") # edits message depending on the language choice
    print (query.data)
    if query.data == 'Выбранный язык: Русский':
        users.create_User(id).language = 'russian'
        users.create_User(id).current_dictionary = russian_dictionary
        users.create_User(id).tree_original = file_reader(users.create_User(id).language) #reads the tree_original_language file depending on the language choice
        users.create_User(id).tree = users.create_User(id).tree_original #creates a User class inside all_Users
        await context.bot.send_message(chat_id=query.message.chat_id, #russian about message
                                       text='Эта программа основанна на машинном обучении, и она может угадывать'
                                            'животных, для чего будет задавать вопросы\\.'
                                            'Если вы загадаете животное, которого нет в базе данных,'
                                            'вы можете добавить его туда\n'
                                            '*Правила*\n'
                                            '1\\. _ТОЛЬКО ПРАВДА_\\. не вводите несуществующих животных с несуществующими'
                                            ' свойствами, так как это будет засорять'
                                            'базу данных и может испортить работу программы\\.\n'
                                            '2\\. _ИСПОЛЬЗУЙТЕ ТОЛЬКО ОДНО СЛОВО ДЛЯ ХАРАКТЕРИСТИК_ животных\n\n'
                                            'Если у вас есть проблемы или вопросы связанные с игрой, пожалуйста'
                                            ' задавайте их по \\@l\\_asinus '
                                            'Вы можете найти код бота на github\\.com/l\\-asinus/guesser\n\n'
                                            'Тогда начнём игру\\. Загадайте животное\\.\nУ него есть шерсть?', parse_mode='MarkdownV2')
    elif query.data == 'Language chosen: English':
        users.create_User(id).language = 'english'
        users.create_User(id).current_dictionary = english_dictionary
        users.create_User(id).tree_original = file_reader(users.create_User(id).language)
        users.create_User(id).tree = users.create_User(id).tree_original
        await context.bot.send_message(chat_id=query.message.chat_id, # english about message
                                       text= 'This is a machine learning based bot that can guess animals\\. For this purpose it'
        ' will ask you questions\\. If the animal you thought about is not in the database,'
        ' you can add it there\\.\n'
        '*RULES*\n'
        '1\\. _ONlY THE TRUTH_\\. Do not enter non\\-existent animals with non\\-existent features,'
        ' because all the information goes to the single database, and false information '
        'can damage the functionality of the program\n'
        '2\\._Use ONLY ONE WORD_ for features\n\n'
        'If you have any problems, questions, or you\'ve noticed any issues in the program you can text \\@l\\_asinus\n'
                                             'You can find the bot\'s code on github\\.com/l\\-asinus/guesser\n\n'
        'Let\'s begin the game then\\. Think about an animal\\.'
        '\nIs it furry?', parse_mode='MarkdownV2')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): #writes the content of bot and user messaging in the terminal
    message_type = update.message.chat.type
    text: str = update.message.text  # input
    id = update.message.chat.id
    print(f'User ({id}) in {message_type}: "{text}"')
    response = users.create_User(id).replay(text)
    print(f'Bot {id}', response)
    await update.message.reply_text(response)

# error
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update{update} caused error {context.error}')

# main function
if __name__ == '__main__':
    print('Bot started')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    #app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_handler(CallbackQueryHandler(choose_language))

    app.add_error_handler(error)

    app.run_polling(poll_interval=1)  # cycle