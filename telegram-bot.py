import os
import sys
import csv
import re
import requests
import datetime
from shamsi_date import convert_to_shamsi

from typing import Dict
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    CallbackQuery,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

                
class BotRunner:
    def __init__(self, token: str, avwx_token: str):
        self.token = token
        self.avwx_token = avwx_token
        self.notam_file = "notam_data.csv"
        self.airport_names_file = "IRAN_AIRPORTS.csv"
        self.airport_names = self.load_airport_names()

    def load_airport_names(self) -> Dict[str, str]:
        airport_names = {}
        if os.path.exists(self.airport_names_file):
            try:
                with open(self.airport_names_file, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip the header
                    for row in reader:
                        if len(row) >= 2:
                            icao = row[0].strip().upper()
                            name = row[1].strip()
                            airport_names[icao] = name
            except Exception as e:
                print(f"Error loading airport names: {e}")
        return airport_names

    def fetch_notams_for_airport(self, icao: str) -> str:
        notams = []
        if os.path.exists(self.notam_file):
            try:
                with open(self.notam_file, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['ICAO'].strip().upper() == icao:
                            from_date = row.get('From', 'N/A')
                            to_date = row.get('To', 'N/A')
                            
                            # Convert dates to Shamsi
                            try:
                                shamsi_from = convert_to_shamsi(from_date, 3.5) if from_date != 'N/A' else 'N/A'
                            except Exception:
                                shamsi_from = 'Invalid date'

                            try:
                                shamsi_to = convert_to_shamsi(to_date, 3.5) if to_date != 'N/A' else 'N/A'
                            except Exception:
                                shamsi_to = 'Invalid date'


                            notam_entry = (
                                "---------------------------\n"
                                f"**NOTAM No:** {row.get('NOTAM No', 'N/A')}\n"
                                f"**Q Code:** {row.get('Q Code', 'N/A')}\n"
                                f"**From:** {row.get('From', 'N/A')}\n"
                                f"**To:** {row.get('To', 'N/A')}\n"
                                f"**Schedule:** {row.get('Schedule', 'N/A')}\n"
                                f"**Text:** {row.get('Text', 'N/A')}\n"
                                f"**Lower Limit:** {row.get('Lower Limit', 'N/A')}\n"
                                f"**Upper Limit:** {row.get('Upper Limit', 'N/A')}\n\n"
                                f"**از :** ({shamsi_from})\n"
                                f"**تا :** ({shamsi_to})\n\n"
                            )

                            # Add Farsi translation if available
                            farsi_translation = row.get('Farsi', '').strip()
                            if farsi_translation:
                                notam_entry += f"\n**شرح مختصر :**\n\n{farsi_translation}\n"

                            notam_entry += "---------------------------\n\n"
                            notams.append(notam_entry)

            except Exception as e:
                print(f"Error reading NOTAM data: {e}")
        return "\n".join(notams) if notams else None

    def get_airport_metar(self, icao: str) -> str:
        base_url = "https://avwx.rest/api"
        headers = {
            "Authorization": f"Token {self.avwx_token}"
        }

        # URL for METAR
        metar_url = f"{base_url}/metar/{icao}"

        # Fetch METAR from AVWX
        try:
            metar_response = requests.get(metar_url, headers=headers, timeout=10)
            metar_response.raise_for_status()
            metar_data = metar_response.json()
            metar_text = metar_data.get("raw", f"Was unable to fetch METAR for {icao}.")
        except Exception:
            metar_text = f"Was unable to fetch METAR for {icao}."

        # Format the response
        result = f"**METAR for {icao.upper()}**\n\n"
        result += f"{metar_text}\n"
        return result

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        buttons = [
            [
                InlineKeyboardButton("METAR", callback_data="METAR"),
                InlineKeyboardButton("NOTAM", callback_data="NOTAM")#,
                #InlineKeyboardButton("Wx FORECAST", callback_data="FORECAST"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Choose a category:", reply_markup=reply_markup)


    async def category_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        category = query.data
        context.user_data['category'] = category

        # Show the first page of airports or prompt for manual input
        await self.show_airport_page(query, context, page=0)

    async def show_airport_page(self, query, context, page=0):
        airports = list(self.airport_names.keys()) #airports = sorted(self.airport_names.keys())
        airports_per_page = 10
        start = page * airports_per_page
        end = start + airports_per_page
        current_airports = airports[start:end]

        buttons = [
            [InlineKeyboardButton(icao, callback_data=f"{context.user_data['category']}_{icao}")]
            for icao in current_airports
        ]

        # Add pagination buttons
        pagination_buttons = []
        if start > 0:
            pagination_buttons.append(InlineKeyboardButton("Previous", callback_data=f"page_{page-1}"))
        if end < len(airports):
            pagination_buttons.append(InlineKeyboardButton("Next", callback_data=f"page_{page+1}"))

        if pagination_buttons:
            buttons.append(pagination_buttons)

        # Add "Other" button
        buttons.append([InlineKeyboardButton("Other", callback_data="OTHER")])

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Select an airport ({context.user_data['category']}):", reply_markup=reply_markup)

    async def pagination_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        page = int(query.data.split("_")[1])
        await self.show_airport_page(query, context, page=page)

    async def airport_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = query.data
        try:
            category, icao = data.split("_", 1)
        except ValueError:
            await query.edit_message_text("Invalid data received.")
            return

        if category == "METAR":
            await self.send_metar(query, context, icao)
        elif category == "NOTAM":
            await self.send_notam(query, context, icao)
        else:
            await query.edit_message_text("Unsupported category selected.")

    def log_user_interaction(self, query: CallbackQuery, message_type: str, icao: str):
        log_file = "user_log.csv"
        user = query.from_user

        # Extract user details
        name = user.first_name or ""
        family = user.last_name or ""
        user_id = user.id  # Guaranteed unique ID for the user
        username = user.username or ""
        phone = user.phone_number if hasattr(user, 'phone_number') else ""
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Write to CSV file
        log_exists = os.path.exists(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not log_exists:
                writer.writerow(["Name", "Family", "UserID", "Username", "Phone", "DateTime", "MessageType", "Airport"])
            writer.writerow([name, family, user_id, username, phone, date_time, message_type, icao])




    async def send_notam(self, query: Update, context: ContextTypes.DEFAULT_TYPE, icao: str):
        notams = self.fetch_notams_for_airport(icao)
        if notams:
            airport_name = self.airport_names.get(icao, f"Unknown Airport ({icao})")
            message = f"**NOTAM(s) for {airport_name} ({icao})**\n\n{notams}"
    
            max_length = 4000
            parts = [message[i:i + max_length] for i in range(0, len(message), max_length)]

            await query.edit_message_text(parts[0], parse_mode="Markdown")
            for part in parts[1:]:
                 await query.message.reply_text(part, parse_mode="Markdown")
        else:
            await query.edit_message_text(f"No NOTAMs found for {icao}.")

        self.log_user_interaction(query, "NOTAM", icao)
    



    async def send_metar(self, query: Update, context: ContextTypes.DEFAULT_TYPE, icao: str):
        info = self.get_airport_metar(icao)
        await query.edit_message_text(info, parse_mode="Markdown")
        self.log_user_interaction(query, "METAR", icao)


    async def handle_other_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        # Set a flag indicating that the bot is awaiting an ICAO code
        context.user_data['awaiting_icao'] = True

        # Optionally, clear the selected category if needed
        # context.user_data.pop('category', None)

        await query.edit_message_text("Please enter a 4-letter ICAO code (e.g., OIII):")




    async def handle_icao_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.user_data.get('awaiting_icao'):
            # If not awaiting ICAO, ignore or send a default message
            return

        icao = update.message.text.strip().upper()

        # Validate the ICAO code
        if not re.fullmatch(r'[A-Z]{4}', icao):
            await update.message.reply_text("Invalid ICAO code format. Please enter a 4-letter ICAO code (e.g., OIII).")
            return

        # Reset the awaiting flag
        context.user_data['awaiting_icao'] = False

        category = context.user_data.get('category')

        if not category:
            await update.message.reply_text("No category selected. Please start again with /start.")
            return

        if category == "METAR":
            info = self.get_airport_metar(icao)
            await update.message.reply_text(info, parse_mode="Markdown")
        elif category == "NOTAM":
            notams = self.fetch_notams_for_airport(icao)
            if notams:
                airport_name = self.airport_names.get(icao, f"Unknown Airport ({icao})")
                message = f"**NOTAM(s) for {airport_name} ({icao})**\n\n{notams}"
                await update.message.reply_text(message, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"No NOTAMs found for {icao}.")
        else:
            await update.message.reply_text("Unsupported category selected.")

    async def other_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # This handler will catch "OTHER" callback data
        await self.handle_other_button(update, context)

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(update.message.text)

    def run_bot(self):
        application = ApplicationBuilder().token(self.token).build()

        # Command handlers
        application.add_handler(CommandHandler("start", self.start))

        # Callback query handlers
        application.add_handler(CallbackQueryHandler(self.category_handler, pattern="^(METAR|NOTAM|FORECAST)$")) #
        application.add_handler(CallbackQueryHandler(self.pagination_handler, pattern="^page_\\d+$"))
        application.add_handler(CallbackQueryHandler(self.airport_handler, pattern="^(METAR|NOTAM)_[A-Z0-9]+$"))
        application.add_handler(CallbackQueryHandler(self.other_callback_handler, pattern="^OTHER$"))

        # Message handlers
        # This handler will capture ICAO codes when the bot is awaiting them
        icao_handler = MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_icao_code
        )
        application.add_handler(icao_handler)

        # Optional: Echo handler for messages not related to ICAO input
        # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

        application.run_polling()

    def run_with_proxy_option(self):
        if "--proxy" not in sys.argv:
            command = ["proxychains", sys.executable] + sys.argv + ["--proxy"]
            try:
                os.execvp("proxychains", command)
            except FileNotFoundError:
                print("proxychains not found. Running the bot without proxy...")
                self.run_bot()
            except Exception as e:
                print(f"An error occurred with proxychains: {e}. Running the bot without proxy...")
                self.run_bot()
        else:
            self.run_bot()


if __name__ == '__main__':
    # **Security Note:** 
    # Never hardcode your tokens in the source code. 
    # Use environment variables or a secure secrets manager instead.
    TELEGRAM_TOKEN = '' #os.getenv("TELEGRAM_TOKEN")
    
    AVWX_TOKEN = '' #os.getenv("AVWX_TOKEN") 

    runner = BotRunner(TELEGRAM_TOKEN, AVWX_TOKEN)
    runner.run_with_proxy_option()
