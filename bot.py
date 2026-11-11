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
import json

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonCommands
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# ============================================================
#  НАСТРОЙКИ AVIATOR
# ============================================================
BOT_TOKEN = "9033220269:AAEL5MCxUjxJOIcMUNxjW0kK-kev6hgXeeQ"
ADMIN_ID  = "6109042131"
WEB_PORT  = int(os.getenv("PORT", "5000"))
PARTNER_URL = "https://r1wagwk.com/v3/aviator-fire?p=a0d1&sub1={uid}"

# ============================================================
BASE_DIR = os.getenv("DATA_DIR") or os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "DataBase.db")

LANG = {
    'ru': {
        'welcome': "✈️ <b>ДОСТУП К СЕКРЕТНОМУ АЛГОРИТМУ ПОЛУЧЕН</b> ✈️\n\nПриветствуем в <b>AVIATOR AI PREDICTOR</b>!\n\n😤 Устал смотреть, как самолет улетает на x1.01? Пора забирать свое.\n\n🧠 Наша нейросеть сканирует игру <b>Aviator</b> и вычисляет точный коэффициент для кэшаута с точностью <b>до 90%</b>.",
        'btn_reg': "💳 Регистрация", 'btn_instr': "📖 Инструкция", 'btn_sign': "✈️ Выдать сигнал", 'btn_lang': "🌐 Язык", 'btn_ref': "👥 Конкурс и Рефералы", 'btn_support': "🆘 Поддержка",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Язык изменен на Русский 🇷🇺",
        'need_reg': "⚠️ <b>ДОСТУП ЗАБЛОКИРОВАН!</b>\n\nАлгоритм ИИ требует привязки аккаунта 1win.\n\n👇 Зарегистрируйся в 1 клик:",
        'regged': "✅ <b>УСПЕХ!</b> Аккаунт привязан. Нейросеть активирована. Жми «Выдать сигнал»! 🚀",
        'choose_risk': "⚙️ <b>Настройка риска</b>\n\nВыбери уровень риска для следующего полета:",
        'btn_risk_1': "🟢 Низкий (до x1.5)", 'btn_risk_2': "🟡 Средний (до x2.5)", 'btn_risk_3': "🔴 Высокий (x3.0+)",
        'btn_main': "⬅️ Главное меню",
        'signal_title': "✈️ <b>Анализ завершен!</b>\nУровень риска: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>Целевой коэффициент:</b> <code>x{target}</code>\n\n{left}🔥 <i>Удачи! Не жадничай.</i>",
        'left_signals': "💡 <i>Осталось сигналов: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>ЛИМИТ ИСЧЕРПАН!</b>\n\n👇 Пригласите друга по кнопке «👥 Конкурс и Рефералы»!",
        'instr_text': "📖 <b>КАК ИГРАТЬ:</b>\n\n1️⃣ <b>Регистрация:</b> <a href='{url}'>КЛИКНИ СЮДА</a>\n2️⃣ <b>Депозит.</b>\n3️⃣ <b>Игра:</b> Раздел <b>Aviator</b>.\n4️⃣ <b>Настройка:</b> Авто-кэшаут по сигналу.",
        'admin_panel': "⚙️ <b>АДМИН ПАНЕЛЬ</b>\n\n👑 Статус: <b>GOD MODE</b>\nВыберите действие:",
        'not_admin': "❌ Вы не админ.",
        'support_text': "🆘 <b>Поддержка</b>\n\n👉 <a href='tg://user?id={admin_id}'>Написать админу</a>",
        'ref_title': "🏆 <b>КОНКУРС</b> 🏆\n\n1 друг = 1 билет.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Твои билеты: <b>{count}</b>\n\n🔗 Ссылка:\n<code>{link}</code>",
        'ref_notify': "🎉 Друг зарегистрировался! +1 билет. Всего: <b>{count}</b>.",
        'ref_success': "🔥 <b>Ты пригласил 3 друзей!</b> Доступ открыт навсегда!"
    },
    'en': {
        'welcome': "✈️ <b>SECRET ALGORITHM ACCESS GRANTED</b> ✈️\n\nWelcome to <b>AVIATOR AI PREDICTOR</b>!\n\n🧠 Our neural network calculates the exact cashout multiplier with <b>up to 90% accuracy</b>.",
        'btn_reg': "💳 Register", 'btn_instr': "📖 Instruction", 'btn_sign': "✈️ Get Signal", 'btn_lang': "🌐 Language", 'btn_ref': "👥 Contest & Refs", 'btn_support': "🆘 Support",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Language changed to English 🇬🇧",
        'need_reg': "⚠️ <b>ACCESS BLOCKED!</b>\n\nRegister below to unlock:",
        'regged': "✅ <b>SUCCESS!</b> Click 'Get Signal'! 🚀",
        'choose_risk': "⚙️ <b>Risk Configuration</b>\n\nChoose risk level:",
        'btn_risk_1': "🟢 Low (up to x1.5)", 'btn_risk_2': "🟡 Medium (up to x2.5)", 'btn_risk_3': "🔴 High (x3.0+)",
        'btn_main': "⬅️ Main Menu",
        'signal_title': "✈️ <b>Analysis Complete!</b>\nRisk level: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>Target multiplier:</b> <code>x{target}</code>\n\n{left}🔥 <i>Good luck!</i>",
        'left_signals': "💡 <i>Signals left: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>LIMIT REACHED!</b>\n\nInvite a friend via '👥 Contest & Refs'!",
        'instr_text': "📖 <b>HOW TO START:</b>\n\n1️⃣ <b>Register:</b> <a href='{url}'>CLICK HERE</a>\n2️⃣ <b>Deposit.</b>\n3️⃣ <b>Game:</b> <b>Aviator</b>.",
        'admin_panel': "⚙️ <b>ADMIN PANEL</b>\n\n👑 Status: <b>GOD MODE</b>\nChoose action:",
        'not_admin': "❌ No rights.",
        'support_text': "🆘 <b>Support</b>\n\n👉 <a href='tg://user?id={admin_id}'>Message Admin</a>",
        'ref_title': "🏆 <b>CONTEST</b> 🏆\n\n1 friend = 1 ticket.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Tickets: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Friend registered! +1 ticket. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 friends invited!</b> Access open forever!"
    }
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("aviator")

class AdminState(StatesGroup):
    waiting_for_broadcast = State()

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY, postback_id TEXT, language TEXT DEFAULT 'ru', referrer_id INTEGER, daily_signals INTEGER DEFAULT 0, last_signal_date TEXT)")
        conn.commit()
        for col, typ in [("language", "TEXT DEFAULT 'ru'"), ("referrer_id", "INTEGER"), ("daily_signals", "INTEGER DEFAULT 0"), ("last_signal_date", "TEXT")]:
            try: conn.execute(f"ALTER TABLE user ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError: pass

def get_user(uid: int):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT postback_id, language, referrer_id, daily_signals, last_signal_date FROM user WHERE user_id = ?", (uid,)).fetchone()
        if row:
            lang = row[1] if row[1] in LANG else 'ru'
            ref_count = conn.execute("SELECT COUNT(*) FROM user WHERE referrer_id = ? AND postback_id IS NOT NULL", (uid,)).fetchone()[0]
            return {"user_id": uid, "postback_id": row[0], "lang": lang, "referrer_id": row[2], "ref_count": ref_count, "daily_signals": row[3] or 0, "last_signal_date": row[4]}
    return None

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True))
dp = Dispatcher(storage=MemoryStorage())

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"), InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")]])

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
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_reg'], url=PARTNER_URL.format(uid=uid))]])

def risk_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_1'], callback_data="gen_risk_low")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_2'], callback_data="gen_risk_med")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_3'], callback_data="gen_risk_high")],
        [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]
    ])

def sign_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_sign'], callback_data="sign")], [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])

def generate_aviator_signal(lang, risk_level, signals_left_str):
    if risk_level == "low": target, r_name, g = round(random.uniform(1.2, 1.6), 2), "Low", "📈  🛫\n     🛫"
    elif risk_level == "high": target, r_name, g = round(random.uniform(2.8, 7.5), 2), "High", "📈  🛫\n          🛫\n               🛫"
    else: target, r_name, g = round(random.uniform(1.8, 2.5), 2), "Medium", "📈  🛫\n     🛫\n          🛫"
    title = LANG[lang]['signal_title'].format(risk_name=r_name)
    hint = LANG[lang]['signal_hint'].format(target=target, left=signals_left_str)
    return f"{title}<code>{g}</code>\n{hint}"

def get_fake_win(lang='ru'):
    names = ["Alex", "Max", "Ivan", "Denis", "Artem", "Vlad", "Favour", "Joyce Appiah"]
    name = random.choice(names)
    win = random.randint(500, 65000)
    mult = round(random.uniform(1.2, 9.5), 2)
    if lang == 'ru': return f"🔥 <i>{name} только что забрал {win:,} ₽ в Aviator (x{mult})!</i>"
    else: return f"🔥 <i>{name} just cashed out ${win:,} in Aviator (x{mult})!</i>"

@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    uid = message.from_user.id
    ref = command.args
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO user (user_id) VALUES (?)", (uid,))
        if ref and ref.isdigit() and int(ref) != uid:
            conn.execute("UPDATE user SET referrer_id = ? WHERE user_id = ? AND referrer_id IS NULL", (int(ref), uid))
        conn.commit()
    await message.answer(LANG['ru']['choose_lang'], reply_markup=get_lang_kb())

@dp.callback_query(F.data == "lang_menu")
async def cb_lang_menu(call: types.CallbackQuery): await call.message.edit_text(LANG['ru']['choose_lang'], reply_markup=get_lang_kb())

@dp.callback_query(F.data.startswith("set_lang_"))
async def cb_set_lang(call: types.CallbackQuery):
    lang = call.data.split("_")[-1]
    with sqlite3.connect(DB_PATH) as conn: conn.execute("UPDATE user SET language = ? WHERE user_id = ?", (lang, call.from_user.id)); conn.commit()
    await call.answer(LANG[lang]['lang_set'])
    welcome_text = f"{LANG[lang]['welcome']}\n\n{get_fake_win(lang)}"
    await call.message.edit_text(welcome_text, reply_markup=main_menu(lang))

@dp.callback_query(F.data == "main_menu")
async def cb_main(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    welcome_text = f"{LANG[lang]['welcome']}\n\n{get_fake_win(lang)}"
    await call.message.edit_text(welcome_text, reply_markup=main_menu(lang)); await call.answer()

@dp.callback_query(F.data == "support")
async def cb_sup(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])
    await call.message.edit_text(LANG[lang]['support_text'].format(admin_id=ADMIN_ID), reply_markup=kb, disable_web_page_preview=True); await call.answer()

@dp.callback_query(F.data == "ref_menu")
async def cb_ref(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    b_info = await bot.get_me(); link = f"https://t.me/{b_info.username}?start={call.from_user.id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])
    await call.message.edit_text(LANG[lang]['ref_title'].format(link=link, count=u['ref_count']), reply_markup=kb, disable_web_page_preview=True); await call.answer()

@dp.callback_query(F.data == "instr")
async def cb_instr(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    await call.message.answer(LANG[lang]['instr_text'].format(url=PARTNER_URL.format(uid=call.from_user.id))); await call.answer()

@dp.callback_query(F.data == "reg")
async def cb_reg(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    await call.message.answer(LANG[lang]['need_reg'], reply_markup=reg_kb(call.from_user.id, lang)); await call.answer()

@dp.callback_query(F.data == "sign")
async def cb_sign(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    if not u or not (u['postback_id'] or u['ref_count'] >= 3):
        lang = u['lang'] if u else 'ru'
        await call.message.answer(LANG[lang]['need_reg'], reply_markup=reg_kb(call.from_user.id, lang)); await call.answer(); return
    await call.message.edit_text(LANG[u['lang']]['choose_risk'], reply_markup=risk_menu(u['lang'])); await call.answer()

@dp.callback_query(F.data.startswith("gen_risk_"))
async def cb_gen(call: types.CallbackQuery):
    uid = call.from_user.id
    u = get_user(uid); lang = u['lang'] if u else 'ru'
    is_admin = (str(uid) == str(ADMIN_ID))
    today = datetime.date.today().isoformat()
    daily = 0 if u['last_signal_date'] != today else u['daily_signals']
    
    if not is_admin:
        if daily >= 5:
            await call.answer("⚠️ Лимит исчерпан!", show_alert=True)
            await call.message.answer(LANG[lang]['limit_msg']); return
        daily += 1
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE user SET daily_signals = ?, last_signal_date = ? WHERE user_id = ?", (daily, today, uid)); conn.commit()
        signals_left_str = LANG[lang]['left_signals'].format(left=5 - daily)
    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE user SET last_signal_date = ? WHERE user_id = ?", (today, uid)); conn.commit()
        signals_left_str = "💡 <i>Осталось сигналов: ∞ (God Mode)</i>\n\n"
    
    signal_text = generate_aviator_signal(lang, call.data.split("_")[-1], signals_left_str)
    await call.message.edit_text(text=signal_text, reply_markup=sign_kb(lang)); await call.answer()

# ============================================================
# АДМИН ПАНЕЛЬ
# ============================================================
@dp.message(Command("admin"))
async def cmd_adm(msg: types.Message):
    if str(msg.from_user.id) != str(ADMIN_ID): return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Сделать рассылку", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="main_menu")]
    ])
    await msg.answer("⚙️ <b>АДМИН ПАНЕЛЬ AVIATOR</b>\n\nВыберите действие:", reply_markup=kb)

@dp.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: types.CallbackQuery):
    if str(call.from_user.id) != str(ADMIN_ID): return
    with sqlite3.connect(DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM user").fetchone()[0]
        regs = conn.execute("SELECT COUNT(*) FROM user WHERE postback_id IS NOT NULL").fetchone()[0]
    
    text = f"📊 <b>Статистика бота:</b>\n\n👥 Всего юзеров: <b>{total}</b>\n✅ Регистраций (1win): <b>{regs}</b>"
    await call.message.edit_text(text, reply_markup=call.message.reply_markup)
    await call.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(call: types.CallbackQuery, state: FSMContext):
    if str(call.from_user.id) != str(ADMIN_ID): return
    await call.message.edit_text("📢 Отправьте текст для рассылки всем пользователям (можно с HTML-тегами):")
    await state.set_state(AdminState.waiting_for_broadcast)
    await call.answer()

@dp.message(AdminState.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    if str(message.from_user.id) != str(ADMIN_ID): return
    await state.clear()
    
    text = message.text
    with sqlite3.connect(DB_PATH) as conn:
        users = conn.execute("SELECT user_id FROM user").fetchall()
        
    await message.answer(f"🚀 Начинаю рассылку для {len(users)} чел...")
    
    success = 0
    for (uid,) in users:
        try:
            await bot.send_message(uid, text, parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.05) # Защита от бана Telegram
        except:
            pass
            
    await message.answer(f"✅ Рассылка завершена!\nУспешно доставлено: {success}")

# ============================================================
# ВСТРОЕННЫЙ ВЕБ-СЕРВЕР ДЛЯ ПОСТБЕКОВ И API
# ============================================================
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == '/health': self.send_response(200); self.end_headers(); self.wfile.write(b'{"ok": true}'); return
        
        if p.path == '/api/stats':
            with sqlite3.connect(DB_PATH) as conn:
                total = conn.execute("SELECT COUNT(*) FROM user").fetchone()[0]
                regs = conn.execute("SELECT COUNT(*) FROM user WHERE postback_id IS NOT NULL").fetchone()[0]
                recent = conn.execute("SELECT user_id, postback_id FROM user WHERE postback_id IS NOT NULL ORDER BY rowid DESC LIMIT 10").fetchall()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"total": total, "regs": regs, "recent": recent}).encode())
            return

        if p.path == '/postback':
            q = urllib.parse.parse_qs(p.query); s1, s2 = q.get('sub1',[''])[0], q.get('subid',[''])[0]
            if not s1 or not s2: self.send_response(400); self.end_headers(); return
            try: uid = int(s1)
            except: self.send_response(400); self.end_headers(); return
            with sqlite3.connect(DB_PATH) as conn: conn.execute("INSERT INTO user (user_id, postback_id) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET postback_id = excluded.postback_id", (uid, s2)); conn.commit()
            u = get_user(uid); lang = u['lang'] if u else 'ru'
            try: urllib.request.urlopen(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={uid}&text={urllib.parse.quote(LANG[lang]['regged'])}&parse_mode=HTML", timeout=5)
            except: pass
            if u and u.get('referrer_id'):
                r_u = get_user(u['referrer_id'])
                if r_u:
                    t = LANG[r_u['lang']]['ref_success'] if r_u['ref_count'] >= 3 else LANG[r_u['lang']]['ref_notify'].format(count=r_u['ref_count'])
                    try: urllib.request.urlopen(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={r_u['user_id']}&text={urllib.parse.quote(t)}&parse_mode=HTML", timeout=5)
                    except: pass
            self.send_response(200); self.end_headers(); self.wfile.write(f"sub1={s1}; subid={s2}; OK".encode('utf-8')); return
        self.send_response(404); self.end_headers()

async def main():
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(text="Start"))
    log.info("Bot starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=lambda: http.server.HTTPServer(('0.0.0.0', WEB_PORT), Handler).serve_forever(), daemon=True).start()
    log.info("Web server started on port %s", WEB_PORT)
    asyncio.run(main())