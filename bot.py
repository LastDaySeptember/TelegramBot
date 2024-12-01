import os
from dotenv import load_dotenv  # Импортируем dotenv для работы с .env файлами
from utils import gpt, util
import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# import tokens
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GPT_TOKEN = os.getenv("ChatGPT_TOKEN")
chat_gpt = gpt.ChatGptService(GPT_TOKEN)

# functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # text = update.message.text
    await util.send_image(update, context, "bot")
    await update.message.reply_text(
        f"Hello, {update.effective_user.first_name}. \n Welcome to the telegram bot, where you can:\n"
        f"/fact - get random fact,\n"
        f"/quiz - get and answer quiz question,\n"
        f"/talk - talk with interesting characters,\n"
        f"/gpt - talk with gpt,\n"
        f"/image - send image to describe it by AI,\n"
        f"/scene - ask GPT to find scene from movie, close to your description.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    await update.message.reply_text(
        f"You have written '{text}' at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


async def give_random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "random")
    message = await util.send_text(update, context, "Thinking...")
    prompt = util.load_prompt("random")
    answer = await chat_gpt.send_question(prompt, '')
    await message.edit_text(answer)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Another fact", callback_data="fact_another")],
        [InlineKeyboardButton("Finish", callback_data="fact_finish")]
        ]
    )
    await context.bot.send_message(update.effective_user.id, 'Do you want another one?', reply_markup=markup)



async def give_quiz():
    pass


async def talk_people():
    pass


async def talk_gpt():
    pass


async def describe_image():
    pass


async def find_scene():
    pass


async def fact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    print(data)
    if "another" in data:
        await give_random_fact(update, context)
    else:
        await start(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fact", give_random_fact))
    app.add_handler(CommandHandler("quiz", give_quiz))
    app.add_handler(CommandHandler("talk", talk_people))
    app.add_handler(CommandHandler("gpt", talk_gpt))
    app.add_handler(CommandHandler("image", describe_image))
    app.add_handler(CommandHandler("scene", find_scene))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.add_handler(CallbackQueryHandler(fact_handler, '^fact_.*'))

    # run app
    app.run_polling()


# main actions
if __name__ == "__main__":
    main()
