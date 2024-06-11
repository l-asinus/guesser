#imports
import ast
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

#Bot info
TOKEN: Final = ''
BOT_USERNAME: Final = '@guess_an_animal_game_bot'


#message replay: bot's logic is here
class User_ids:
    def __init__(self):
        self.ids = {}
    def get(self, id):
        if not id in self.ids:
            self.ids[id] = State()
        return self.ids[id]
user_ids = User_ids()

def file_writer():
    with open('tree_original.txt', 'w') as file:
        file.write(repr(tree_original))


def file_reader():
    with open('tree_original.txt', 'r') as file:
        tree = file.read()
        return ast.literal_eval(tree)


tree_original = file_reader()

class State:
    def __init__(self):  # self = variable we are currently working with
        global tree_original
        self.tree = tree_original
        self.state = 1
        self.new_animal = ''
        self.branch = 0

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



#commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, welcome to the Guesser game! I can guess an animal that you think about '
                                    'if you answer my questions.\n'
                                    f'Think about an animal. Is it {tree_original[0]}?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a machine learning based bot that can guess animals. For this purpose it'
                                    ' will ask you questions. If the animal you thought about is not in the database,'
                                    ' you can add it there.\n'
                                    'RULES\n'
                                    '1. ONlY THE TRUTH. Don`t enter non-existent animals with non-existent features,'
                                    ' because all the information goes to the single database, and false information '
                                    'can damage the program`s functionality\n'
                                    '2. Use ONLY ONE WORD for features')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text       #input
    id = update.message.chat.id
    print(f'User ({id}) in {message_type}: "{text}"')
    response = user_ids.get(id).replay(text)
    print(f'Bot {id}', response)

    await update.message.reply_text(response)


#error
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update{update} caused error {context.error}')


#main function
if __name__ == '__main__':
    print('Bot started')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))


    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    app.run_polling(poll_interval=1)   #cycle
