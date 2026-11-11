# -*- coding: utf-8 -*-
import logging
import os
import random
import sqlite3
import threading
import http.server
import urllib.parse
import urllib.request
import datetime
import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonCommands
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# ============================================================
#  НАСТРОЙКИ
# ============================================================
BOT_TOKEN = "7303209127:AAGHrwgFYbmrh3LFW7mxZl63Yefs_ITYbVQ" # Токен Aviator-бота
ADMIN_ID  = "6109042131"

DAILY_LIMIT = 5
WEB_PORT    = int(os.getenv("PORT", "5000"))

# Твоя ссылка для Aviator (проверь, правильная ли она у тебя)
PARTNER_URL = "https://r1wagwk.com/v3/aviator-fire?p=a0d1&sub1={uid}"

# ============================================================

BASE_DIR = os.getenv("DATA_DIR") or os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "DataBase.db")

LANG = {
    'ru': {
        'welcome': "✈️ <b>ДОСТУП К СЕКРЕТНОМУ АЛГОРИТМУ ПОЛУЧЕН</b> ✈️\n\nПриветствуем в <b>AVIATOR AI PREDICTOR</b>!\n\n😤 Устал смотреть, как самолет улетает на x1.01? Пора забирать свое.\n\n🧠 Наша нейросеть сканирует игру <b>Aviator</b> и вычисляет точный коэффициент для кэшаута с точностью <b>до 90%</b>.\n\n🚀 <b>Начни зарабатывать прямо сейчас!</b> 👇",
        'btn_reg': "💳 Регистрация", 'btn_instr': "📖 Инструкция", 'btn_sign': "🔮 Выдать сигнал", 'btn_lang': "🌐 Язык", 'btn_ref': "👥 Конкурс и Рефералы", 'btn_support': "🆘 Поддержка",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Язык изменен на Русский 🇷🇺",
        'need_reg': "⚠️ <b>ДОСТУП ЗАБЛОКИРОВАН!</b>\n\nАлгоритм ИИ требует привязки аккаунта 1win.\n\n👇 Зарегистрируйся в 1 клик:",
        'regged': "✅ <b>УСПЕХ!</b> Аккаунт привязан. Нейросеть активирована. Жми «Выдать сигнал»! 🚀",
        'choose_risk': "⚙️ <b>Настройка риска</b>\n\nВыбери уровень риска для следующего полета:",
        'btn_risk_1': "🟢 Низкий (до x1.5)", 'btn_risk_2': "🟡 Средний (до x2.5)", 'btn_risk_3': "🔴 Высокий (x3.0+)",
        'btn_main': "⬅️ Главное меню",
        'signal_title': "✈️ <b>Анализ завершен!</b>\nУровень риска: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>Целевой коэффициент для кэшаута:</b> <code>x{target}</code>\n\n{left}🔥 <i>Удачи! Не жадничай, забирай вовремя.</i>",
        'left_signals': "💡 <i>Осталось сигналов на сегодня: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>ДНЕВНОЙ ЛИМИТ ИСЧЕРПАН!</b>\n\nВы использовали все {limit} сигналов на сегодня.\n\n👇 <b>Хотите больше?</b> Пригласите друга по кнопке «👥 Конкурс и Рефералы»!",
        'instr_text': "📖 <b>КАК НАЧАТЬ ЗАРАБАТЫВАТЬ:</b>\n\n1️⃣ <b>Регистрация:</b> <a href='{url}'>КЛИКНИ СЮДА</a>\n2️⃣ <b>Депозит:</b> Пополни баланс.\n3️⃣ <b>Игра:</b> Перейди в раздел <b>Aviator</b>.\n4️⃣ <b>Настройка:</b> Выстави авто-кэшаут по сигналу.\n5️⃣ <b>Действие:</b> Запускай раунд и жди нужной иксы.",
        'admin_panel': "⚙️ Админ панель. Команда /top - таблица лидеров.", 'not_admin': "❌ У вас нет прав администратора.",
        'support_text': "🆘 <b>Служба поддержки</b>\n\n👉 <a href='tg://user?id={admin_id}'>Написать администратору</a>",
        'ref_title': "🏆 <b>КОНКУРС С ПРИЗОВЫМ ФОНДОМ</b> 🏆\n\nПриглашай друзей и зарабатывай билеты! <b>1 зарегистрированный друг = 1 билет.</b>\n\n🥇 <b>1 место:</b> $100\n🥈 <b>2 место:</b> $50\n🥉 <b>3 место:</b> $20\n\n📊 Твои билеты: <b>{count}</b>\n\n🔗 Твоя ссылка:\n<code>{link}</code>",
        'ref_notify': "🎉 По твоей ссылке зарегистрировался друг! Ты получил +1 билет. Всего: <b>{count}</b>.",
        'ref_success': "🔥 <b>Ты пригласил 3 друзей!</b> Твой доступ открыт навсегда!"
    },
    'en': {
        'welcome': "✈️ <b>SECRET ALGORITHM ACCESS GRANTED</b> ✈️\n\nWelcome to <b>AVIATOR AI PREDICTOR</b>!\n\n😤 Tired of watching the plane fly away at x1.01? It's time to take yours.\n\n🧠 Our neural network scans Aviator and calculates the exact cashout multiplier with <b>up to 90% accuracy</b>.\n\n🚀 <b>Start earning right now!</b> 👇",
        'btn_reg': "💳 Register", 'btn_instr': "📖 Instruction", 'btn_sign': "🔮 Get Signal", 'btn_lang': "🌐 Language", 'btn_ref': "👥 Contest & Refs", 'btn_support': "🆘 Support",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Language changed to English 🇬🇧",
        'need_reg': "⚠️ <b>ACCESS BLOCKED!</b>\n\nRegister below to unlock:",
        'regged': "✅ <b>SUCCESS!</b> Account linked. Click 'Get Signal'! 🚀",
        'choose_risk': "⚙️ <b>Risk Configuration</b>\n\nChoose risk level:",
        'btn_risk_1': "🟢 Low (up to x1.5)", 'btn_risk_2': "🟡 Medium (up to x2.5)", 'btn_risk_3': "🔴 High (x3.0+)",
        'btn_main': "⬅️ Main Menu",
        'signal_title': "✈️ <b>Analysis Complete!</b>\nRisk level: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>Target cashout multiplier:</b> <code>x{target}</code>\n\n{left}🔥 <i>Good luck!</i>",
        'left_signals': "💡 <i>Signals left today: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>DAILY LIMIT REACHED!</b>\n\nInvite a friend via '👥 Contest & Refs' to get more!",
        'instr_text': "📖 <b>HOW TO START:</b>\n\n1️⃣ <b>Register:</b> <a href='{url}'>CLICK HERE</a>\n2️⃣ <b>Deposit:</b> Top up.\n3️⃣ <b>Game:</b> Go to <b>Aviator</b>.\n4️⃣ <b>Setup:</b> Set auto-cashout by signal.\n5️⃣ <b>Action:</b> Start the round.",
        'admin_panel': "⚙️ Admin panel.", 'not_admin': "❌ No admin rights.",
        'support_text': "🆘 <b>Support</b>\n\n👉 <a href='tg://user?id={admin_id}'>Message Admin</a>",
        'ref_title': "🏆 <b>PRIZE POOL CONTEST</b> 🏆\n\nInvite friends! <b>1 friend = 1 ticket.</b>\n\n🥇 <b>1st:</b> $100\n🥈 <b>2nd:</b> $50\n🥉 <b>3rd:</b> $20\n\n📊 Tickets: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Friend registered! +1 ticket. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 friends invited!</b> Access open forever!"
    }
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("aviator")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user (
                user_id     INTEGER PRIMARY KEY,
                postback_id TEXT,
                language    TEXT DEFAULT 'ru',
                referrer_id INTEGER,
                daily_signals INTEGER DEFAULT 0,
                last_signal_date TEXT
            )
        """)
        conn.commit()
        
        columns = [
            ("language", "TEXT DEFAULT 'ru'"),
            ("referrer_id", "INTEGER"),
            ("daily_signals", "INTEGER DEFAULT 0"),
            ("last_signal_date", "TEXT")
        ]
        for col, typ in columns:
            try:
                conn.execute(f"ALTER TABLE user ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError:
                pass

def get_user(uid: int):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("""
            SELECT postback_id, language, referrer_id, daily_signals, last_signal_date 
            FROM user WHERE user_id = ?
        """, (uid,)).fetchone()
        
        if row:
            lang = row[1] if row[1] in LANG else 'ru'
            ref_count = conn.execute(
                "SELECT COUNT(*) FROM user WHERE referrer_id = ? AND postback_id IS NOT NULL", 
                (uid,)
            ).fetchone()[0]
            return {
                "postback_id": row[0], "lang": lang, "referrer_id": row[2], 
                "ref_count": ref_count, "daily_signals": row[3] or 0, "last_signal_date": row[4]
            }
    return None

bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True)
)
dp = Dispatcher(storage=MemoryStorage())

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"), InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")]
    ])

def main_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_reg'], callback_data="reg")],
        [InlineKeyboardButton(text=LANG[lang]['btn_instr'], callback_data="instr")],
        [InlineKeyboardButton(text=LANG[lang]['btn_sign'], callback_data="sign")],
        [InlineKeyboardButton(text=LANG[lang]['btn_ref'], callback_data="ref_menu")],
        [InlineKeyboardButton(text=LANG[lang]['btn_support'], callback_data="support")],
        [InlineKeyboardButton(text=LANG[lang]['btn_lang'], callback_data="lang_menu")]
    ])

def reg_kb(uid, lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_reg'], url=PARTNER_URL.format(uid=uid))]
    ])

def risk_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_1'], callback_data="gen_risk_low")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_2'], callback_data="gen_risk_med")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_3'], callback_data="gen_risk_high")],
        [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]
    ])

def sign_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_sign'], callback_data="sign")],
        [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]
    ])

def generate_aviator_signal(lang, risk_level="med", signals_left=0):
    if risk_level == "low":
        target = round(random.uniform(1.20, 1.60), 2)
        risk_name = LANG[lang]['btn_risk_1'].split(' ')[1]
        graphic = "📈  🛫\n     🛫\n          🛫"
    elif risk_level == "high":
        target = round(random.uniform(2.80, 7.50), 2)
        risk_name = LANG[lang]['btn_risk_3'].split(' ')[1]
        graphic = "📈  🛫\n          🛫\n               🛫\n                    🛫"
    else:
        target = round(random.uniform(1.80, 2.50), 2)
        risk_name = LANG[lang]['btn_risk_2'].split(' ')[1]
        graphic = "📈  🛫\n     🛫\n          🛫\n               🛫"
        
    title = LANG[lang]['signal_title'].format(risk_name=risk_name)
    left_text = LANG[lang]['left_signals'].format(left=signals_left) if signals_left > 0 else ""
    
    hint = LANG[lang]['signal_hint'].format(target=target, left=left_text)
    return f"{title}<code>{graphic}</code>\n{hint}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    uid = message.from_user.id
    args = command.args
    referrer_id = None
    if args and args.isdigit():
        referrer_id = int(args)
        if referrer_id == uid: referrer_id = None
            
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO user (user_id) VALUES (?)", (uid,))
        if referrer_id:
            conn.execute("UPDATE user SET referrer_id = ? WHERE user_id = ? AND referrer_id IS NULL", (referrer_id, uid))
        conn.commit()
    
    await message.answer(LANG['ru']['choose_lang'], reply_markup=get_lang_kb())

@dp.callback_query(F.data == "lang_menu")
async def cb_lang_menu(call: types.CallbackQuery):
    await call.message.edit_text(LANG['ru']['choose_lang'], reply_markup=get_lang_kb())

@dp.callback_query(F.data.startswith("set_lang_"))
async def cb_set_lang(call: types.CallbackQuery):
    new_lang = call.data.split("_")[-1]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE user SET language = ? WHERE user_id = ?", (new_lang, call.from_user.id))
        conn.commit()
    await call.answer(LANG[new_lang]['lang_set'])
    await call.message.edit_text(text=LANG[new_lang]['welcome'], reply_markup=main_menu(new_lang))

@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user['lang'] if user else 'ru'
    await call.message.edit_text(text=LANG[lang]['welcome'], reply_markup=main_menu(lang))
    await call.answer()

@dp.callback_query(F.data == "support")
async def cb_support(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user['lang'] if user else 'ru'
    text = LANG[lang]['support_text'].format(admin_id=ADMIN_ID)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]])
    await call.message.edit_text(text=text, reply_markup=kb, disable_web_page_preview=True)
    await call.answer()

@dp.callback_query(F.data == "ref_menu")
async def cb_ref_menu(call: types.CallbackQuery):
    uid = call.from_user.id
    user = get_user(uid)
    lang = user['lang'] if user else 'ru'
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={uid}"
    text = LANG[lang]['ref_title'].format(link=ref_link, count=user['ref_count'])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]])
    await call.message.edit_text(text=text, reply_markup=kb, disable_web_page_preview=True)
    await call.answer()

@dp.callback_query(F.data == "instr")
async def cb_instr(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user['lang'] if user else 'ru'
    text = LANG[lang]['instr_text'].format(url=PARTNER_URL.format(uid=call.from_user.id))
    await call.message.answer(text)
    await call.answer()

@dp.callback_query(F.data == "reg")
async def cb_reg(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user['lang'] if user else 'ru'
    await call.message.answer(LANG[lang]['need_reg'], reply_markup=reg_kb(call.from_user.id, lang))
    await call.answer()

@dp.callback_query(F.data == "sign")
async def cb_sign(call: types.CallbackQuery):
    uid = call.from_user.id
    user = get_user(uid)
    
    has_access = user and (user['postback_id'] or user['ref_count'] >= 3)
    if not has_access:
        lang = user['lang'] if user else 'ru'
        await call.message.answer(LANG[lang]['need_reg'], reply_markup=reg_kb(uid, lang))
        await call.answer()
        return
    
    lang = user['lang']
    await call.message.edit_text(text=LANG[lang]['choose_risk'], reply_markup=risk_menu(lang))
    await call.answer()

@dp.callback_query(F.data.startswith("gen_risk_"))
async def cb_gen_risk(call: types.CallbackQuery):
    uid = call.from_user.id
    user = get_user(uid)
    lang = user['lang'] if user else 'ru'
    
    today = datetime.date.today().isoformat()
    daily_signals = 0 if user['last_signal_date'] != today else user['daily_signals']
        
    if daily_signals >= DAILY_LIMIT:
        await call.answer("⚠️ Лимит на сегодня исчерпан!", show_alert=True)
        await call.message.answer(LANG[lang]['limit_msg'].format(limit=DAILY_LIMIT))
        return
        
    daily_signals += 1
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE user SET daily_signals = ?, last_signal_date = ? WHERE user_id = ?", (daily_signals, today, uid))
        conn.commit()
    
    signals_left = DAILY_LIMIT - daily_signals
    risk_level = call.data.split("_")[-1]
    
    signal_text = generate_aviator_signal(lang, risk_level, signals_left)
    
    await call.message.edit_text(text=signal_text, reply_markup=sign_kb(lang))
    await call.answer()

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_ID): return
    await message.answer("⚙️ Админ панель. /top - лидеры")

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_ID): return
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT u1.user_id, COUNT(u2.user_id) as ref_count FROM user u1
            JOIN user u2 ON u1.user_id = u2.referrer_id
            WHERE u2.postback_id IS NOT NULL GROUP BY u1.user_id ORDER BY ref_count DESC LIMIT 10
        """).fetchall()

    if not rows:
        await message.answer("Нет рефералов.")
        return

    text = "🏆 <b>ТОП-10</b>\n\n"
    for i, (uid, count) in enumerate(rows, 1):
        text += f"{i}. ID: <code>{uid}</code> — <b>{count} билетов</b>\n"
    await message.answer(text)

# ============================================================
# ВСТРОЕННЫЙ ВЕБ-СЕРВЕР
# ============================================================
class PostbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # 1. Проверка здоровья
        if parsed.path == '/health' or parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
            return

        # 2. Постбек
        if parsed.path == '/postback':
            qs = urllib.parse.parse_qs(parsed.query)
            sub1 = qs.get('sub1', [''])[0].strip()
            subid = qs.get('subid', [''])[0].strip()

            if not sub1 or not subid:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"missing params")
                return
            try:
                uid = int(sub1)
            except ValueError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"bad sub1")
                return

            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "INSERT INTO user (user_id, postback_id) VALUES (?, ?) "
                    "ON CONFLICT(user_id) DO UPDATE SET postback_id = excluded.postback_id",
                    (uid, subid),
                )
                conn.commit()

            user = get_user(uid)
            lang = user['lang'] if user else 'ru'
            
            text = LANG[lang]['regged']
            url = (
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                f"?chat_id={uid}&text={urllib.parse.quote(text)}&parse_mode=HTML"
            )
            try:
                urllib.request.urlopen(url, timeout=10)
            except Exception as e:
                log.error("telegram send failed: %s", e)

            if user and user.get('referrer_id'):
                ref_id = user['referrer_id']
                ref_user = get_user(ref_id)
                if ref_user:
                    ref_lang = ref_user['lang']
                    ref_count = ref_user['ref_count']
                    if ref_count == 3:
                        ref_text = LANG[ref_lang]['ref_success']
                    else:
                        ref_text = LANG[ref_lang]['ref_notify'].format(count=ref_count)
                        
                    ref_url = (
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        f"?chat_id={ref_id}&text={urllib.parse.quote(ref_text)}&parse_mode=HTML"
                    )
                    try:
                        urllib.request.urlopen(ref_url, timeout=10)
                    except Exception as e:
                        log.error("ref notify failed: %s", e)

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"sub1={sub1}; subid={subid}; OK".encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass

def run_web():
    server = http.server.HTTPServer(('0.0.0.0', WEB_PORT), PostbackHandler)
    log.info("Web server started on port %s", WEB_PORT)
    server.serve_forever()

# ============================================================
# ЗАПУСК
# ============================================================
async def main():
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(text="Start"))
    await dp.start_polling(bot)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_web, daemon=True).start()
    log.info("Bot starting...")
    asyncio.run(main())