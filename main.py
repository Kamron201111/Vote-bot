import telebot
from telebot import types
from selenium_py.sl import Vote, save_user
from Config.config import TOKEN

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        f"Assalomu aleykum <b>{message.from_user.first_name}</b> botimizga xush kelibsiz! \n\n"
        f"Ovoz berishdan avval telefon nomeringizni yuboring.\n"
        f"Masalan: <code>973332222</code>\n\n"
        f"⚠️ Iltimos <b>+998</b> belgisini ishlatmang!"
    )
    bot.register_next_step_handler(message, user_answer)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'yes':
        # Inline tugmalarni o'chirish
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        Vote(bot=bot, msg=call.message)
    elif call.data == 'no':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, '❌ Ovoz berish bekor qilindi.')


def user_answer(msg):
    msg_str = str(msg.text).strip()

    if msg_str.startswith('+'):
        new_msg = bot.send_message(msg.chat.id, "⚠️ Iltimos +998 ishlatmang, faqat raqamlarni kiriting.\nMasalan: <code>973332222</code>")
        bot.register_next_step_handler(new_msg, user_answer)
        return

    # Faqat raqam kiritilganini tekshirish
    if not msg_str.isdigit():
        new_msg = bot.send_message(msg.chat.id, "⚠️ Faqat raqam kiriting!\nMasalan: <code>973332222</code>")
        bot.register_next_step_handler(new_msg, user_answer)
        return

    # Uzunlikni tekshirish (9 ta raqam)
    if len(msg_str) != 9:
        new_msg = bot.send_message(msg.chat.id, f"⚠️ Noto'g'ri format! 9 ta raqam bo'lishi kerak.\nSiz {len(msg_str)} ta kiritdingiz.\nMasalan: <code>973332222</code>")
        bot.register_next_step_handler(new_msg, user_answer)
        return

    phone_number = msg_str
    bot.send_message(msg.chat.id, '📱 Telefon raqam saqlanmoqda...')

    resp = save_user(phone_number=phone_number, msg=msg, bot=bot)

    if resp:
        markup_inline = types.InlineKeyboardMarkup()
        item_yes = types.InlineKeyboardButton(text='✅ Ha, ovoz beraman', callback_data='yes')
        item_no = types.InlineKeyboardButton(text='❌ Yo\'q', callback_data='no')
        markup_inline.add(item_yes, item_no)

        bot.send_message(
            msg.chat.id,
            f"📞 Raqam: <b>+998{phone_number}</b>\n\nOvoz berasizmi?",
            reply_markup=markup_inline
        )


if __name__ == '__main__':
    print("✅ Asosiy bot ishga tushdi...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
