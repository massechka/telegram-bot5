import telebot
import os
import time
import json
from datetime import datetime, timezone, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

print("🚀 Запуск бота FluxShop...")

# ==========================================
# 🔥 ВАШИ ДАННЫЕ:
# ==========================================
BOT_TOKEN = "8980889906:AAFumieQpR1QvzBfjYeFKzr-OrUKrAN489w"
CHANNEL_ID = "-1004393648334"
SELLER_ID = "7389526173"  # @iadza
SUPPORT_ID = "8140113992"  # @rfrpq (ЗАМЕНИТЕ НА РЕАЛЬНЫЙ ID)
WEBAPP_URL = "https://warm-daifuku-2653f5.netlify.app/"
RULES_URL = "https://fluxsshops.netlify.app"
# ==========================================

print(f"✅ Токен: {'ДА' if BOT_TOKEN else 'НЕТ'}")
print(f"✅ CHANNEL_ID: {'ДА' if CHANNEL_ID else 'НЕТ'}")
print(f"✅ SELLER_ID: {'ДА' if SELLER_ID else 'НЕТ'}")
print(f"✅ SUPPORT_ID: {'ДА' if SUPPORT_ID else 'НЕТ'}")
print(f"✅ WEBAPP_URL: {'ДА' if WEBAPP_URL else 'НЕТ'}")

if not all([BOT_TOKEN, CHANNEL_ID, SELLER_ID, WEBAPP_URL, SUPPORT_ID]):
    print("❌ ОШИБКА: Не все данные введены!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
print("🤖 Бот создан")

try:
    bot.remove_webhook()
    print("✅ Webhook удалён")
except Exception as e:
    print(f"⚠️ Не удалось удалить webhook: {e}")

# ==========================================
# 📅 ВРЕМЯ РАБОТЫ ПОДДЕРЖКИ
# ==========================================
SUPPORT_SCHEDULE = """
📅 График работы поддержки:

ПН 14:00 — 22:00
ВТ 14:00 — 22:00
СР 14:00 — 22:00
ЧТ 14:00 — 22:00
ПТ 14:00 — 22:00
СБ 16:00 — 22:00
ВС 16:00 — 22:00
"""

# ==========================================
# 🕐 ВРЕМЯ ПО МСК
# ==========================================
def get_msk_time():
    msk = timezone(timedelta(hours=3))
    now = datetime.now(msk)
    return now.strftime("%d.%m.%Y %H:%M:%S")

def get_current_day():
    msk = timezone(timedelta(hours=3))
    now = datetime.now(msk)
    days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
    return days[now.weekday()]

# ==========================================
# 🎛️ КНОПКИ
# ==========================================

def get_subscribe_button():
    keyboard = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/FluxSshop")
    keyboard.add(btn)
    return keyboard

def get_check_button():
    keyboard = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")
    keyboard.add(btn)
    return keyboard

def get_webapp_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn = KeyboardButton("🛒 Магазин", web_app=WebAppInfo(WEBAPP_URL))
    keyboard.add(btn)
    return keyboard

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = KeyboardButton("🛒 Магазин", web_app=WebAppInfo(WEBAPP_URL))
    btn2 = KeyboardButton("📞 Связь с продавцом")
    btn3 = KeyboardButton("🆘 Поддержка")
    keyboard.add(btn1, btn2, btn3)
    return keyboard

def get_buy_button():
    keyboard = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("💎 Оплатить Stars", url="https://t.me/iadza")
    keyboard.add(btn)
    return keyboard

def get_support_button():
    keyboard = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("🆘 Написать в поддержку", url="https://t.me/rfrpq")
    keyboard.add(btn)
    return keyboard

# ==========================================
# 🔍 ПРОВЕРКА ПОДПИСКИ
# ==========================================

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        print(f"❌ Ошибка проверки подписки: {e}")
        return False

# ==========================================
# 📨 ОБРАБОТЧИКИ
# ==========================================

@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        print(f"📨 /start от {message.from_user.id}")
        user_id = message.from_user.id
        
        if is_subscribed(user_id):
            bot.send_message(
                message.chat.id,
                "👋 Здравствуйте, здесь вы можете приобрести телеграмм аккаунты.\n\n"
                "Наш тгк: @fluxsshop\n"
                "Наши отзывы: @fluxs_reviews\n"
                f"Наши правила: {RULES_URL}",
                reply_markup=get_main_menu()
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Для доступа к магазину подпишитесь на наш канал:",
                reply_markup=get_subscribe_button()
            )
            bot.send_message(
                message.chat.id,
                "После подписки нажмите кнопку ниже:",
                reply_markup=get_check_button()
            )
    except Exception as e:
        print(f"❌ Ошибка в start_command: {e}")

@bot.message_handler(func=lambda message: True)
def all_messages(message):
    try:
        print(f"📨 Сообщение от {message.from_user.id}: {message.text}")
        user_id = message.from_user.id
        
        if not is_subscribed(user_id):
            bot.send_message(
                message.chat.id,
                "❌ Для доступа подпишитесь на канал @fluxsshop.",
                reply_markup=get_subscribe_button()
            )
            return
        
        text = message.text
        
        if text == "🛒 Магазин":
            bot.send_message(
                message.chat.id,
                "🛒 Добро пожаловать в магазин! Выберите товар в каталоге:",
                reply_markup=get_webapp_button()
            )
        elif text == "📞 Связь с продавцом":
            bot.send_message(
                message.chat.id,
                f"📞 Свяжитесь с продавцом:\n"
                f"👤 @iadza\n"
                f"🆔 ID: {SELLER_ID}\n\n"
                f"💎 Telegram Stars принимаются на @iadza",
                reply_markup=get_buy_button()
            )
        elif text == "🆘 Поддержка":
            bot.send_message(
                message.chat.id,
                f"🆘 Поддержка:\n"
                f"👤 @rfrpq\n"
                f"🆔 ID: {SUPPORT_ID}\n\n"
                f"{SUPPORT_SCHEDULE}\n\n"
                f"📌 Зачем писать в поддержку:\n"
                f"— Вопросы по заказу\n"
                f"— Проблемы с аккаунтом\n"
                f"— Общие вопросы",
                reply_markup=get_support_button()
            )
        else:
            bot.send_message(
                message.chat.id,
                "👋 Здравствуйте, здесь вы можете приобрести телеграмм аккаунты.\n\n"
                "Наш тгк: @fluxsshop\n"
                "Наши отзывы: @fluxs_reviews\n"
                f"Наши правила: {RULES_URL}",
                reply_markup=get_main_menu()
            )
    except Exception as e:
        print(f"❌ Ошибка в all_messages: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    try:
        print(f"📨 Проверка подписки от {call.from_user.id}")
        user_id = call.from_user.id
        
        if is_subscribed(user_id):
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="✅ Подписка подтверждена! Добро пожаловать!",
                reply_markup=None
            )
            bot.send_message(
                user_id,
                "👋 Здравствуйте, здесь вы можете приобрести телеграмм аккаунты.\n\n"
                "Наш тгк: @fluxsshop\n"
                "Наши отзывы: @fluxs_reviews\n"
                f"Наши правила: {RULES_URL}",
                reply_markup=get_main_menu()
            )
        else:
            bot.answer_callback_query(call.id, "❌ Вы ещё не подписались на канал!", show_alert=True)
    except Exception as e:
        print(f"❌ Ошибка в check_subscription: {e}")

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    try:
        print(f"📨 Данные из Mini App от {message.from_user.id}")
        user_id = message.from_user.id
        
        if not is_subscribed(user_id):
            bot.send_message(
                user_id,
                "❌ Для заказа подпишитесь на канал.",
                reply_markup=get_subscribe_button()
            )
            return
        
        data = json.loads(message.web_app_data.data)
        print(f"📦 Получены данные: {data}")
        
        if data.get('action') == 'order':
            product = data.get('product', 'Неизвестно')
            price = data.get('price', '0')
            
            username = message.from_user.username or f"user_{user_id}"
            first_name = message.from_user.first_name or ''
            last_name = message.from_user.last_name or ''
            full_name = f"{first_name} {last_name}".strip() or "Без имени"
            msk_time = get_msk_time()
            
            order_text = f"""📦 НОВЫЙ ЗАКАЗ!

👤 Покупатель: @{username}
🆔 ID: {user_id}
📛 Имя: {full_name}
🛒 Товар: {product}
⭐ Цена: {price} Stars
🕐 Время (МСК): {msk_time}

💳 Оплата на @iadza"""
            
            bot.send_message(SELLER_ID, order_text)
            print(f"✅ Заказ отправлен продавцу {SELLER_ID}")
            
            bot.send_message(
                user_id,
                f"✅ Заказ на {product} принят!\n\n"
                f"⭐ Для оплаты переведите {price} Stars на @iadza\n"
                f"После оплаты напишите продавцу для получения товара.",
                reply_markup=get_main_menu()
            )
        else:
            bot.send_message(
                user_id,
                "⚠️ Неизвестная команда.",
                reply_markup=get_main_menu()
            )
            
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка обработки заказа.", reply_markup=get_main_menu())
    except Exception as e:
        print(f"❌ Ошибка в handle_webapp_data: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка.", reply_markup=get_main_menu())

# ==========================================
# 🚀 ЗАПУСК БОТА
# ==========================================

print("🔄 Запуск polling...")

while True:
    try:
        print("✅ Бот запущен и ждёт сообщения!")
        bot.polling(non_stop=True, interval=1, timeout=30)
    except Exception as e:
        print(f"❌ Ошибка в polling: {e}")
        print("🔄 Перезапуск через 5 секунд...")
        time.sleep(5)
