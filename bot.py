import logging
import json
import os
import random
from datetime import datetime, time, timedelta
import pytz

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, JobQueue
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8639409120:AAGAeEZVG9FMrwzk7QZGxgaKDpCpHyoowNg"
TIMEZONE = pytz.timezone("Europe/Belgrade")
DATA_FILE = os.path.join(os.path.expanduser("~"), "lumora_progress.json")

MOTIVATIONS = [
    "Огонь! Так и строятся империи 🔥",
    "Каждый шаг — это кирпич в фундаменте Lumora 🏗",
    "Артём в деле. Клиенты ещё не знают что их ждёт 😎",
    "XP накапливается. Уровень растёт. Продолжай 💪",
    "Сделано — значит существует. Молодец 👊",
    "Вот так и выглядит путь к международному агентству ✈️",
    "Маленький шаг сегодня — большой результат через 90 дней 📈",
    "Серьёзные люди делают серьёзные вещи каждый день 🎯",
    "Lumora строится прямо сейчас. Ты в процессе 🚀",
    "Конкуренты отдыхают. Ты работаешь. Разница очевидна 😏",
    "Ещё одна задача — ещё один шаг к первому зарубежному клиенту 🌍",
    "Так и работает дисциплина. Тихо, но мощно ⚡️",
    "Продюсер с таким темпом точно выйдет на международный рынок 🎬",
    "Хорошо сделано — это тоже часть бренда Lumora ✨",
    "Каждое выполненное задание — инвестиция в будущую версию себя 💡",
    "Артём Малыгин. Уровень растёт. История пишется 📖",
    "Это и есть настоящая работа над собой — по одному шагу 🪜",
    "Сделал — отметил — двигаешься дальше. Система работает ⚙️",
    "Будущий основатель международного агентства не пропускает задачи 🏆",
    "Кто-то мечтает. Ты делаешь. Разница именно в этом 💎",
    "Плюс к XP, плюс к опыту, плюс к результату 📊",
    "Ещё один день в плюсе. Серия продолжается 🔗",
    "Lumora — это не просто название. Это то что ты строишь прямо сейчас 🌟",
    "Хорошая работа не требует аплодисментов. Но XP она заслуживает 👏",
    "Продолжай. Через 30 дней ты не узнаешь свои результаты 🎯",
]

PHASES = [
    {
        "name": "Месяц 1 — база",
        "zones": [
            {
                "title": "LinkedIn",
                "tasks": [
                    {"id": "li1", "name": "Заголовок профиля на EN", "xp": 20, "freq": "once"},
                    {"id": "li2", "name": "Пост о своём опыте", "xp": 15, "freq": "daily"},
                    {"id": "li3", "name": "10 личных DM", "xp": 25, "freq": "daily"},
                ]
            },
            {
                "title": "Портфолио",
                "tasks": [
                    {"id": "pf1", "name": "AI demo-ролик 2-3 мин", "xp": 50, "freq": "once"},
                    {"id": "pf2", "name": "Кейс на английском", "xp": 30, "freq": "once"},
                ]
            },
            {
                "title": "Upwork",
                "tasks": [
                    {"id": "up1", "name": "Профиль на Upwork", "xp": 25, "freq": "once"},
                    {"id": "up2", "name": "5 заявок на Upwork", "xp": 20, "freq": "daily"},
                ]
            },
            {
                "title": "Английский",
                "tasks": [
                    {"id": "en1", "name": "30 мин английского", "xp": 10, "freq": "daily"},
                    {"id": "en2", "name": "Текст на английском", "xp": 15, "freq": "daily"},
                ]
            },
        ]
    },
    {
        "name": "Месяц 2 — контракты",
        "zones": [
            {
                "title": "Субподряд",
                "tasks": [
                    {"id": "ag1", "name": "5 DM агентствам", "xp": 30, "freq": "daily"},
                    {"id": "ag2", "name": "Партнёрский pitch", "xp": 40, "freq": "once"},
                ]
            },
            {
                "title": "Контракты",
                "tasks": [
                    {"id": "ct1", "name": "Первый платный проект", "xp": 100, "freq": "once"},
                    {"id": "ct2", "name": "Отзыв от клиента", "xp": 30, "freq": "once"},
                ]
            },
            {
                "title": "Контент",
                "tasks": [
                    {"id": "yt1", "name": "BTS-видео процесса", "xp": 20, "freq": "daily"},
                    {"id": "yt2", "name": "5 комментов клиентам", "xp": 10, "freq": "daily"},
                ]
            },
        ]
    },
    {
        "name": "Месяц 3 — система",
        "zones": [
            {
                "title": "Ретейнеры",
                "tasks": [
                    {"id": "rt1", "name": "Monthly retainer", "xp": 50, "freq": "once"},
                    {"id": "rt2", "name": "3 пакета услуг с ценами", "xp": 35, "freq": "once"},
                ]
            },
            {
                "title": "Релокация",
                "tasks": [
                    {"id": "rl1", "name": "Регистрация ИП Сербия", "xp": 20, "freq": "once"},
                    {"id": "rl2", "name": "Счёт Wise или Payoneer", "xp": 30, "freq": "once"},
                    {"id": "rl3", "name": "Доход 1500+ USD x 2 мес", "xp": 100, "freq": "once"},
                ]
            },
            {
                "title": "Аналитика",
                "tasks": [
                    {"id": "an1", "name": "Конверсия DM", "xp": 15, "freq": "daily"},
                    {"id": "an2", "name": "Инсайт недели", "xp": 10, "freq": "daily"},
                ]
            },
        ]
    },
]

LEVELS = [
    (0,    "Новичок"),
    (100,  "Стартер"),
    (300,  "Практик"),
    (600,  "Профи"),
    (1000, "Эксперт"),
    (1500, "Лидер рынка"),
]

MAX_XP = 1500

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"xp": 0, "streak": 0, "last_day": None, "total_days": 0,
            "done": {}, "once_done": {}, "chat_id": None, "phase": 0}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def today_str():
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d")

def get_level(xp):
    level = 0
    for i, (threshold, _) in enumerate(LEVELS):
        if xp >= threshold:
            level = i
    return level

def progress_bar(current, total, length=12):
    if total == 0:
        return "░" * length
    filled = round(length * current / total)
    return "▓" * filled + "░" * (length - filled)

def xp_bar(xp, length=12):
    pct = min(xp / MAX_XP, 1.0)
    filled = round(length * pct)
    return "▓" * filled + "░" * (length - filled)

def get_all_tasks_for_phase(phase_idx):
    tasks = []
    for zone in PHASES[phase_idx]["zones"]:
        tasks.extend(zone["tasks"])
    return tasks

def get_daily_tasks(data):
    today = today_str()
    phase = data.get("phase", 0)
    tasks = []
    for zone in PHASES[phase]["zones"]:
        for task in zone["tasks"]:
            if task["freq"] == "daily":
                done = (data["done"].get(today) or {}).get(task["id"], False)
                tasks.append({**task, "done": done, "zone": zone["title"]})
            elif task["freq"] == "once" and not data["once_done"].get(task["id"]):
                done = (data["done"].get(today) or {}).get(task["id"], False)
                tasks.append({**task, "done": done, "zone": zone["title"]})
    return tasks

def count_today_done(data):
    today = today_str()
    tasks = get_daily_tasks(data)
    done = sum(1 for t in tasks if t["done"])
    return done, len(tasks)

def build_today_keyboard(data):
    tasks = get_daily_tasks(data)
    keyboard = []
    prev_zone = None
    for task in tasks:
        if task["zone"] != prev_zone:
            keyboard.append([InlineKeyboardButton(f"— {task['zone']} —", callback_data="noop")])
            prev_zone = task["zone"]
        check = "✅" if task["done"] else "⬜"
        keyboard.append([InlineKeyboardButton(
            f"{check} {task['name']}  +{task['xp']} XP",
            callback_data=f"task_{task['id']}"
        )])
    keyboard.append([InlineKeyboardButton("📊 Статистика", callback_data="stats")])
    return InlineKeyboardMarkup(keyboard)

def build_header(data):
    xp = data["xp"]
    level = get_level(xp)
    level_name = LEVELS[level][1]
    streak = data["streak"]
    done, total = count_today_done(data)

    day_bar = progress_bar(done, total, 10)
    total_bar = xp_bar(xp, 10)

    return (
        f"🎮 Уровень {level + 1}: {level_name}\n"
        f"⚡ XP: {xp}  {total_bar}  {round(xp / MAX_XP * 100)}%\n"
        f"🔥 Серия: {streak} дн.\n\n"
        f"Сегодня: {done}/{total}  {day_bar}\n"
    )

def build_stats_text(data):
    xp = data["xp"]
    level = get_level(xp)
    level_name = LEVELS[level][1]
    streak = data["streak"]
    total_days = data["total_days"]
    phase = data.get("phase", 0)
    phase_name = PHASES[phase]["name"]
    done, total = count_today_done(data)
    done_once = len(data.get("once_done", {}))
    next_level_xp = LEVELS[level + 1][0] if level + 1 < len(LEVELS) else LEVELS[level][0]
    xp_to_next = next_level_xp - xp

    day_bar = progress_bar(done, total, 12)
    total_bar = xp_bar(xp, 12)

    return (
        f"📊 Прогресс Артёма\n"
        f"{'─'*22}\n"
        f"🎮 Уровень {level + 1}: {level_name}\n"
        f"⚡ XP: {xp} / {MAX_XP}\n"
        f"{total_bar}  {round(xp / MAX_XP * 100)}%\n"
        f"До след. уровня: {xp_to_next} XP\n\n"
        f"🔥 Серия: {streak} дн.\n"
        f"📅 Всего дней: {total_days}\n"
        f"✅ Разовых задач: {done_once}\n\n"
        f"Сегодня: {done}/{total}\n"
        f"{day_bar}\n\n"
        f"📌 Фаза: {phase_name}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    chat_id = update.effective_chat.id
    data["chat_id"] = chat_id
    today = today_str()
    if data["last_day"] != today:
        yesterday = (datetime.now(TIMEZONE) - timedelta(days=1)).strftime("%Y-%m-%d")
        data["streak"] = data["streak"] + 1 if data["last_day"] == yesterday else 1
        data["last_day"] = today
        data["total_days"] += 1
    save_data(data)
    await update.message.reply_text(
        build_header(data) + "\nЗадачи на сегодня:",
        reply_markup=build_today_keyboard(data)
    )

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    await update.message.reply_text(build_stats_text(data))

async def phase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    keyboard = []
    for i, phase in enumerate(PHASES):
        mark = "✅ " if i == data.get("phase", 0) else ""
        keyboard.append([InlineKeyboardButton(f"{mark}{phase['name']}", callback_data=f"phase_{i}")])
    await update.message.reply_text("Выбери текущую фазу:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "noop":
        return
    data = load_data()
    today = today_str()

    if query.data == "stats":
        await query.edit_message_text(
            build_stats_text(data),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("← Назад", callback_data="back")
            ]])
        )
        return

    if query.data == "back":
        await query.edit_message_text(
            build_header(data) + "\nЗадачи на сегодня:",
            reply_markup=build_today_keyboard(data)
        )
        return

    if query.data.startswith("phase_"):
        phase_idx = int(query.data.split("_")[1])
        data["phase"] = phase_idx
        save_data(data)
        await query.edit_message_text(
            f"✅ Фаза изменена: {PHASES[phase_idx]['name']}\n\nНапиши /today"
        )
        return

    if query.data.startswith("task_"):
        task_id = query.data[5:]
        if today not in data["done"]:
            data["done"][today] = {}
        all_tasks = [t for ph in PHASES for z in ph["zones"] for t in z["tasks"]]
        task = next((t for t in all_tasks if t["id"] == task_id), None)
        if not task:
            return

        was_done = data["done"][today].get(task_id, False)
        if was_done:
            data["done"][today][task_id] = False
            data["xp"] = max(0, data["xp"] - task["xp"])
            if task["freq"] == "once" and task_id in data.get("once_done", {}):
                del data["once_done"][task_id]
        else:
            data["done"][today][task_id] = True
            if task["freq"] == "once":
                data["once_done"][task_id] = True
            data["xp"] += task["xp"]

        save_data(data)
        done, total = count_today_done(data)
        xp = data["xp"]
        level = get_level(xp)
        day_bar = progress_bar(done, total, 10)
        total_bar = xp_bar(xp, 10)

        if not was_done:
            motivation = random.choice(MOTIVATIONS)
            msg = (
                f"✅ +{task['xp']} XP!\n\n"
                f"{motivation}\n\n"
                f"🎮 Уровень {level + 1}  ⚡ {xp} XP\n"
                f"{total_bar}  {round(xp / MAX_XP * 100)}%\n\n"
                f"Сегодня: {done}/{total}  {day_bar}"
            )
        else:
            msg = (
                f"↩️ -{task['xp']} XP\n\n"
                f"🎮 Уровень {level + 1}  ⚡ {xp} XP\n"
                f"Сегодня: {done}/{total}  {day_bar}"
            )

        await query.edit_message_text(msg, reply_markup=build_today_keyboard(data))

async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    chat_id = data.get("chat_id")
    if not chat_id:
        return
    today = today_str()
    if data["last_day"] != today:
        yesterday = (datetime.now(TIMEZONE) - timedelta(days=1)).strftime("%Y-%m-%d")
        data["streak"] = data["streak"] + 1 if data["last_day"] == yesterday else 1
        data["last_day"] = today
        data["total_days"] += 1
        save_data(data)
    tasks = get_daily_tasks(data)
    xp = data["xp"]
    level = get_level(xp)
    total_bar = xp_bar(xp, 10)
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"☀️ Доброе утро, Артём!\n\n"
            f"🎮 Уровень {level + 1}  ⚡ {xp} XP\n"
            f"{total_bar}  {round(xp / MAX_XP * 100)}%\n"
            f"🔥 Серия: {data['streak']} дн.\n\n"
            f"Задач на сегодня: {len(tasks)}\nВперёд!"
        ),
        reply_markup=build_today_keyboard(data)
    )

def main():
    app = Application.builder().token(TOKEN).job_queue(JobQueue()).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("phase", phase_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.job_queue.run_daily(
        send_morning_reminder,
        time=time(hour=9, minute=0, tzinfo=TIMEZONE),
        name="morning_reminder"
    )
    logger.info("Lumora Bot запущен...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
