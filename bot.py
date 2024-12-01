import os
from dotenv import load_dotenv  # Импортируем dotenv для работы с .env файлами
from utils import gpt, util
import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

# import tokens
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GPT_TOKEN = os.getenv("ChatGPT_TOKEN")
chat_gpt = gpt.ChatGptService(GPT_TOKEN)


# states
TALK_GPT, TALK_PEOPLE, QUIZ, IMAGE_DESCRIPTION, SCENE_FIND = range(5)

# functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await util.send_image(update, context, "bot")
    text = "You can:\n/fact - get random fact,\n/quiz - get and answer quiz question,\n/talk - talk with interesting characters,\n/gpt - talk with gpt,\n/image - send image to describe it by AI,\n/scene - ask GPT to find scene from movie, close to your description."
    if update.message:
        await update.message.reply_text(
            f"Hello, {update.effective_user.first_name}.Welcome to the telegram bot! {text}")
    else:
        await util.send_text(update, context, text)


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


async def talk_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update,context, "talk")


async def talk_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "gpt")
    message = await util.send_text(update, context, "Let's talk.")


async def describe_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "eye")
    await util.send_text(update, context, "Please, send picture to get the description")
    return IMAGE_DESCRIPTION


async def find_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await util.send_image(update, context, "film")
    await util.send_text(update, context, "Describe the scene you want to see:")


async def fact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    print(data)
    if "another" in data:
        await give_random_fact(update, context)
    else:
        await start(update, context)


async def image_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler_talk = ConversationHandler(
        entry_points = [CommandHandler("talk", talk_people)],
        states={
            TALK_PEOPLE:[CommandHandler("talk", talk_people)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    conv_handler_gpt = ConversationHandler(
        entry_points = [CommandHandler("gpt", talk_gpt)],
        states={
            TALK_GPT:[CommandHandler("gpt", talk_gpt)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    conv_handler_quiz = ConversationHandler(
        entry_points = [CommandHandler("quiz", give_quiz)],
        states={
            QUIZ:[CommandHandler("quiz", give_quiz)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    conv_handler_image = ConversationHandler(
        entry_points = [CommandHandler("image", describe_image)],
        states={
            IMAGE_DESCRIPTION:[CommandHandler("image", describe_image)],
        },
        fallbacks=[CommandHandler("start", start)],
    )


    conv_handler_scene= ConversationHandler(
        entry_points = [CommandHandler("scene", find_scene)],
        states={
            SCENE_FIND:[CommandHandler("scene", find_scene)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.PHOTO, image_description))

    app.add_handler(CallbackQueryHandler(fact_handler, '^fact_.*'))

    # run app
    app.add_handler(conv_handler_talk)
    app.add_handler(conv_handler_gpt)
    app.add_handler(conv_handler_quiz)
    app.add_handler(conv_handler_image)
    app.add_handler(conv_handler_scene)
    app.run_polling()


# main actions
if __name__ == "__main__":
    main()
