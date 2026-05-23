from datetime import date
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler,
    ContextTypes, filters
)

from config import BOT_TOKEN
from db_handler import DatabaseHandler
from analyzer import Analyzer

MOOD, WORK, SLEEP, COMMENT = range(4)


class MoodBot:

    def __init__(self):
        self.db = DatabaseHandler()
        self.analyzer = Analyzer()

    def reply_kb(self, buttons):
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    def inline_kb(self, buttons):
        return InlineKeyboardMarkup(buttons)

    def main_keyboard(self):
        return self.reply_kb([
            ["➕ Записать день"],
            ["📊 Статистика"],
            ["📜 История"],
            ["🔍 Инсайты"],
            ["⚙️ Настройки"],
            ["❓ Помощь"]
        ])

    def mood_keyboard(self):

        moods = [
            ("1 😞", "mood_1"),
            ("2 😐", "mood_2"),
            ("3 🙂", "mood_3"),
            ("4 😊", "mood_4"),
            ("5 🤩", "mood_5")
        ]

        return self.inline_kb([[
            InlineKeyboardButton(text, callback_data=data)
            for text, data in moods
        ]])

    def hours_keyboard(self, mode):

        buttons = (
            [["0.5 ч"], ["1 ч"], ["2 ч"], ["4 ч"], ["Другое..."]]
            if mode == "work"
            else [["6 ч"], ["7 ч"], ["8 ч"], ["9 ч"], ["Другое..."]]
        )

        return self.reply_kb(buttons)

    def stats_keyboard(self):
        return self.inline_kb([
            [InlineKeyboardButton("📅 За неделю", callback_data="stats_week")],
            [InlineKeyboardButton("🗓 За месяц", callback_data="stats_month")],
            [InlineKeyboardButton("📉 График", callback_data="stats_chart")]
        ])

    def settings_keyboard(self):
        return self.inline_kb([
            [InlineKeyboardButton("⏰ Изменить время", callback_data="change_time")],
            [InlineKeyboardButton("🗑 Очистить данные", callback_data="clear_data")]
        ])

    def confirm_keyboard(self):
        return self.inline_kb([[
            InlineKeyboardButton("✅ Да", callback_data="confirm_clear"),
            InlineKeyboardButton("❌ Нет", callback_data="cancel_clear")
        ]])

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user = update.effective_user

        self.db.get_or_create_user(
            user.id,
            user.username,
            user.first_name,
            user.last_name
        )

        await update.message.reply_text(
            "🌟 Добро пожаловать!\n\n"
            "Я бот для отслеживания настроения и продуктивности.",
            reply_markup=self.main_keyboard()
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        text = (
            "/start - запуск\n"
            "/add - добавить запись\n"
            "/stats - статистика\n"
            "/history - история\n"
            "/settings - настройки\n"
            "/clear - очистка данных\n"
            "/help - помощь"
        )

        await update.message.reply_text(
            text,
            reply_markup=self.main_keyboard()
        )

    async def add_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        if self.db.entry_exists(update.effective_user.id, date.today()):

            await update.message.reply_text(
                "❌ Запись за сегодня уже существует"
            )

            return ConversationHandler.END

        await update.message.reply_text(
            "😊 Оцени настроение:",
            reply_markup=self.mood_keyboard()
        )

        return MOOD

    async def mood_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        context.user_data["mood"] = int(query.data.split("_")[1])

        await query.message.reply_text(
            "💼 Сколько часов работы/учебы?",
            reply_markup=self.hours_keyboard("work")
        )

        return WORK

    async def work_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        text = update.message.text

        if text == "Другое...":
            await update.message.reply_text("Введите количество часов:")
            return WORK

        try:

            hours = float(text.replace(" ч", ""))

            if not 0 <= hours <= 24:
                raise ValueError

            context.user_data["work"] = hours

            await update.message.reply_text(
                "😴 Сколько часов сна?",
                reply_markup=self.hours_keyboard("sleep")
            )

            return SLEEP

        except:

            await update.message.reply_text("❌ Введите корректное число")
            return WORK

    async def sleep_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        text = update.message.text

        if text == "Другое...":
            await update.message.reply_text("Введите количество часов сна:")
            return SLEEP

        try:

            hours = float(text.replace(" ч", ""))

            if not 0 <= hours <= 24:
                raise ValueError

            context.user_data["sleep"] = hours

            await update.message.reply_text(
                "✏️ Напиши комментарий или используй /skip"
            )

            return COMMENT

        except:

            await update.message.reply_text("❌ Введите корректное число")
            return SLEEP

    async def save_entry(self, update, context, comment=None):

        self.db.save_mood_entry(
            update.effective_user.id,
            date.today(),
            context.user_data["mood"],
            context.user_data["work"],
            context.user_data["sleep"],
            comment
        )

        await update.message.reply_text(
            "✅ Данные успешно сохранены",
            reply_markup=self.main_keyboard()
        )

        return ConversationHandler.END

    async def comment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.save_entry(update, context, update.message.text)

    async def skip_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.save_entry(update, context)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        await update.message.reply_text(
            "📊 Выбери период:",
            reply_markup=self.stats_keyboard()
        )

    async def stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id

        if query.data == "stats_chart":

            df = self.db.get_dataframe(user_id)
            chart = self.analyzer.create_chart(df)

            if chart is None:
                await query.message.reply_text("Недостаточно данных")
                return

            await query.message.reply_photo(chart)
            return

        period = "month" if query.data == "stats_month" else "week"

        stats = self.db.get_statistics_period(user_id, period)

        if stats["total_days"] == 0:
            await query.message.reply_text("Нет данных")
            return

        text = f"""
📊 Статистика

😊 Среднее настроение: {stats['avg_mood']}
😞 Минимальное настроение: {stats['min_mood']}
🤩 Максимальное настроение: {stats['max_mood']}
💼 Средняя работа/учеба: {stats['avg_work']} ч
😴 Средний сон: {stats['avg_sleep']} ч
📅 Всего записей: {stats['total_days']}
"""

        await query.message.reply_text(text)

    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        entries = self.db.get_all_user_entries(update.effective_user.id)

        if not entries:
            await update.message.reply_text("История пуста")
            return

        text = "📜 История\n\n"

        for entry in entries[:10]:

            text += (
                f"📅 {entry['entry_date']}\n"
                f"😊 Настроение: {entry['mood_score']}/5\n"
                f"💼 Работа/учеба: {entry['study_work_hours']} ч\n"
                f"😴 Сон: {entry['sleep_hours']} ч\n"
            )

            if entry["comment"]:
                text += f"✏️ {entry['comment']}\n"

            text += "\n"

        await update.message.reply_text(text)

    async def insights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        insights = self.db.get_insights(update.effective_user.id)

        if "message" in insights:
            await update.message.reply_text(insights["message"])
            return

        text = "🔍 Инсайты\n\n"

        for value in insights.values():
            text += f"• {value}\n\n"

        await update.message.reply_text(text)

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        await update.message.reply_text(
            "⚙️ Настройки",
            reply_markup=self.settings_keyboard()
        )

    async def settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        if query.data == "change_time":

            context.user_data["waiting_time"] = True

            await query.message.reply_text(
                "⏰ Введите новое время в формате HH:MM"
            )

        elif query.data == "clear_data":

            await query.message.reply_text(
                "⚠️ Ты уверен что хочешь удалить ВСЕ данные?",
                reply_markup=self.confirm_keyboard()
            )

        elif query.data == "confirm_clear":

            self.db.clear_user_data(update.effective_user.id)

            await query.message.reply_text(
                "✅ Все данные успешно удалены",
                reply_markup=self.main_keyboard()
            )

        elif query.data == "cancel_clear":

            await query.message.reply_text(
                "❌ Очистка отменена",
                reply_markup=self.main_keyboard()
            )

    async def reminder_time_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        if not context.user_data.get("waiting_time"):
            return

        text = update.message.text.strip()

        try:

            h, m = map(int, text.split(":"))

            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError

        except:

            await update.message.reply_text(
                "❌ Неверный формат времени\n\nИспользуй HH:MM"
            )

            return

        self.db.update_reminder_time(
            update.effective_user.id,
            text
        )

        context.user_data["waiting_time"] = False

        await update.message.reply_text(
            "✅ Время успешно установлено",
            reply_markup=self.main_keyboard()
        )

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        await update.message.reply_text(
            "⚠️ Ты уверен что хочешь удалить ВСЕ данные?",
            reply_markup=self.confirm_keyboard()
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        await update.message.reply_text(
            "❌ Действие отменено",
            reply_markup=self.main_keyboard()
        )

        return ConversationHandler.END

    def run(self):

        app = Application.builder().token(BOT_TOKEN).build()

        async def set_commands(app):

            await app.bot.set_my_commands([
                BotCommand("start", "Запуск"),
                BotCommand("add", "Добавить запись"),
                BotCommand("stats", "Статистика"),
                BotCommand("history", "История"),
                BotCommand("settings", "Настройки"),
                BotCommand("clear", "Очистка данных"),
                BotCommand("help", "Помощь")
            ])

        app.post_init = set_commands

        conv_handler = ConversationHandler(

            entry_points=[
                CommandHandler("add", self.add_entry),
                MessageHandler(filters.Regex("^➕ Записать день$"), self.add_entry)
            ],

            states={

                MOOD: [
                    CallbackQueryHandler(self.mood_handler, pattern="^mood_")
                ],

                WORK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.work_handler)
                ],

                SLEEP: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.sleep_handler)
                ],

                COMMENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.comment_handler),
                    CommandHandler("skip", self.skip_comment)
                ]
            },

            fallbacks=[CommandHandler("cancel", self.cancel)]
        )

        app.add_handler(conv_handler)

        handlers = [
            ("start", self.start),
            ("help", self.help_command),
            ("stats", self.stats_command),
            ("history", self.history_command),
            ("settings", self.settings_command),
            ("clear", self.clear_command)
        ]

        for command, handler in handlers:
            app.add_handler(CommandHandler(command, handler))

        text_handlers = [
            ("^📊 Статистика$", self.stats_command),
            ("^📜 История$", self.history_command),
            ("^🔍 Инсайты$", self.insights_command),
            ("^⚙️ Настройки$", self.settings_command),
            ("^❓ Помощь$", self.help_command)
        ]

        for pattern, handler in text_handlers:
            app.add_handler(MessageHandler(filters.Regex(pattern), handler))

        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.reminder_time_handler
            )
        )

        app.add_handler(
            CallbackQueryHandler(self.stats_callback, pattern="^stats_")
        )

        app.add_handler(
            CallbackQueryHandler(
                self.settings_callback,
                pattern="^(change_time|clear_data|confirm_clear|cancel_clear)$"
            )
        )

        print("Бот запущен")
        app.run_polling()


if __name__ == "__main__":
    MoodBot().run()