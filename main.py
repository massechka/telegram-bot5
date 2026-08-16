import telebot
import os
import time
import json
import traceback
import threading
import requests
from datetime import datetime, timezone, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

print("🚀 ЗАПУСК БОТА FLUXSHOP...")

# ============================================================
# ТВОИ ДАННЫЕ
# ============================================================
BOT_TOKEN = "8917418368:AAFzB9LzRbNnYUF8YCK7ILKoGhWWnBLvXs4"
CHANNEL_ID = "-1004393648334"
SELLER_ID = "7389526173"
SUPPORT_ID = "8140113992"
WEBAPP_URL = "https://keen-pika-acbb17.netlify.app"
RULES_URL = "https://fluxsshops.netlify.app"
# ============================================================

print(f"✅ Токен: {BOT_TOKEN[:10]}... (скрыто)")
print(f"✅ CHANNEL_ID: {CHANNEL_ID}")
print(f"✅ SELLER_ID: {SELLER_ID}")
print(f"✅ SUPPORT_ID: {SUPPORT_ID}")

# ============================================================
# 1. ЗАПУСКАЕМ FLASK В ГЛАВНОМ ПОТОКЕ (Render сразу видит порт)
# ============================================================
from flask import Flask
import threading

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "✅ Бот работает", 200

@flask_app.route('/health')
def health():
    return "OK", 200

# ЗАПУСКАЕМ БОТА В ОТДЕЛЬНОМ ПОТОКЕ
def run_bot():
    # ============================================================
    # 2. БОТ
    # ============================================================
    bot = telebot.TeleBot(BOT_TOKEN)
    print("🤖 Бот создан")

    try:
        bot.remove_webhook()
        print("✅ Webhook удалён")
    except Exception as e:
        print(f"⚠️ {e}")

    try:
        requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook')
        print("✅ API-сброс webhook выполнен")
    except:
        pass

    # ============================================================
    # 3. ФУНКЦИИ
    # ============================================================
    def get_msk_time():
        msk = timezone(timedelta(hours=3))
        now = datetime.now(msk)
        return now.strftime("%d.%m.%Y %H:%M:%S")

    def is_subscribed(user_id):
        try:
            member = bot.get_chat_member(CHANNEL_ID, user_id)
            return member.status in ['creator', 'administrator', 'member']
        except Exception as e:
            print(f"⚠️ Ошибка проверки: {e}")
            return False

    # ============================================================
    # 4. КНОПКИ
    # ============================================================
    def get_subscribe_button():
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/fluxsshop"))
        return kb

    def get_check_button():
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub"))
        return kb

    def get_webapp_button():
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        kb.add(KeyboardButton("🛒 Магазин", web_app=WebAppInfo(WEBAPP_URL)))
        return kb

    def get_main_menu():
        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        kb.add(
            KeyboardButton("🛒 Магазин", web_app=WebAppInfo(WEBAPP_URL)),
            KeyboardButton("📞 Связь с продавцом"),
            KeyboardButton("🆘 Поддержка")
        )
        return kb

    def get_buy_button():
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Оплатить Stars", url="https://t.me/iadza"))
        return kb

    def get_support_button():
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🆘 Написать в поддержку", url="https://t.me/rfrpq"))
        return kb

    # ============================================================
    # 5. ОБРАБОТЧИКИ
    # ============================================================
    @bot.message_handler(commands=['start'])
    def start_command(message):
        try:
            user_id = message.from_user.id
            if is_subscribed(user_id):
                bot.send_message(
                    user_id,
                    "👋 Здравствуйте, здесь вы можете приобрести телеграмм аккаунты.\n\n"
                    "Наш тгк: @fluxsshop\n"
                    "Наши отзывы: @fluxs_reviews\n"
                    f"Наши правила: {RULES_URL}",
                    reply_markup=get_main_menu()
                )
            else:
                bot.send_message(
                    user_id,
                    "❌ Для доступа подпишитесь на канал:",
                    reply_markup=get_subscribe_button()
                )
                bot.send_message(
                    user_id,
                    "После подписки нажмите кнопку ниже:",
                    reply_markup=get_check_button()
                )
        except Exception as e:
            print(f"❌ start: {e}\n{traceback.format_exc()}")

    @bot.message_handler(func=lambda m: True)
    def all_messages(message):
        try:
            user_id = message.from_user.id
            if not is_subscribed(user_id):
                bot.send_message(user_id, "❌ Подпишитесь на канал.", reply_markup=get_subscribe_button())
                return

            text = message.text
            if text == "🛒 Магазин":
                bot.send_message(user_id, "🛒 Выберите товар:", reply_markup=get_webapp_button())
            elif text == "📞 Связь с продавцом":
                bot.send_message(
                    user_id,
                    f"📞 Продавец: @iadza\n🆔 {SELLER_ID}\n\n💎 Оплата Stars на @iadza",
                    reply_markup=get_buy_button()
                )
            elif text == "🆘 Поддержка":
                bot.send_message(
                    user_id,
                    f"🆘 Поддержка: @rfrpq\n🆔 {SUPPORT_ID}\n\n📅 ПН-ПТ: 14:00-22:00\n📅 СБ-ВС: 16:00-22:00",
                    reply_markup=get_support_button()
                )
            else:
                bot.send_message(
                    user_id,
                    "👋 Здравствуйте, здесь вы можете приобрести телеграмм аккаунты.\n\n"
                    "Наш тгк: @fluxsshop\n"
                    "Наши отзывы: @fluxs_reviews\n"
                    f"Наши правила: {RULES_URL}",
                    reply_markup=get_main_menu()
                )
        except Exception as e:
            print(f"❌ all: {e}\n{traceback.format_exc()}")

    @bot.callback_query_handler(func=lambda call: call.data == "check_sub")
    def check_subscription(call):
        try:
            user_id = call.from_user.id
            if is_subscribed(user_id):
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="✅ Подписка подтверждена!",
                    reply_markup=None
                )
                bot.send_message(user_id, "👋 Добро пожаловать!", reply_markup=get_main_menu())
            else:
                bot.answer_callback_query(call.id, "❌ Вы не подписались!", show_alert=True)
        except Exception as e:
            print(f"❌ check: {e}\n{traceback.format_exc()}")

    @bot.message_handler(content_types=['web_app_data'])
    def handle_webapp_data(message):
        try:
            user_id = message.from_user.id
            if not is_subscribed(user_id):
                bot.send_message(user_id, "❌ Подпишитесь на канал.", reply_markup=get_subscribe_button())
                return

            data = json.loads(message.web_app_data.data)
            if data.get('action') == 'order':
                product = data.get('product', 'Неизвестно')
                price = data.get('price', '0')
                username = message.from_user.username or f"user_{user_id}"
                full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip() or "Без имени"
                msk_time = get_msk_time()

                order_text = (
                    f"📦 НОВЫЙ ЗАКАЗ!\n\n"
                    f"👤 @{username}\n"
                    f"🆔 {user_id}\n"
                    f"📛 {full_name}\n"
                    f"🛒 {product}\n"
                    f"⭐ {price} Stars\n"
                    f"🕐 {msk_time}\n\n"
                    f"💳 Оплата на @iadza"
                )
                bot.send_message(SELLER_ID, order_text)
                bot.send_message(
                    user_id,
                    f"✅ Заказ на {product} принят!\n\n"
                    f"Переведите {price} Stars на @iadza\n"
                    f"После оплаты напишите продавцу.",
                    reply_markup=get_main_menu()
                )
        except Exception as e:
            print(f"❌ webapp: {e}\n{traceback.format_exc()}")
            bot.send_message(message.chat.id, "❌ Ошибка.", reply_markup=get_main_menu())

    # ============================================================
    # 6. ЗАПУСК БОТА С АВТОПЕРЕЗАПУСКОМ
    # ============================================================
    print("🔄 Запуск polling...")

    while True:
        try:
            print("✅ БОТ РАБОТАЕТ!")
            bot.polling(non_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"❌ Ошибка: {e}\n{traceback.format_exc()}")
            print("🔄 Перезапуск через 5 сек...")
            time.sleep(5)

# ============================================================
# 7. СТАРТ
# ============================================================
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Запускаем Flask в ГЛАВНОМ потоке (Render видит порт сразу)
    port = int(os.environ.get('PORT', 10000))
    print(f"🔥 Запуск веб-сервера на порту {port}")
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
