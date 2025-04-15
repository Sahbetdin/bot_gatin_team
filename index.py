import os
from datetime import datetime
from telegram import InputFile
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    ContextTypes,
    filters
)
from sqlite_class import SQLiteDB


class InitiativeBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        self.res_file = "ideas_collected_"
        self.s = SQLiteDB(db_name = 'ideas_users.db')
        self._setup_handlers()

    def _setup_handlers(self):
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("reset", self.reset))

        # Message handler for initiatives
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_initiative
        ))

        # Callback query handler for inline keyboard
        self.application.add_handler(CallbackQueryHandler(self.handle_inline_buttons))


    async def handle_initiative(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the user's initiative and ask if they want to save their name."""
        if context.user_data.get('state') == 'waiting_for_initiative':
            # Store the initiative
            context.user_data['initiative'] = update.message.text
            # Create inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton("Да", callback_data="save_name_yes"),
                    InlineKeyboardButton("Нет", callback_data="save_name_no"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
			
            # Ask if user wants to save name
            await update.message.reply_text(
                "Желаете ли Вы, чтобы я сохранил Ваше имя пользователя для последующего обращения?",
                reply_markup=reply_markup
            )
        elif context.user_data.get('state') == 'waiting_for_name':
            await update.message.reply_text("Ваша идея записана.")
            self.save_results_db(update.effective_user.id, 
                            update.effective_user.full_name,     
                            context.user_data['initiative'],
                            user_name=update.message.text, to_record=1)
            context.user_data['state'] = 'finished'
   

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        # 329200678 real
        if update.effective_user.id in (329200678,):
            self.res_file_ = f"{self.res_file}{datetime.now().strftime("%Y%m%d_%H_%M")}.csv"
            # print(self.res_file_)
            self.s.select_to_csv(table_name1='users', table_name2='ideas',
              filename=self.res_file_)
            with open(self.res_file_, 'rb') as file:
                await update.message.reply_document(
                    document=InputFile(file), caption="Александр Айдарович,\n все собранные идеи здесь")
                context.user_data['state'] = 'finished'
        else:
            await update.message.reply_text("Отправьте Вашу инциативу.")
            context.user_data['state'] = 'waiting_for_initiative'


    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /reset is issued."""
        await update.message.reply_text("Пожалуйста нажмите кнопку /start.")
        context.user_data['state'] = None


    async def handle_inline_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the inline keyboard buttons."""
        query = update.callback_query
        # await query.answer()
        await query.edit_message_reply_markup(reply_markup=None)
        
        if query.data == "save_name_yes":
            await query.edit_message_text(text="Пожалуйста напишите, как к Вам можно обращаться.")
            context.user_data['state'] = 'waiting_for_name'
        elif query.data == "save_name_no":
            await query.edit_message_text(text="Хорошо. Ваша идея записана.")
            self.save_results_db(update.effective_user.id, 
                            update.effective_user.full_name,
                            context.user_data['initiative'],
                            user_name=None, to_record=0)
            context.user_data['state'] = 'finished'

    def save_results_db(self, user_tg_id: str, 
                        user_tg_name: str,
                        idea: str, user_name: str, to_record: int) -> None:
        self.s.insert_data("ideas",
                      {"user_tg_id": user_tg_id,
                       "idea": idea,
                    #    "created_at_i": datetime.now()
                       })
        self.s.insert_data("users", 
                      {"user_tg_id": user_tg_id,
                       "tg_name": user_tg_name,
                       "name": user_name,
                            "is_agree_to_save_name": to_record, 
                            # "created_at": datetime.now()
                            })
        self.s.close()

    def run(self):
        self.application.run_polling()


if __name__ == "__main__":
    TOKEN = "8171611036:AAF4KJvqxTRf4fnlBVNctfSM_fG8_8g37mw"
    bot = InitiativeBot(token=TOKEN)
    bot.run()