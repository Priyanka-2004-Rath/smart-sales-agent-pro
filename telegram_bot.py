import os
# from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import streamlit as st
BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]


# Import mood detection and reply generation
from enhanced_mood_detector import MoodDetector, ReplyGenerator

# Initialize AI components
mood_detector = MoodDetector()
reply_generator = ReplyGenerator()

# Conversation history per user (chat_id)
user_histories = {}
MAX_HISTORY = 5  # Max messages per user

# Handle /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Hello! I'm Smart Sales Agent Pro.\nAsk me anything about your sales issue, lead, or product!")

# Handle all text messages
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()

    if chat_id not in user_histories:
        user_histories[chat_id] = []

    user_histories[chat_id].append(user_text)
    user_histories[chat_id] = user_histories[chat_id][-MAX_HISTORY:]
    conversation_context = "\n".join(user_histories[chat_id])

    # Mood detection
    mood_result = mood_detector.detect_mood(user_text)
    mood = mood_result["mood"]
    label = mood_result["label"]
    intensity = mood_detector.analyze_sentiment_intensity(user_text)
    category = mood_detector.get_mood_category(label)

    # Generate reply
    smart_reply = reply_generator.generate_reply(user_text, category, intensity)

    final_message = (
        f"🤖 Mood: {mood} (Intensity: {intensity})\n"
        f"💬 {smart_reply}"
    )
    await update.message.reply_text(final_message)

# Start the bot
def start_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("✅ Telegram bot is running...")
    app.run_polling()
