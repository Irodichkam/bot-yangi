import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot va Admin sozlamalari
BOT_TOKEN = "9207194444:AAFbuZLm_iH6Cn-oaosmsuCW8gAujDgdazI"
ADMIN_ID = 1872175086

# Tort turlari (Nomi, rasmi, narxi va tavsifi bilan)
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
        "description": "Qat-qat xamir va zavarnoy (pishirilgan) krem uyg'unligi."
    },
    "snickers": {
        "name": "🥜 Snickers Tort",
        "price": "160,000 so'm",
        "photo": "https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=600",
        "description": "Shokoladli biskvit, arab yong'og'i va karamel bilan."
    }
}

def main_menu_keyboard():
    keyboard = []
    for key, cake in CAKES_MENU.items():
        keyboard.append([InlineKeyboardButton(cake["name"], callback_data=f"cake_{key}")])
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Ortga qaytish", callback_data="back_to_menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}!\n\n"
        "Shirinliklar botimizga xush kelibsiz. Quyidagi tortlardan birini tanlang:",
        reply_markup=main_menu_keyboard()
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("cake_"):
        cake_key = data.replace("cake_", "")
        if cake_key in CAKES_MENU:
            cake = CAKES_MENU[cake_key]
            caption_text = (
                f"<b>{cake['name']}</b>\n\n"
                f"📝 <b>Tavsif:</b> {cake['description']}\n"
                f"💰 <b>Narxi:</b> {cake['price']}"
            )
            
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=cake["photo"],
                caption=caption_text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )

    elif data == "back_to_menu":
        await query.message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Quyidagi tortlardan birini tanlang:",
            reply_markup=main_menu_keyboard()
        )

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
