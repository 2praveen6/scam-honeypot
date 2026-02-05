from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.config import TELEGRAM_BOT_TOKEN
from app.services.honeypot_agent import honeypot_analyze, reset_conversation
import json

# Track which users are in honeypot mode
honeypot_mode_users = set()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = """
🛡️ **Scam Detection & Honeypot Bot**

**Commands:**
/start - Welcome message
/honeypot - Enable honeypot mode (engage scammers)
/detect - Normal detection mode
/reset - Reset conversation
/help - Show help

**How to use:**
1. Forward suspicious message
2. Get instant analysis
3. In honeypot mode, I'll help you engage scammers safely!

Stay safe! 🔒
    """
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def honeypot_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    honeypot_mode_users.add(user_id)
    await update.message.reply_text(
        "🕵️ **Honeypot Mode ACTIVATED**\n\n"
        "Forward scammer messages here.\n"
        "I'll respond as 'Ramesh' to extract their details.\n\n"
        "Use /detect to switch back to normal mode.",
        parse_mode='Markdown'
    )

async def detect_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    honeypot_mode_users.discard(user_id)
    await update.message.reply_text(
        "🔍 **Detection Mode ACTIVATED**\n\n"
        "Send any message for scam analysis.",
        parse_mode='Markdown'
    )

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    reset_conversation(user_id)
    await update.message.reply_text("🔄 Conversation reset!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message = update.message.text
    
    await update.message.chat.send_action("typing")
    
    if user_id in honeypot_mode_users:
        # HONEYPOT MODE
        result = honeypot_analyze(user_id, message)
        
        intel = result["extracted_intelligence"]
        intel_found = []
        if intel["upi_id"]: intel_found.append(f"• UPI: `{intel['upi_id']}`")
        if intel["bank_account"]: intel_found.append(f"• Bank: `{intel['bank_account']}`")
        if intel["ifsc"]: intel_found.append(f"• IFSC: `{intel['ifsc']}`")
        if intel["phishing_links"]: intel_found.append(f"• Links: {intel['phishing_links']}")
        if intel["phone_numbers"]: intel_found.append(f"• Phones: {intel['phone_numbers']}")
        
        response = f"""
🕵️ **HONEYPOT ANALYSIS**

**Scam Type:** {result['scam_type']}
**Confidence:** {int(result['confidence']*100)}%
**Risk Level:** {result['risk_level'].upper()}
**Turn:** {result['turn_count']}/6

---
📤 **Reply as Ramesh:**
_{result['honeypot_response']}_

---
🔍 **Intel Extracted:**
{chr(10).join(intel_found) if intel_found else '• None yet'}

---
{"✅ **CONVERSATION COMPLETE** - Intel gathered!" if result['conversation_complete'] else "💬 Continue forwarding scammer replies..."}
        """
        await update.message.reply_text(response, parse_mode='Markdown')
        
    else:
        # NORMAL DETECTION MODE
        from app.services.ai_service import analyze_message
        result = json.loads(analyze_message(message))
        
        emoji = "🚨" if result["is_scam"] else "✅"
        status = "SCAM DETECTED" if result["is_scam"] else "LOOKS SAFE"
        
        response = f"""
{emoji} **{status}**

**Confidence:** {result['confidence']}%
**Type:** {result.get('scam_type', 'N/A')}

**Red Flags:**
{chr(10).join(['• ' + f for f in result['red_flags']]) if result['red_flags'] else '• None'}

**Advice:** {result['advice']}
        """
        await update.message.reply_text(response, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔍 **Bot Modes:**

**1. Detection Mode** (default)
- Analyzes messages for scams
- Returns confidence & red flags

**2. Honeypot Mode** (/honeypot)
- Pretends to be victim "Ramesh"
- Engages scammers
- Extracts UPI, bank details, links

**Commands:**
/honeypot - Enable honeypot
/detect - Normal detection
/reset - Clear conversation
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

def run_bot():
    print("🤖 Starting Honeypot Bot...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("honeypot", honeypot_mode))
    app.add_handler(CommandHandler("detect", detect_mode))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    run_bot()