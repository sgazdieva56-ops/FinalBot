from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from datetime import datetime


def get_main_keyboard():
    keyboard = [
        [
            KeyboardButton("➕ Записать день"),
            KeyboardButton("📊 Статистика")
        ],
        [
            KeyboardButton("📜 История"),
            KeyboardButton("🔍 Инсайты")
        ],
        [
            KeyboardButton("⚙️ Настройки"),
            KeyboardButton("❓ Помощь")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def get_mood_keyboard():
    keyboard = [[
        InlineKeyboardButton("1 😞", callback_data="mood_1"),
        InlineKeyboardButton("2 😐", callback_data="mood_2"),
        InlineKeyboardButton("3 🙂", callback_data="mood_3"),
        InlineKeyboardButton("4 😊", callback_data="mood_4"),
        InlineKeyboardButton("5 🤩", callback_data="mood_5")
    ]]

    return InlineKeyboardMarkup(keyboard)


def get_hours_keyboard(hours_type='work'):
    if hours_type == 'work':
        buttons = [
            ['0.5 ч', '1 ч', '2 ч', '4 ч'],
            ['6 ч', '8 ч', 'Другое...']
        ]
    else:
        buttons = [
            ['6 ч', '7 ч', '8 ч', '9 ч'],
            ['10 ч', 'Другое...']
        ]

    keyboard = []

    for row in buttons:
        keyboard.append([
            KeyboardButton(btn)
            for btn in row
        ])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_stats_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📅 За неделю", callback_data="stats_week")
        ],
        [
            InlineKeyboardButton("🗓 За месяц", callback_data="stats_month")
        ],
        [
            InlineKeyboardButton("📉 График", callback_data="stats_chart")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "⏰ Изменить время",
                callback_data="change_time"
            )
        ],
        [
            InlineKeyboardButton(
                "🗑 Очистить данные",
                callback_data="clear_data"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_confirm_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Да",
                callback_data="confirm_clear"
            ),
            InlineKeyboardButton(
                "❌ Нет",
                callback_data="cancel_clear"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def validate_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except:
        return False


def get_mood_emoji(score):
    emojis = {
        1: '😞',
        2: '😐',
        3: '🙂',
        4: '😊',
        5: '🤩'
    }

    return emojis.get(score, '😐')