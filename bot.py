# -*- coding: utf-8 -*-
import logging
import os
import random
import sqlite3
import threading
import http.server
import urllib.parse
import datetime
import asyncio

import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonCommands

# ============================================================
#  НАСТРОЙКИ
# ============================================================
BOT_TOKEN = "9033220269:AAEL5MCxUjxJOIcMUNxjW0kK-kev6hgXeeQ"
ADMIN_ID  = "6109042131"

DAILY_LIMIT = 5
WEB_PORT    = int(os.getenv("PORT", "5000"))

# ВАЖНО: Ссылка на игру Aviator Fire с меткой sub1
PARTNER_URL = "https://r1wagwk.com/v3/aviator-fire?p=a0d1&sub1={uid}"

# ============================================================

BASE_DIR = os.getenv("DATA_DIR") or os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "DataBase.db")

# --- СЛОВАРИ ПЕРЕВОДОВ ---
LANG = {
    'ru': {
        'welcome': "✈️ <b>ДОСТУП К СЕКРЕТНОМУ АЛГОРИТМУ ПОЛУЧЕН</b> ✈️\n\nПриветствуем в <b>AVIATOR AI PREDICTOR</b>!\n\n😤 Устал смотреть, как самолет улетает на x1.01, когда ты поставил на x2.00? Пора забирать свое.\n\n🧠 Наша нейросеть в реальном времени сканирует паттерны игры <b>Aviator</b> в 1win и вычисляет точный коэффициент для кэшаута с точностью <b>до 90%</b>.\n\n⚙️ <b>Как это работает?</b>\n1. Ты жмешь кнопку «🔮 Выдать сигнал»\n2. ИИ генерирует целевую иксу\n3. Ты вовремя жмешь «Забрать» и получаешь профит\n\n🎁 <i>Хочешь получать сигналы бесплатно и участвовать в розыгрыше $100? Жми кнопку «👥 Конкурс и Рефералы».</i>\n\n🚀 <b>Твой личный AI-дилер уже ждет. Начни зарабатывать прямо сейчас!</b> 👇",
        'btn_reg': "💳 Регистрация", 'btn_instr': "📖 Инструкция", 'btn_sign': "🔮 Выдать сигнал", 'btn_lang': "🌐 Язык", 'btn_ref': "👥 Конкурс и Рефералы", 'btn_support': "🆘 Поддержка",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Язык изменен на Русский 🇷🇺",
        'need_reg': "⚠️ <b>ДОСТУП ЗАБЛОКИРОВАН!</b>\n\nАлгоритм ИИ требует привязки аккаунта 1win.\n\n👇 Зарегистрируйся в 1 клик, чтобы открыть доступ:\n\n<i>Или участвуй в конкурсе по кнопке «👥 Конкурс и Рефералы»!</i>",
        'regged': "✅ <b>УСПЕХ!</b> Аккаунт привязан к системе. Нейросеть активирована. Жми «Выдать сигнал»! 🚀",
        'choose_risk': "⚙️ <b>Настройка риска</b>\n\nВыбери уровень риска для следующего полета:",
        'btn_risk_1': "🟢 Низкий (до x1.5)", 'btn_risk_2': "🟡 Средний (до x2.5)", 'btn_risk_3': "🔴 Высокий (x3.0+)",
        'btn_main': "⬅️ Главное меню",
        'signal_title': "✈️ <b>Анализ завершен!</b>\nУровень риска: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>Целевой коэффициент для кэшаута:</b> <code>x{target}</code>\n\n{left}🔥 <i>Удачи! Не жадничай, забирай вовремя.</i>",
        'left_signals': "💡 <i>Осталось сигналов на сегодня: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>ДНЕВНОЙ ЛИМИТ ИСЧЕРПАН!</b>\n\nВы использовали все {limit} сигналов на сегодня. Нейросети нужно время для калибровки.\n\n👇 <b>Хотите больше сигналов?</b> Пригласите друга по кнопке «👥 Конкурс и Рефералы», чтобы получить бонусные попытки!",
        'instr_text': "📖 <b>КАК НАЧАТЬ ЗАРАБАТЫВАТЬ:</b>\n\n1️⃣ <b>Регистрация:</b> <a href='{url}'>КЛИКНИ СЮДА</a>\n2️⃣ <b>Депозит:</b> Пополни баланс.\n3️⃣ <b>Игра:</b> Перейди в раздел <b>Aviator</b>.\n4️⃣ <b>Настройка:</b> Выстави авто-кэшаут по сигналу.\n5️⃣ <b>Действие:</b> Запускай раунд и жди нужной иксы.\n6️⃣ <b>Страховка:</b> При проигрыше удваивай ставку.\n\n💸 <i>Профит при строгом следовании алгоритму!</i>",
        'admin_panel': "⚙️ Админ панель. Команда /top - таблица лидеров.", 'not_admin': "❌ У вас нет прав администратора.",
        'support_text': "🆘 <b>Служба поддержки</b>\n\nЕсли у вас возникли вопросы по работе бота, регистрации или выплатам, напишите менеджеру:\n\n👉 <a href='tg://user?id={admin_id}'>Написать администратору</a>",
        'ref_title': "🏆 <b>КОНКУРС С ПРИЗОВЫМ ФОНДОМ</b> 🏆\n\nПриглашай друзей и зарабатывай билеты! <b>1 зарегистрированный друг = 1 билет.</b>\n\n🥇 <b>1 место:</b> $100\n🥈 <b>2 место:</b> $50\n🥉 <b>3 место:</b> $20\n\n📊 Твои билеты: <b>{count}</b>\n\n🔗 Твоя ссылка для приглашения:\n<code>{link}</code>",
        'ref_notify': "🎉 По твоей ссылке зарегистрировался друг! Ты получил +1 билет. Всего билетов: <b>{count}</b>.",
        'ref_success': "🔥 <b>Ты пригласил 3 друзей!</b> Твой доступ к сигналам открыт навсегда. Но не останавливайся, на кону денежные призы!"
    },
    'en': {
        'welcome': "✈️ <b>SECRET ALGORITHM ACCESS GRANTED</b> ✈️\n\nWelcome to <b>AVIATOR AI PREDICTOR</b>!\n\n😤 Tired of watching the plane fly away at x1.01? It's time to take yours.\n\n🧠 Our neural network scans Aviator patterns and calculates the exact cashout multiplier with <b>up to 90% accuracy</b>.\n\n⚙️ <b>How it works?</b>\n1. Click '🔮 Get Signal'\n2. AI generates a target multiplier\n3. You cash out in time and get profit\n\n🎁 <i>Want free signals and a chance to win $100? Click '👥 Contest & Refs'.</i>\n\n🚀 <b>Start earning right now!</b> 👇",
        'btn_reg': "💳 Register", 'btn_instr': "📖 Instruction", 'btn_sign': "🔮 Get Signal", 'btn_lang': "🌐 Language", 'btn_ref': "👥 Contest & Refs", 'btn_support': "🆘 Support",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Language changed to English 🇬🇧",
        'need_reg': "⚠️ <b>ACCESS BLOCKED!</b>\n\nAI algorithm requires a 1win account link.\n\n👇 Register in 1 click below to unlock:\n\n<i>Or participate in the contest using the “👥 Contest & Refs” button!</i>",
        'regged': "✅ <b>SUCCESS!</b> Account linked. Neural network activated. Click 'Get Signal'! 🚀",
        'choose_risk': "⚙️ <b>Risk Configuration</b>\n\nChoose risk level for the next flight:",
        'btn_risk_1': "🟢 Low (up to x1.5)", 'btn_risk_2': "🟡 Medium (up to x2.5)", 'btn_risk_3': "🔴 High (x3.0+)",
        'btn_main': "⬅️ Main Menu",
        'signal_title': "✈️ <b>Analysis Complete!</b>\nRisk level: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>Target cashout multiplier:</b> <code>x{target}</code>\n\n{left}🔥 <i>Good luck! Don't be greedy, cash out on time.</i>",
        'left_signals': "💡 <i>Signals left today: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>DAILY LIMIT REACHED!</b>\n\nYou have used all {limit} signals for today. Invite a friend via '👥 Contest & Refs' to get bonus attempts!",
        'instr_text': "📖 <b>HOW TO START:</b>\n\n1️⃣ <b>Register:</b> <a href='{url}'>CLICK HERE</a>\n2️⃣ <b>Deposit:</b> Top up.\n3️⃣ <b>Game:</b> Go to <b>Aviator</b>.\n4️⃣ <b>Setup:</b> Set auto-cashout by signal.\n5️⃣ <b>Action:</b> Start the round and wait.\n6️⃣ <b>Insurance:</b> Double bet on loss.",
        'admin_panel': "⚙️ Admin panel. Command /top.", 'not_admin': "❌ You don't have admin rights.",
        'support_text': "🆘 <b>Support</b>\n\nContact our manager:\n\n👉 <a href='tg://user?id={admin_id}'>Message Admin</a>",
        'ref_title': "🏆 <b>PRIZE POOL CONTEST</b> 🏆\n\nInvite friends and earn tickets! <b>1 registered friend = 1 ticket.</b>\n\n🥇 <b>1st:</b> $100\n🥈 <b>2nd:</b> $50\n🥉 <b>3rd:</b> $20\n\n📊 Tickets: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Friend registered! +1 ticket. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 friends invited!</b> Access is open forever."
    },
    'es': {
        'welcome': "✈️ <b>ACCESO AL ALGORITMO SECRETO</b> ✈️\n\n¡Bienvenido a <b>AVIATOR AI PREDICTOR</b>!\n\n😤 ¿Cansado de que el avión vuele a x1.01? Deja de alimentar al casino.\n\n🧠 Nuestra red neuronal calcula el multiplicador exacto con <b>hasta un 90% de precisión</b>.\n\n⚙️ <b>¿Cómo funciona?</b>\n1. Haces clic en '🔮 Obtener señal'\n2. La IA genera un multiplicador\n3. Retiras a tiempo y obtienes ganancias\n\n🎁 <i>¿Quieres señales gratis y ganar $100? Haz clic en '👥 Concurso y Refs'.</i>\n\n🚀 <b>¡Empieza a ganar ahora!</b> 👇",
        'btn_reg': "💳 Registrarse", 'btn_instr': "📖 Instrucción", 'btn_sign': "🔮 Obtener señal", 'btn_lang': "🌐 Idioma", 'btn_ref': "👥 Concurso y Refs", 'btn_support': "🆘 Soporte",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Idioma cambiado a Español 🇪🇸",
        'need_reg': "⚠️ <b>¡ACCESO BLOQUEADO!</b>\n\nVincula tu cuenta de 1win.\n\n👇 Regístrate abajo:",
        'regged': "✅ <b>¡ÉXITO!</b> Cuenta vinculada. 🚀",
        'choose_risk': "⚙️ <b>Configuración de riesgo</b>\n\nElige el nivel de riesgo:",
        'btn_risk_1': "🟢 Bajo (hasta x1.5)", 'btn_risk_2': "🟡 Medio (hasta x2.5)", 'btn_risk_3': "🔴 Alto (x3.0+)",
        'btn_main': "⬅️ Menú Principal",
        'signal_title': "✈️ <b>¡Análisis completado!</b>\nRiesgo: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>Multiplicador objetivo:</b> <code>x{target}</code>\n\n{left}🔥 <i>¡Buena suerte!</i>",
        'left_signals': "💡 <i>Señales restantes hoy: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>¡LÍMITE DIARIO ALCANZADO!</b>\n\nHas usado las {limit} señales de hoy. ¡Invita a un amigo para obtener intentos extra!",
        'instr_text': "📖 <b>CÓMO EMPEZAR:</b>\n\n1️⃣ <b>Registro:</b> <a href='{url}'>HAZ CLIC AQUÍ</a>\n2️⃣ <b>Depósito:</b> Recarga.\n3️⃣ <b>Juego:</b> Ve a <b>Aviator</b>.\n4️⃣ <b>Configuración:</b> Auto-retiro.\n5️⃣ <b>Acción:</b> Abre la ronda.\n6️⃣ <b>Seguro:</b> Dobla al perder.",
        'admin_panel': "⚙️ Panel de admin. Comando /top.", 'not_admin': "❌ No eres admin.",
        'support_text': "🆘 <b>Soporte</b>\n\n👉 <a href='tg://user?id={admin_id}'>Mensaje al Admin</a>",
        'ref_title': "🏆 <b>CONCURSO CON PREMIOS</b> 🏆\n\n¡Invita amigos y gana boletos! <b>1 amigo = 1 boleto.</b>\n\n🥇 <b>1er lugar:</b> $100\n🥈 <b>2do:</b> $50\n🥉 <b>3er:</b> $20\n\n📊 Boletos: <b>{count}</b>\n\n🔗 Enlace:\n<code>{link}</code>",
        'ref_notify': "🎉 ¡Un amigo se registró! +1 boleto. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>¡Invitaste a 3 amigos!</b> Acceso abierto."
    },
    'pt': {
        'welcome': "✈️ <b>ACESSO AO ALGORITMO SECRETO</b> ✈️\n\nBem-vindo ao <b>AVIATOR AI PREDICTOR</b>!\n\n😤 Cansado de ver o avião voar em x1.01? Pare de alimentar o cassino.\n\n🧠 Nossa rede neural calcula o multiplicador exato com <b>até 90% de precisão</b>.\n\n⚙️ <b>Como funciona?</b>\n1. Clique em '🔮 Obter sinal'\n2. A IA gera um multiplicador\n3. Retire a tempo e obtenha lucro\n\n🎁 <i>Quer sinais grátis e chance de ganhar $100? Clique em '👥 Concurso e Refs'.</i>\n\n🚀 <b>Comece a ganhar agora!</b> 👇",
        'btn_reg': "💳 Registre-se", 'btn_instr': "📖 Instrução", 'btn_sign': "🔮 Obter sinal", 'btn_lang': "🌐 Idioma", 'btn_ref': "👥 Concurso e Refs", 'btn_support': "🆘 Suporte",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Idioma alterado para Português 🇵🇹",
        'need_reg': "⚠️ <b>ACESSO BLOQUEADO!</b>\n\nVincule sua conta 1win.\n\n👇 Registre-se abaixo:",
        'regged': "✅ <b>SUCESSO!</b> Conta vinculada. 🚀",
        'choose_risk': "⚙️ <b>Configuração de risco</b>\n\nEscolha o nível de risco:",
        'btn_risk_1': "🟢 Baixo (até x1.5)", 'btn_risk_2': "🟡 Médio (até x2.5)", 'btn_risk_3': "🔴 Alto (x3.0+)",
        'btn_main': "⬅️ Menu Principal",
        'signal_title': "✈️ <b>Análise concluída!</b>\nRisco: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>Multiplicador alvo:</b> <code>x{target}</code>\n\n{left}🔥 <i>Boa sorte!</i>",
        'left_signals': "💡 <i>Sinais restantes hoje: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>LIMITE DIÁRIO ATINGIDO!</b>\n\nVocê usou todos os {limit} sinais de hoje. Convide um amigo para tentativas extras!",
        'instr_text': "📖 <b>COMO COMEÇAR:</b>\n\n1️⃣ <b>Registro:</b> <a href='{url}'>CLIQUE AQUI</a>\n2️⃣ <b>Depósito:</b> Recarregue.\n3️⃣ <b>Jogo:</b> Vá para <b>Aviator</b>.\n4️⃣ <b>Configuração:</b> Auto-retirada.\n5️⃣ <b>Ação:</b> Abra a rodada.\n6️⃣ <b>Seguro:</b> Dobre na perda.",
        'admin_panel': "⚙️ Painel de admin. Comando /top.", 'not_admin': "❌ Você não é admin.",
        'support_text': "🆘 <b>Suporte</b>\n\n👉 <a href='tg://user?id={admin_id}'>Mensagem para o Admin</a>",
        'ref_title': "🏆 <b>CONCURSO COM PRÊMIOS</b> 🏆\n\nConvide amigos e ganhe bilhetes! <b>1 amigo = 1 bilhete.</b>\n\n🥇 <b>1º:</b> $100\n🥈 <b>2º:</b> $50\n🥉 <b>3º:</b> $20\n\n📊 Bilhetes: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Um amigo se registrou! +1 bilhete. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>Você convidou 3 amigos!</b> Acesso aberto."
    },
    'hi': {
        'welcome': "✈️ <b>गुप्त एल्गोरिथम तक पहुंच</b> ✈️\n\n<b>AVIATOR AI PREDICTOR</b> में आपका स्वागत है!\n\n😤 x1.01 पर विमान को उड़ते देखना थक गए? कैसीनो को खिलाना बंद करें।\n\n🧠 हमारा न्यूरल नेटवर्क <b>90% तक सटीकता</b> के साथ सटीक गुणक की गणना करता है।\n\n⚙️ <b>यह कैसे काम करता है?</b>\n1. '🔮 सिग्नल प्राप्त करें' पर क्लिक करें\n2. AI लक्ष्य गुणक उत्पन्न करता है\n3. समय पर नकद निकालें और लाभ प्राप्त करें\n\n🎁 <i>मुफ्त सिग्नल चाहते हैं? '👥 प्रतियोगिता और रेफरल' पर क्लिक करें।</i>\n\n🚀 <b>अभी कमाना शुरू करें!</b> 👇",
        'btn_reg': "💳 पंजीकरण", 'btn_instr': "📖 निर्देश", 'btn_sign': "🔮 सिग्नल प्राप्त करें", 'btn_lang': "🌐 भाषा", 'btn_ref': "👥 प्रतियोगिता और रेफरल", 'btn_support': "🆘 सहायता",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "भाषा हिंदी में बदल गई 🇮🇳",
        'need_reg': "⚠️ <b>पहुंच अवरुद्ध!</b>\n\n1win खाता लिंक करें।\n\n👇 नीचे पंजीकरण करें:",
        'regged': "✅ <b>सफलता!</b> खाता लिंक हो गया। 🚀",
        'choose_risk': "⚙️ <b>जोखिम कॉन्फ़िगरेशन</b>\n\nजोखिम स्तर चुनें:",
        'btn_risk_1': "🟢 कम (x1.5 तक)", 'btn_risk_2': "🟡 मध्यम (x2.5 तक)", 'btn_risk_3': "🔴 उच्च (x3.0+)",
        'btn_main': "⬅️ मुख्य मेनू",
        'signal_title': "✈️ <b>विश्लेषण पूरा!</b>\nजोखिम: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>लक्ष्य गुणक:</b> <code>x{target}</code>\n\n{left}🔥 <i>शुभकामनाएं!</i>",
        'left_signals': "💡 <i>आज बचे सिग्नल: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>दैनिक सीमा समाप्त!</b>\n\nआपने आज के सभी {limit} सिग्नल का उपयोग कर लिया है। बोनस के लिए दोस्त को आमंत्रित करें!",
        'instr_text': "📖 <b>कैसे शुरू करें:</b>\n\n1️⃣ <b>पंजीकरण:</b> <a href='{url}'>यहाँ क्लिक करें</a>\n2️⃣ <b>जमा:</b> टॉप अप करें।\n3️⃣ <b>गेम:</b> <b>Aviator</b> पर जाएं।\n4️⃣ <b>सेटअप:</b> ऑटो-कैशआउट सेट करें।\n5️⃣ <b>कार्रवाई:</b> राउंड शुरू करें।\n6️⃣ <b>बीमा:</b> हार पर दोगुना करें।",
        'admin_panel': "⚙️ एडमिन पैनल। कमांड /top।", 'not_admin': "❌ आप एडमिन नहीं हैं।",
        'support_text': "🆘 <b>सहायता</b>\n\n👉 <a href='tg://user?id={admin_id}'>एडमिन को संदेश भेजें</a>",
        'ref_title': "🏆 <b>पुरस्कार प्रतियोगिता</b> 🏆\n\nदोस्तों को आमंत्रित करें! <b>1 दोस्त = 1 टिकट।</b>\n\n🥇 <b>1st:</b> $100\n🥈 <b>2nd:</b> $50\n🥉 <b>3rd:</b> $20\n\n📊 टिकट: <b>{count}</b>\n\n🔗 लिंक:\n<code>{link}</code>",
        'ref_notify': "🎉 एक दोस्त पंजीकृत हुआ! +1 टिकट। कुल: <b>{count}</b>।",
        'ref_success': "🔥 <b>आपने 3 दोस्तों को आमंत्रित किया!</b> पहुंच हमेशा के लिए खुली है।"
    },
    'ar': {
        'welcome': "✈️ <b>تم منح الوصول إلى الخوارزمية السرية</b> ✈️\n\nمرحبًا بك في <b>AVIATOR AI PREDICTOR</b>!\n\n😤 سئمت من هروب الطائرة عند x1.01؟ توقف عن إطعام الكازينو.\n\n🧠 شبكتنا العصبية تحسب مضاعف السحب الصحيح بدقة <b>تصل إلى 90٪</b>.\n\n⚙️ <b>كيف يعمل؟</b>\n1. تنقر على '🔮 الحصول على إشارة'\n2. ينشئ الذكاء الاصطناعي مضاعفًا مستهدفًا\n3. تسحب في الوقت المحدد وتحقق الربح\n\n🎁 <i>تريد إشارات مجانية؟ انقر على '👥 المسابقة والإحالات'.</i>\n\n🚀 <b>ابدأ الكسب الآن!</b> 👇",
        'btn_reg': "💳 التسجيل", 'btn_instr': "📖 تعليمات", 'btn_sign': "🔮 الحصول على إشارة", 'btn_lang': "🌐 اللغة", 'btn_ref': "👥 المسابقة والإحالات", 'btn_support': "🆘 الدعم",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "تم تغيير اللغة إلى العربية 🇸🇦",
        'need_reg': "⚠️ <b>تم حظر الوصول!</b>\n\nاربط حسابك في 1win.\n\n👇 سجل أدناه:",
        'regged': "✅ <b>نجاح!</b> تم ربط الحساب. 🚀",
        'choose_risk': "⚙️ <b>تكوين المخاطر</b>\n\nاختر مستوى المخاطرة:",
        'btn_risk_1': "🟢 منخفض (حتى x1.5)", 'btn_risk_2': "🟡 متوسط (حتى x2.5)", 'btn_risk_3': "🔴 مرتفع (x3.0+)",
        'btn_main': "⬅️ القائمة الرئيسية",
        'signal_title': "✈️ <b>اكتمل التحليل!</b>\nالمخاطر: <b>{risk_name}</b>\n\n",
        'signal_hint': "\n🎯 <b>مضاعف السحب المستهدف:</b> <code>x{target}</code>\n\n{left}🔥 <i>حظا سعيدا!</i>",
        'left_signals': "💡 <i>الإشارات المتبقية اليوم: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>تم الوصول إلى الحد اليومي!</b>\n\nلقد استخدمت جميع الإشارات الـ {limit} لهذا اليوم. ادعو صديقًا للحصول على محاولات إضافية!",
        'instr_text': "📖 <b>كيف تبدأ:</b>\n\n1️⃣ <b>التسجيل:</b> <a href='{url}'>انقر هنا</a>\n2️⃣ <b>إيداع:</b> اشحن رصيدك.\n3️⃣ <b>اللعبة:</b> انتقل إلى <b>Aviator</b>.\n4️⃣ <b>الإعداد:</b> ضع السحب التلقائي.\n5️⃣ <b>الإجراء:</b> ابدأ الجولة.\n6️⃣ <b>التأمين:</b> ضاعف عند الخسارة.",
        'admin_panel': "⚙️ لوحة المسؤول. الأمر /top.", 'not_admin': "❌ ليس لديك حقوق المسؤول.",
        'support_text': "🆘 <b>الدعم</b>\n\n👉 <a href='tg://user?id={admin_id}'>مراسلة المسؤول</a>",
        'ref_title': "🏆 <b>مسابقة جوائز</b> 🏆\n\nادعو الأصدقاء! <b>صديق = تذكرة.</b>\n\n🥇 <b>1:</b> $100\n🥈 <b>2:</b> $50\n🥉 <b>3:</b> $20\n\n📊 تذاكرك: <b>{count}</b>\n\n🔗 رابطك:\n<code>{link}</code>",
        'ref_notify': "🎉 سجل صديق! +1 تذكرة. الإجمالي: <b>{count}</b>.",
        'ref_success': "🔥 <b>لقد دعوت 3 أصدقاء!</b> وصولك مفتوح للأبد."
    }
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("aviator")

# ---------- DB ----------
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

# ---------- Bot ----------
bot = Bot(token=BOT_TOKEN, disable_web_page_preview=True, parse_mode="HTML")
dp = Dispatcher()

def get_lang_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"), InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
        [InlineKeyboardButton(text="🇪🇸 Español", callback_data="set_lang_es"), InlineKeyboardButton(text="🇵🇹 Português", callback_data="set_lang_pt")],
        [InlineKeyboardButton(text="🇮🇳 हिंदी", callback_data="set_lang_hi"), InlineKeyboardButton(text="🇸🇦 العربية", callback_data="set_lang_ar")]
    ])
    return kb

def main_menu(lang):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_reg'], callback_data="reg")],
        [InlineKeyboardButton(text=LANG[lang]['btn_instr'], callback_data="instr")],
        [InlineKeyboardButton(text=LANG[lang]['btn_sign'], callback_data="sign")],
        [InlineKeyboardButton(text=LANG[lang]['btn_ref'], callback_data="ref_menu")],
        [InlineKeyboardButton(text=LANG[lang]['btn_support'], callback_data="support")],
        [InlineKeyboardButton(text=LANG[lang]['btn_lang'], callback_data="lang_menu")]
    ])
    return kb

def reg_kb(uid, lang):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_reg'], url=PARTNER_URL.format(uid=uid))]
    ])
    return kb

def risk_menu(lang):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_1'], callback_data="gen_risk_Low")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_2'], callback_data="gen_risk_Medium")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_3'], callback_data="gen_risk_High")],
        [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]
    ])
    return kb

def sign_kb(lang):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_sign'], callback_data="sign")],
        [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]
    ])
    return kb

def generate_aviator_signal(lang, risk_level="Medium", signals_left=0):
    if risk_level == "Low":
        target = round(random.uniform(1.20, 1.60), 2)
        risk_name = LANG[lang]['btn_risk_1'].split(' ')[1]
        graphic = "📈  🛫\n     🛫\n          🛫"
    elif risk_level == "High":
        target = round(random.uniform(2.80, 7.50), 2)
        risk_name = LANG[lang]['btn_risk_3'].split(' ')[1]
        graphic = "📈  🛫\n          🛫\n               🛫\n                    🛫"
    else:
        target = round(random.uniform(1.80, 2.50), 2)
        risk_name = LANG[lang]['btn_risk_2'].split(' ')[1]
        graphic = "📈  🛫\n     🛫\n          🛫\n               🛫"
        
    title = LANG[lang]['signal_title'].format(risk_name=risk_name)
    
    if signals_left > 0:
        left_text = LANG[lang]['left_signals'].format(left=signals_left)
    else:
        left_text = ""
        
    hint = LANG[lang]['signal_hint'].format(target=target, left=left_text)
    
    return f"{title}<code>{graphic}</code>\n{hint}"

# ---------- Handlers ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    uid = message.from_user.id
    args = command.args
    
    referrer_id = None
    if args and args.isdigit():
        referrer_id = int(args)
        if referrer_id == uid:
            referrer_id = None 
            
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
    await call.message.edit_text(
        text=LANG[new_lang]['welcome'],
        reply_markup=main_menu(new_lang)
    )

@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user['lang'] if user else 'ru'
    await call.message.edit_text(
        text=LANG[lang]['welcome'],
        reply_markup=main_menu(lang)
    )
    await call.answer()

@dp.callback_query(F.data == "support")
async def cb_support(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user['lang'] if user else 'ru'
    text = LANG[lang]['support_text'].format(admin_id=ADMIN_ID)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])
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
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])
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
    await call.message.edit_text(
        text=LANG[lang]['choose_risk'],
        reply_markup=risk_menu(lang)
    )
    await call.answer()

@dp.callback_query(F.data.startswith("gen_risk_"))
async def cb_gen_risk(call: types.CallbackQuery):
    uid = call.from_user.id
    user = get_user(uid)
    lang = user['lang'] if user else 'ru'
    
    today = datetime.date.today().isoformat()
    daily_signals = user['daily_signals']
    
    if user['last_signal_date'] != today:
        daily_signals = 0
        
    if daily_signals >= DAILY_LIMIT:
        await call.answer("⚠️ Лимит на сегодня исчерпан!", show_alert=True)
        await call.message.answer(LANG[lang]['limit_msg'].format(limit=DAILY_LIMIT))
        return
        
    daily_signals += 1
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE user SET daily_signals = ?, last_signal_date = ? WHERE user_id = ?", 
            (daily_signals, today, uid)
        )
        conn.commit()
    
    signals_left = DAILY_LIMIT - daily_signals
    risk_level = call.data.split("_")[-1]
    
    signal_text = generate_aviator_signal(lang, risk_level, signals_left)
    
    await call.message.edit_text(
        text=signal_text,
        reply_markup=sign_kb(lang)
    )
    await call.answer()

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    user = get_user(message.from_user.id)
    lang = user['lang'] if user else 'ru'
    if str(message.from_user.id) != str(ADMIN_ID):
        await message.answer(LANG[lang]['not_admin'])
        return
    await message.answer(LANG[lang]['admin_panel'])

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT u1.user_id, COUNT(u2.user_id) as ref_count
            FROM user u1
            JOIN user u2 ON u1.user_id = u2.referrer_id
            WHERE u2.postback_id IS NOT NULL
            GROUP BY u1.user_id
            ORDER BY ref_count DESC
            LIMIT 10
        """).fetchall()

    if not rows:
        await message.answer("Пока нет рефералов с регистрациями.")
        return

    text = "🏆 <b>ТОП-10 УЧАСТНИКОВ КОНКУРСА</b> 🏆\n\n"
    for i, (uid, count) in enumerate(rows, 1):
        text += f"{i}. ID: <code>{uid}</code> — <b>{count} билетов</b>\n"

    await message.answer(text)

# ============================================================
# ВСТРОЕННЫЙ ВЕБ-СЕРВЕР ДЛЯ ПОСТБЕКОВ
# ============================================================
class PostbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == '/health' or parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
            return

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
                f"?chat_id={uid}&text={requests.utils.quote(text)}&parse_mode=HTML"
            )
            try:
                requests.get(url, timeout=10)
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
                        f"?chat_id={ref_id}&text={requests.utils.quote(ref_text)}&parse_mode=HTML"
                    )
                    try:
                        requests.get(ref_url, timeout=10)
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

# ---------- Entry ----------
async def main():
    # Устанавливаем кнопку меню (Start)
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(text="Start"))
    
    # Запуск бота (aiogram 3.x)
    await dp.start_polling(bot)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_web, daemon=True).start()
    log.info("Bot starting (aiogram 3.x)...")
    asyncio.run(main())