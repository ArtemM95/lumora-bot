import logging
import httpx
import json
import os
import random
import asyncio
from datetime import datetime, timedelta
import pytz

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN")
TIMEZONE = pytz.timezone("Europe/Belgrade")
DATA_FILE = os.path.join(os.path.expanduser("~"), "lumora_progress.json")

MOTIVATIONS = [
    "Огонь! Так и строятся империи 🔥",
    "Каждый шаг — кирпич в фундаменте Lumora 🏗",
    "Артём в деле. Клиенты ещё не знают что их ждёт 😎",
    "XP накапливается. Уровень растёт. Продолжай 💪",
    "Сделано — значит существует. Молодец 👊",
    "Вот так выглядит путь к международному агентству ✈️",
    "Маленький шаг сегодня — большой результат через 90 дней 📈",
    "Серьёзные люди делают серьёзные вещи каждый день 🎯",
    "Lumora строится прямо сейчас 🚀",
    "Конкуренты отдыхают. Ты работаешь 😏",
    "Ещё один шаг к первому зарубежному клиенту 🌍",
    "Так работает дисциплина. Тихо, но мощно ⚡️",
    "Продюсер с таким темпом точно выйдет на международный рынок 🎬",
    "Хорошо сделано — это тоже часть бренда Lumora ✨",
    "Каждое выполненное задание — инвестиция в себя 💡",
    "Артём Малыгин. Уровень растёт. История пишется 📖",
    "Это и есть настоящая работа — по одному шагу 🪜",
    "Сделал — отметил — двигаешься дальше ⚙️",
    "Будущий основатель международного агентства не пропускает задачи 🏆",
    "Кто-то мечтает. Ты делаешь 💎",
    "Плюс к XP, плюс к опыту, плюс к результату 📊",
    "Ещё один день в плюсе. Серия продолжается 🔗",
    "Lumora — это то что ты строишь прямо сейчас 🌟",
    "Хорошая работа заслуживает XP 👏",
    "Через 30 дней ты не узнаешь свои результаты 🎯",
]

PHASES = [
    {
        "name": "Месяц 1 — база",
        "zones": [
            {
                "title": "Каждый день",
                "tasks": [
                    {"id": "dm1", "name": "10 личных DM в LinkedIn", "xp": 25, "freq": "daily"},
                    {"id": "en1", "name": "30 мин английского", "xp": 10, "freq": "daily"},
                    {"id": "ct1", "name": "Пост или комментарии", "xp": 15, "freq": "daily"},
                    {"id": "uw1", "name": "3 заявки на Upwork", "xp": 20, "freq": "daily"},
                    {"id": "in1", "name": "Инсайт дня", "xp": 10, "freq": "daily"},
                ]
            },
            {
                "title": "Разовые цели",
                "tasks": [
                    {"id": "pf1", "name": "AI demo-ролик 2-3 мин", "xp": 50, "freq": "once"},
                    {"id": "pf2", "name": "Кейс на английском", "xp": 30, "freq": "once"},
                    {"id": "uw2", "name": "Профиль на Upwork", "xp": 25, "freq": "once"},
                    {"id": "ag1", "name": "Партнёрский pitch", "xp": 40, "freq": "once"},
                    {"id": "ct2", "name": "Первый платный проект", "xp": 100, "freq": "once"},
                    {"id": "rl1", "name": "Открыть Wise или Payoneer", "xp": 30, "freq": "once"},
                    {"id": "rl2", "name": "Доход 1500+ USD x 2 мес", "xp": 100, "freq": "once"},
                ]
            },
        ]
    },
    {
        "name": "Месяц 2 — контракты",
        "zones": [
            {
                "title": "Каждый день",
                "tasks": [
                    {"id": "dm2", "name": "10 DM агентствам и клиентам", "xp": 25, "freq": "daily"},
                    {"id": "en2", "name": "30 мин английского", "xp": 10, "freq": "daily"},
                    {"id": "ct3", "name": "Пост или BTS-видео", "xp": 15, "freq": "daily"},
                    {"id": "uw3", "name": "3 заявки на Upwork", "xp": 20, "freq": "daily"},
                    {"id": "in2", "name": "Инсайт дня", "xp": 10, "freq": "daily"},
                ]
            },
            {
                "title": "Разовые цели",
                "tasks": [
                    {"id": "ag2", "name": "Закрыть 2й платный проект", "xp": 80, "freq": "once"},
                    {"id": "rv1", "name": "Получить 2 отзыва на EN", "xp": 50, "freq": "once"},
                    {"id": "rt1", "name": "Первый monthly retainer", "xp": 100, "freq": "once"},
                    {"id": "pk1", "name": "3 пакета услуг с ценами", "xp": 35, "freq": "once"},
                ]
            },
        ]
    },
    {
        "name": "Месяц 3 — система",
        "zones": [
            {
                "title": "Каждый день",
                "tasks": [
                    {"id": "dm3", "name": "10 DM целевым клиентам", "xp": 25, "freq": "daily"},
                    {"id": "en3", "name": "30 мин английского", "xp": 10, "freq": "daily"},
                    {"id": "ct4", "name": "Контент или нетворкинг", "xp": 15, "freq": "daily"},
                    {"id": "an1", "name": "Конверсия DM за день", "xp": 15, "freq": "daily"},
                    {"id": "in3", "name": "Инсайт дня", "xp": 10, "freq": "daily"},
                ]
            },
            {
                "title": "Разовые цели",
                "tasks": [
                    {"id": "sr1", "name": "Регистрация ИП в Сербии", "xp": 50, "freq": "once"},
                    {"id": "rl3", "name": "Переезд семьи в Сербию", "xp": 200, "freq": "once"},
                    {"id": "cl1", "name": "3 постоянных клиента", "xp": 150, "freq": "once"},
                    {"id": "rv2", "name": "5 отзывов на LinkedIn", "xp": 75, "freq": "once"},
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

def progress_bar(current, total, length=10):
    if total == 0:
        return "░" * length
    filled = round(length * current / total)
    return "▓" * filled + "░" * (length - filled)

def xp_bar(xp, length=10):
    pct = min(xp / MAX_XP, 1.0)
    filled = round(length * pct)
    return "▓" * filled + "░" * (length - filled)

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
    phase = data.get("phase", 0)
    all_tasks = []
    for zone in PHASES[phase]["zones"]:
        for task in zone["tasks"]:
            if task["freq"] == "daily":
                all_tasks.append(task)
            elif task["freq"] == "once":
                done_today = (data["done"].get(today) or {}).get(task["id"], False)
                was_done_before = data["once_done"].get(task["id"]) and not done_today
                if not was_done_before:
                    all_tasks.append(task)
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if (data["done"].get(today) or {}).get(t["id"], False))
    return done, total

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
        f"Прогресс Артёма\n"
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

def update_streak(data):
    today = today_str()
    if data["last_day"] != today:
        yesterday = (datetime.now(TIMEZONE) - timedelta(days=1)).strftime("%Y-%m-%d")
        data["streak"] = data["streak"] + 1 if data["last_day"] == yesterday else 1
        data["last_day"] = today
        data["total_days"] += 1
    return data

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    data["chat_id"] = update.effective_chat.id
    data = update_streak(data)
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
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data="back")]])
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
        await query.edit_message_text(f"✅ Фаза изменена: {PHASES[phase_idx]['name']}\n\nНапиши /today")
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

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text(
            "Напиши вопрос после команды. Например:\n/ask как написать холодное DM на английском?"
        )
        return
    thinking_msg = await update.message.reply_text("Думаю... 🤔")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        await thinking_msg.edit_text("API ключ не настроен.")
        return
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 1024,
                    "system": "Ты помощник Артёма Малыгина — основателя видеопродакшн агентства Lumora. Артём переезжает в Сербию и строит международный бизнес в сфере AI video production. Отвечай кратко, по делу, на русском языке. Давай конкретные советы.",
                    "messages": [{"role": "user", "content": question}]
                }
            )
            data = response.json()
            answer = data["content"][0]["text"]
            await thinking_msg.edit_text(answer)
    except Exception as e:
        await thinking_msg.edit_text(f"Ошибка: {str(e)}")

async def morning_reminder(app):
    while True:
        now = datetime.now(TIMEZONE)
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        data = load_data()
        chat_id = data.get("chat_id")
        if chat_id:
            data = update_streak(data)
            save_data(data)
            tasks = get_daily_tasks(data)
            xp = data["xp"]
            level = get_level(xp)
            total_bar = xp_bar(xp, 10)
            try:
                await app.bot.send_message(
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
            except Exception as e:
                logger.error(f"Morning reminder error: {e}")

async def post_init(app):
    asyncio.create_task(morning_reminder(app))

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("phase", phase_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("Lumora Bot запущен...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
