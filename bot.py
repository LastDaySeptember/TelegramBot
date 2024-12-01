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
    await util.send_image(update, context, "bot")
    text = (
        "You can :\n/fact - get random fact,\n/quiz - get and answer quiz question,\n/talk - talk with interesting characters,\n"
        "/gpt - talk with gpt,\n/image - get image description,\n/scene - find scene close to your description.")
    if update.message:
        await update.message.reply_text(
            f"Hello, {update.effective_user.first_name}.Welcome to the telegram bot! {text}")
    else:
        await util.send_text(update, context, text)
    context.user_data["state"] = "base"


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


async def give_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "quiz")
    await util.send_text(update, context, "Let's quiz. I am thinking about the topic.")
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Python", callback_data='quiz_prog'),
            InlineKeyboardButton("Math", callback_data='quiz_math')
        ],
        [
            InlineKeyboardButton("Biology", callback_data='quiz_bio'),
            InlineKeyboardButton("Random", callback_data='quiz_rand')
        ],
        [
            InlineKeyboardButton("More", callback_data='quiz_more')
        ]
    ])
    await context.bot.send_message(update.effective_user.id, " What would you like?", reply_markup=markup)
    context.user_data["state"] = "quiz"


async def talk_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "talk")
    pass


async def talk_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "gpt")
    pass


async def describe_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "eye")
    await util.send_text(update, context, "Send me picture, please")
    context.user_data["state"] = "image"

async def send_image_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE, photo):
    prompt = util.load_prompt("image")
    file_id = photo.file_id
    photo = await context.bot.get_file(file_id)
    # Download the photo to a temporary path
    file_path = "temp/toSend.jpg"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
    await photo.download_to_drive(custom_path=file_path)
    base64_photo = await util.encode_image(file_path)
    message = await util.send_text(update, context, "Sending photo...")
    answer = await chat_gpt.send_image(prompt, base64_photo)
    await message.edit_text(answer)

async def find_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "scene")
    pass

# callback handlers
async def fact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    if "another" in data:
        await give_random_fact(update, context)
    else:
        await start(update, context)

async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    topic = data[5:]


async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[1]
    else:
        await util.send_text(update, context, "Please, check compresssed image")
        return
    if "state" not in context.user_data or context.user_data["state"] != "image":
        await util.send_text(update, context, "To get the description use /image command, please")
        context.user_data["state"] = "base"
        return
    await send_image_gpt(update, context, photo)





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
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, image_handler))


    app.add_handler(CallbackQueryHandler(fact_handler, '^fact_.*'))
    app.add_handler(CallbackQueryHandler(quiz_handler, '^quiz_.*'))

    # run app
    app.run_polling()


# main actions
if __name__ == "__main__":
    main()
