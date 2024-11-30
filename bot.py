import os
from dotenv import load_dotenv  # Импортируем dotenv для работы с .env файлами
from utils import gpt, util
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# import tokens
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GPT_TOKEN = os.getenv("ChatGPT_TOKEN")


# functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    await update.message.reply_text(f"Hello, {update.effective_user.first_name}. Welcome to the telegram bot, where you have few useful functions.")




# main actions
app = ApplicationBuilder().token(BOT_TOKEN).build()





app.add_handler(CommandHandler("start", start))

# run app
app.run_polling()


