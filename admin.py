import telebot
from telebot import types
from Config.config import TOKEN_ADMIN, PASSWORD
from database import db, sql

bot = telebot.TeleBot(TOKEN_ADMIN, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    create_user(message)

    if check_user(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton('👥 Foydalanuvchilar'),
            types.KeyboardButton('👑 Adminlar'),
            types.KeyboardButton('📊 Statistika')
        )
        bot.send_message(
            message.chat.id,
            f"Assalomu aleykum <b>admin</b> 👋\nAdmin panelga xush kelibsiz!",
            reply_markup=markup
        )
    else:
        msg = bot.send_message(
            message.chat.id,
            f"Assalomu aleykum <b>{message.from_user.first_name}</b>!\n🔒 Kirish uchun parolni kiriting:"
        )
        bot.register_next_step_handler(msg, check_password)


def check_password(msg):
    if msg.text == PASSWORD:
        sql.execute(
            "UPDATE admins SET status = 1 WHERE telegram_id = ?", (msg.chat.id,)
        )
        db.commit()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton('👥 Foydalanuvchilar'),
            types.KeyboardButton('👑 Adminlar'),
            types.KeyboardButton('📊 Statistika')
        )
        bot.send_message(msg.chat.id, "✅ Parol to'g'ri! Xush kelibsiz admin!", reply_markup=markup)
    else:
        new_msg = bot.send_message(msg.chat.id, "❌ Parol noto'g'ri! Qaytadan urinib ko'ring:")
        bot.register_next_step_handler(new_msg, check_password)


def create_user(message):
    telegram_id = message.chat.id
    first_name = message.chat.first_name or "Noma'lum"
    username = message.chat.username or ""

    existing = sql.execute(
        "SELECT id FROM admins WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()

    if existing is None:
        sql.execute(
            "INSERT INTO admins(first_name, username, telegram_id, status) VALUES(?, ?, ?, 0)",
            (first_name, username, telegram_id)
        )
        db.commit()


def check_user(message):
    result = sql.execute(
        "SELECT status FROM admins WHERE telegram_id = ?", (message.chat.id,)
    ).fetchone()

    if result and result[0] == 1:
        return True
    return False


@bot.message_handler(content_types=['text'])
def text_handler(message):
    if not check_user(message):
        bot.send_message(message.chat.id, "⚠️ Iltimos ro'yhatdan o'ting! /start")
        return

    if message.text == '👥 Foydalanuvchilar':
        get_users(message)
    elif message.text == '👑 Adminlar':
        get_admins(message)
    elif message.text == '📊 Statistika':
        get_stats(message)


def get_users(message):
    users = sql.execute("SELECT * FROM users").fetchall()

    if not users:
        bot.send_message(message.chat.id, "📭 Hech qanday foydalanuvchi yo'q.")
        return

    bot.send_message(message.chat.id, f"👥 Jami foydalanuvchilar: <b>{len(users)}</b>")

    for user in users:
        id, first_name, username, telegram_id, status, phone_number = user
        status_m = '✅ Ovoz bergan' if status == 1 else '❌ Ovoz bermagan'
        uname = f"@{username}" if username else "—"

        bot.send_message(
            message.chat.id,
            f"👤 <b>{first_name}</b> #{id}\n\n"
            f"📱 Tel: +998{phone_number}\n"
            f"🔗 Username: {uname}\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>\n"
            f"📌 Status: {status_m}"
        )


def get_admins(message):
    admins = sql.execute("SELECT * FROM admins WHERE status = 1").fetchall()

    if not admins:
        bot.send_message(message.chat.id, "📭 Admin topilmadi.")
        return

    bot.send_message(message.chat.id, f"👑 Adminlar soni: <b>{len(admins)}</b>")

    for admin in admins:
        id, first_name, username, telegram_id, status = admin
        uname = f"@{username}" if username else "—"
        bot.send_message(
            message.chat.id,
            f"👑 <b>{first_name}</b> #{id}\n\n"
            f"🔗 Username: {uname}\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>"
        )


def get_stats(message):
    total = sql.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    voted = sql.execute("SELECT COUNT(*) FROM users WHERE status = 1").fetchone()[0]
    not_voted = total - voted

    bot.send_message(
        message.chat.id,
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"✅ Ovoz berganlar: <b>{voted}</b>\n"
        f"❌ Ovoz bermaganlar: <b>{not_voted}</b>"
    )


if __name__ == '__main__':
    print("✅ Admin bot ishga tushdi...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
