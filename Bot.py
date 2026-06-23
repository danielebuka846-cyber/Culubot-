import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL") 
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    result = supabase.table('users').select("*").eq('user_id', user_id).execute()
    if not result.data:
        supabase.table('users').insert({
            'user_id': user_id,
            'username': user.username,
            'balance': 0,
            'taps': 0
        }).execute()
        await update.message.reply_text(f"Welcome {user.first_name}! Your tap bot account is created. Use /tap to start earning.")
    else:
        await update.message.reply_text(f"Welcome back {user.first_name}! Use /tap to earn.")

async def tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    result = supabase.table('users').select("*").eq('user_id', user_id).execute()
    user_data = result.data[0]
    new_taps = user_data['taps'] + 1
    new_balance = user_data['balance'] + 1
    supabase.table('users').update({
        'taps': new_taps,
        'balance': new_balance
    }).eq('user_id', user_id).execute()
    await update.message.reply_text(f"Tap! +1 point\nTotal taps: {new_taps}\nBalance: {new_balance}")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    result = supabase.table('users').select("*").eq('user_id', user_id).execute()
    if result.data:
        bal = result.data[0]['balance']
        await update.message.reply_text(f"Your balance: {bal} points")
    else:
        await update.message.reply_text("Use /start first")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tap", tap))
    app.add_handler(CommandHandler("balance", balance))
    app.run_polling()

if __name__ == '__main__':
    main()
