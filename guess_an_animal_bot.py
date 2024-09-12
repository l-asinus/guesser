# todo:
#   - write file with user_ids instances
#   - put on the server
#   - comment everything and github
#   - store tree_original in a google spreadsheet
#   - use inline keyboard for language choice!
#   - write prompts into a separate map
#   - start command into a state

# imports
import ast
import asyncio
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CallbackQueryHandler, CallbackContext

def token_reader():  # reads the file with the telegram bot token
    with open('telegram_bot_token', 'r') as file:
        content = file.read()
        return content

# Bot info
TOKEN: Final = token_reader()
BOT_USERNAME: Final = '@guess_an_animal_game_bot'

class User_ids:
    def __init__(self):
        self.ids = {}

    def get(self, id):
        if not id in self.ids:
            self.ids[id] = State()
        return self.ids[id]

# commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data='Language chosen: English'),
            InlineKeyboardButton("Русский", callback_data= 'Выбранный язык: Русский')
        ],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please, choose the language:\n Пожалуйста, выбирете язык:', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'This is a machine learning based bot that can guess animals. For this purpose it'
        ' will ask you questions. If the animal you thought about is not in the database,'
        ' you can add it there.\n'
        '*RULES*\n'
        '1. _ONlY THE TRUTH_. Do not enter non-existent animals with non-existent features,'
        ' because all the information goes to the single database, and false information '
        'can damage the functionality of the program\n'
        '2. _Use ONLY ONE WORD_ for features', parse_mode='Markdown')

user_ids = User_ids()

def file_writer():
    if user_ids.get(id).language == 'russian':
        file = tree_original_russian
    elif user_ids.get(id).language == 'english':
        file = tree_original_english
    with open(file, 'w') as file:
        file.write(repr(file))


def file_reader(language):
    if language == 'russian': file = 'tree_original_russian'
    if language == 'english': file = 'tree_original_english'
    with open(file, 'r') as file:
        tree = file.read()
        return ast.literal_eval(tree)

tree_original_russian = file_reader('russian')
tree_original_english = file_reader('english')

# message replay: bot's logic is here
class State:
    def __init__(self):  # self = variable we are currently working with
        global tree_original_russian, tree_original_english
        #self.tree = tree_original
        self.state = 1
        self.new_animal = ''
        self.branch = 0
        self.language = ('')

    def replay(self, text):
        processed = text.lower()
        if self.state == 0:
            self.state = 1
            return f'Think about an animal. Is it {self.tree[0]}?'
        if self.state == 1:
            if 'yes' in processed:
                self.branch = 1
            elif 'no' in processed:
                self.branch = 2
            else:
                return 'I haven`t understand you'
            if isinstance(self.tree[self.branch], list):
                self.tree = self.tree[self.branch]
                self.state = 1
                return f'Is it {self.tree[0]}?'
            elif isinstance(self.tree[self.branch], str):
                self.state = 2
                return f'Is it a {self.tree[self.branch]}?'
            else:
                print('error')
                return 'ERROR'

        elif self.state == 2:
            if 'yes' in processed:
                self.state = 0
                self.tree = tree_original
                return "I Won! Do you want play again?"
            elif 'no' in processed:
                self.state = 3
                return 'I lost! What is it?'
            else:
                return 'ERROR'

        elif self.state == 3:
            self.new_animal = processed
            old_animal = self.tree[self.branch]
            self.state = 4
            return f'What is the feature that {self.new_animal} has and {old_animal} doesn`t have?'

        elif self.state == 4:
            old_animal = self.tree[self.branch]
            self.tree[self.branch] = [processed, self.new_animal, old_animal]
            file_writer()
            self.state = 0
            self.tree = tree_original
            return 'Lets play again!'
        else:
            return 'state out of range'


# button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"{query.data}")
    print (query.data)
    if query.data == 'Выбранный язык: Русский':
        user_ids.get(id).tree = tree_original_russian
        await context.bot.send_message(chat_id=query.message.chat_id, text='Тогда начнём игру. Загадайте животное.\nУ него есть шерсть?')
    elif query.data == 'Language chosen: English':
        await context.bot.send_message(chat_id=query.message.chat_id, text='Let`s begin the game then. Think about an animal.\nIs it furry?')
        user_ids.get(id).tree = tree_original_english

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text  # input
    id = update.message.chat.id
    print(f'User ({id}) in {message_type}: "{text}"')
    response = user_ids.get(id).replay(text)
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

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_handler(CallbackQueryHandler(button))

    app.add_error_handler(error)

    app.run_polling(poll_interval=1)  # cycle