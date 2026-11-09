import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# Bot va Admin sozlamalari
BOT_TOKEN = "9207194444:AAFbuZLm_iH6Cn-oaosmsuCW8gAujDgdazI"
ADMIN_ID = 1872175086

# Conversation state-lari (Buyurtma bosqichlari)
PHONE, ADDRESS, QUANTITY = range(3)

# Kengaytirilgan Tortlar Menyusi
CAKES_MENU = {
    "red_velvet": {
        "name": "🔴 Red Velvet (Qizil Barsxat)",
        "price": "150,000 so'm",
        "photo": "https://images.unsplash.com/photo-1586985289688-ca3cf47d3e6e?w=600",
        "description": "Mayin biskvit va pishloqli (cream cheese) krem aralashmasi."
    },
    "medovik": {
        "name": "🍯 Medovik (Asalli tort)",
        "price": "120,000 so'm",
        "photo": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600",
        "description": "Tabiiy asal va sariyog'li krem bilan tayyorlangan klassik tort."
    },
    "napoleon": {
        "name": "🥐 Napoleon",
        "price": "130,000 so'm",
        "photo": "https://images.unsplash.com/photo-1535141192574-5d4897c13136?w=600",
        "description": "Qat-qat xamir va zavarnoy krem uyg'unligi."
    },
    "snickers": {
        "name": "🥜 Snickers Tort",
        "price": "160,000 so'm",
        "photo": "https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=600",
        "description": "Shokoladli biskvit, arab yong'og'i va karamel bilan."
    },
    "tiramisu": {
        "name": "☕ Tiramisu",
        "price": "170,000 so'm",
        "photo": "https://images.unsplash.com/photo-1571115177098-24ec42ed204d?w=600",
        "description": "Italiya uslubidagi maskarpone pishlog'i va kofe ta'mli desert."
    },
    "cheesecake": {
        "name": "🧀 Chizkeyk Nyuyork",
        "price": "180,000 so'm",
        "photo": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=600",
        "description": "Nozik pishloqli va qumoq pechenyeli klassik chizkeyk."
    },
    "fruity": {
        "name": "🍓 Mevali Tort",
        "price": "140,000 so'm",
        "photo": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=600",
        "description": "Yengil biskvit va yangi mevalar bilan bezatilgan desert."
    },
    "chocolate": {
        "name": "🍫 Shokoladli Mousse",
        "price": "165,000 so'm",
        "photo": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600",
        "description": "Achchiq va sutli shokoladli premium desert."
    }
}

def get_main_menu():
    keyboard = []
    for key, cake in CAKES_MENU.items():
        keyboard.append([InlineKeyboardButton(cake["name"], callback_data=f"cake_{key}")])
    return InlineKeyboardMarkup(keyboard)

def get_cake_action_keyboard(cake_key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buyurtma berish", callback_data=f"order_{cake_key}")],
        [InlineKeyboardButton("⬅️ Ortga qaytish", callback_data="back_to_menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}!\n\n"
        "🍰 Shirinliklar botimizga xush kelibsiz. Quyidagi tortlardan birini tanlang:",
        reply_markup=get_main_menu()
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("cake_"):
        cake_key = data.replace("cake_", "")
        if cake_key in CAKES_MENU:
            cake = CAKES_MENU[cake_key]
            caption = (
                f"<b>{cake['name']}</b>\n\n"
                f"📝 <b>Tavsif:</b> {cake['description']}\n"
                f"💰 <b>Narxi:</b> {cake['price']}"
            )
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=cake["photo"],
                caption=caption,
                parse_mode="HTML",
                reply_markup=get_cake_action_keyboard(cake_key)
            )

    elif data == "back_to_menu":
        await query.message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Quyidagi tortlardan birini tanlang:",
            reply_markup=get_main_menu()
        )

# Buyurtma berish bosqichi
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cake_key = query.data.replace("order_", "")
    context.user_data["order_cake"] = CAKES_MENU[cake_key]["name"]
    context.user_data["order_price"] = CAKES_MENU[cake_key]["price"]

    phone_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Buyurtmani rasmiylashtirish uchun pastdagi tugma orqali telefon raqamingizni yuboring:",
        reply_markup=phone_keyboard
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text

    context.user_data["phone"] = phone

    await update.message.reply_text(
        "Rahmat! Endi yetkazib berish manzilini (shahar, ko'cha, uy) yozib yuboring:"
    )
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text

    await update.message.reply_text(
        "Nechta tort buyurtma qilmoqchisiz? (Masalan: 1 ta yoki 2 kg):"
    )
    return QUANTITY

async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quantity"] = update.message.text
    user = update.effective_user

    # Mijozga tasdiq xabari
    await update.message.reply_text(
        "✅ Rahmat! Buyurtmangiz qabul qilindi. Tez orada siz bilan bog'lanamiz.",
        reply_markup=types.ReplyKeyboardRemove()
    )

    # ADMINGA BUYURTMA HAQIDA MA'LUMOT YUBORISH
    admin_message = (
        f"📥 <b>YANGI BUYURTMA!</b>\n\n"
        f"👤 <b>Mijoz:</b> {user.full_name} (@{user.username if user.username else 'yoq'})\n"
        f"📞 <b>Tel:</b> {context.user_data['phone']}\n"
        f"📍 <b>Manzil:</b> {context.user_data['address']}\n\n"
        f"🍰 <b>Tort:</b> {context.user_data['order_cake']}\n"
        f"💰 <b>Narxi:</b> {context.user_data['order_price']}\n"
        f"🔢 <b>Soni:</b> {context.user_data['quantity']}"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Adminga xabar yuborishda xatolik: {e}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buyurtma bekor qilindi.")
    return ConversationHandler.END

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^order_")],
        states={
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="^(cake_|back_to_menu)"))
    app.add_handler(conv_handler)

    print("Bot 24/7 rejimida ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
