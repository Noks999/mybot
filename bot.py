import asyncio
import logging
import random
import string
import json
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ChatMemberStatus
import aiosqlite

# ============ НАСТРОЙКИ ============
BOT_TOKEN = "8544716257:AAHF_UBpvTs7IMB7aFm69-ycdYF7_qemEOo"
ADMIN_IDS = [7424256419]
DB_NAME = "exploit.db"
REVIEWS_LINK = "https://t.me/+y7FSXW3L53ExZjky"
SUPPORT_LINK = "https://t.me/ExploitOrig"
FILES_CHANNEL = "https://t.me/ExploitXitersFiles"
REQUIRED_CHANNEL_ID = -1003222770311
REQUIRED_CHANNEL_LINK = "https://t.me/+GkuqvoSDQNthOTJh"

DUSHANBE_CARD = "9762000105839392"
DUSHANBE_NAME = "Душанбе Сити"
YUMANI_CARD = "4100119145377099"
YUMANI_NAME = "Юмани"
BINANCE_ID = "1153650076"

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=storage)

# ============ ТОВАРЫ ============
# В PRODUCTS добавить:
PRODUCTS = {
    'internal': {
        'name': 'INTERNAL PANEL',
        'emoji': '🔷',
        'desc': """🎯 <b>AIMBOT</b>
• Aimbot Head
• Aimbot Legit
• Silent Aim
• Triggerbot

👁 <b>VISUAL</b>
• All Chams
• ESP
• WallHack
• Stream Mode

⚡ <b>MOVEMENT</b>
• Speed Hack
• Climb
• Spin 360

🔫 <b>EXTRA</b>
• Fast Fire
• No Recoil
• No Reload
• Double Guns

🌐 <b>LAG</b>
• Fake Lag
• Freeze Lag
• Flush Lag

🧲 <b>OTHER</b>
• Magnet
• Ghost Mode
• Hide Menu""",
        'prices': {3: 250, 7: 550, 15: 999, 30: 1599}
    },
    'aimbot': {
        'name': ' AIMBOT + BH',
        'emoji': '🎯',
        'desc': """🎯 <b>AIMBOT</b>
• Aimbot Head
• Chams Menu""",
        'prices': {1: 70, 7: 200, 30: 350}
    },
    'drip': {
        'name': ' DRIP CLIENT ANDROID',
        'emoji': '🤖',
        'desc': """<b>🤖 DRIP CLIENT ANDROID</b>

• Полная совместимость с Android
• Все функции Internal Panel
• Оптимизация под мобильные устройства
• Встроенный анти-бан""",
        'prices': {1: 105, 7: 300, 15: 500, 30: 750}
    },
    'fluorite': {
        'name': ' FLUORITE IOS',
        'emoji': '🍏',
        'desc': """<b>🍏 FLUORITE IOS</b>

• Полная совместимость с iOS
• Встроенная защита от бана""",
        'prices': {1: 600, 7: 1400, 30: 2250}
    },
    'bypass': {
        'name': ' BYPASS',
        'emoji': '🚀',
        'desc': """<b>🚀 BYPASS PANEL</b>

• Обход бана по HWID
• Полный обход античита
• Защита от всех видов банов""",
        'prices': {30: 1500}
    },
    'external': {
        'name': ' EXTERNAL PANEL',
        'emoji': '📡',
        'desc': """<b>📡 EXTERNAL PANEL</b>
• Aimbot
• Chams Menu
• Sniper Scope
• Sniper Switch
• 2x Scope Tracking



• Внешний чит (без инжекта)
• Работает на всех эмуляторах
• Низкий риск бана
• Простая установка
• Все основные функции""",
        'prices': {1: 120, 7: 290, 30: 450}
    }
}


# ============ FSM ============
class AddReseller(StatesGroup):
    waiting_for_user_id = State()

class SetResellerPrice(StatesGroup):
    waiting_for_product = State()
    waiting_for_user = State()
    waiting_for_prices = State()

# ============ БАЗА ДАННЫХ ============
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, referral_code TEXT, is_admin INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0, total_spent REAL DEFAULT 0, registration_date TEXT)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY, username TEXT, added_by INTEGER, added_date TEXT)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS resellers (user_id INTEGER PRIMARY KEY, username TEXT, custom_prices TEXT, added_by INTEGER, balance REAL DEFAULT 0, total_earned REAL DEFAULT 0, added_date TEXT)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, product_type TEXT, product_name TEXT, days INTEGER, amount REAL, payment_method TEXT, status TEXT DEFAULT 'pending', created_at TEXT)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE, product_type TEXT, product_name TEXT, days INTEGER, is_used INTEGER DEFAULT 0, used_by INTEGER, order_id INTEGER, created_at TEXT, expires_at TEXT)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS keyauth_pool (id INTEGER PRIMARY KEY AUTOINCREMENT, keyauth_key TEXT UNIQUE, product_type TEXT, product_name TEXT, duration_days INTEGER, is_used INTEGER DEFAULT 0, used_by INTEGER, order_id INTEGER, added_date TEXT, used_date TEXT)''')
        await db.commit()

# ============ ФУНКЦИИ ============
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL_ID, user_id=user_id)
        return member.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]
    except:
        return False

async def is_admin(user_id):
    if user_id in ADMIN_IDS: return True
    async with aiosqlite.connect(DB_NAME) as db:
        c = await db.execute('SELECT 1 FROM admins WHERE user_id = ?', (user_id,))
        return await c.fetchone() is not None

async def is_reseller(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        c = await db.execute('SELECT * FROM resellers WHERE user_id = ?', (user_id,))
        return await c.fetchone() is not None

async def get_reseller_prices(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        c = await db.execute('SELECT custom_prices FROM resellers WHERE user_id = ?', (user_id,))
        row = await c.fetchone()
        return json.loads(row[0]) if row and row[0] else None

async def get_prices(user_id, product_type):
    if await is_reseller(user_id):
        all_prices = await get_reseller_prices(user_id)
        if all_prices and product_type in all_prices:
            return {int(k): v for k, v in all_prices[product_type].items()}
    return PRODUCTS[product_type]['prices']

async def add_user(user_id, username, first_name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, referral_code, registration_date) VALUES (?, ?, ?, ?, ?)', (user_id, username, first_name, f"EX{user_id}", datetime.now().isoformat()))
        await db.commit()

async def add_reseller(user_id, username, added_by):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO resellers (user_id, username, custom_prices, added_by, added_date) VALUES (?, ?, ?, ?, ?)', (user_id, username, json.dumps({}), added_by, datetime.now().isoformat()))
        await db.commit()

async def delete_reseller(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM resellers WHERE user_id = ?', (user_id,))
        await db.commit()

async def set_reseller_prices(reseller_id, product_type, prices):
    async with aiosqlite.connect(DB_NAME) as db:
        c = await db.execute('SELECT custom_prices FROM resellers WHERE user_id = ?', (reseller_id,))
        row = await c.fetchone()
        all_prices = json.loads(row[0]) if row and row[0] else {}
        all_prices[product_type] = {str(k): v for k, v in prices.items()}
        await db.execute('UPDATE resellers SET custom_prices = ? WHERE user_id = ?', (json.dumps(all_prices), reseller_id))
        await db.commit()

async def add_order(user_id, username, product_type, product_name, days, amount, payment):
    async with aiosqlite.connect(DB_NAME) as db:
        c = await db.execute('INSERT INTO orders (user_id, username, product_type, product_name, days, amount, payment_method, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (user_id, username, product_type, product_name, days, amount, payment, datetime.now().isoformat()))
        await db.commit()
        return c.lastrowid

async def get_pending_orders():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute("SELECT * FROM orders WHERE status='pending' ORDER BY created_at DESC LIMIT 20")
        return await c.fetchall()

async def get_all_orders(limit=50):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,))
        return await c.fetchall()

async def complete_order(order_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = await c.fetchone()
        if order:
            await db.execute("UPDATE orders SET status='completed' WHERE id=?", (order_id,))
            await db.execute('UPDATE users SET total_spent = total_spent + ? WHERE user_id = ?', (order['amount'], order['user_id']))
            await db.commit()
            return dict(order)
        return None

async def get_keyauth_key(product_type, duration_days):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute('SELECT * FROM keyauth_pool WHERE product_type = ? AND duration_days = ? AND is_used = 0 LIMIT 1', (product_type, duration_days))
        key = await c.fetchone()
        if key:
            await db.execute('UPDATE keyauth_pool SET is_used = 1, used_date = ? WHERE id = ?', (datetime.now().isoformat(), key['id']))
            await db.commit()
            return dict(key)
        return None

async def get_keyauth_count(product_type, days):
    async with aiosqlite.connect(DB_NAME) as db:
        c = await db.execute('SELECT COUNT(*) FROM keyauth_pool WHERE product_type = ? AND duration_days = ? AND is_used = 0', (product_type, days))
        return (await c.fetchone())[0]

async def get_keyauth_stats():
    """Полная статистика по всем ключам"""
    async with aiosqlite.connect(DB_NAME) as db:
        c = await db.execute("SELECT product_name, duration_days, COUNT(*) as total, SUM(CASE WHEN is_used=0 THEN 1 ELSE 0 END) as free FROM keyauth_pool GROUP BY product_name, duration_days ORDER BY product_name, duration_days")
        return await c.fetchall()

async def check_all_keys():
    """Проверяет все ключи и возвращает те, которых меньше 5"""
    low = []
    for pt, p in PRODUCTS.items():
        for d in p['prices']:
            cnt = await get_keyauth_count(pt, d)
            if cnt < 5:
                d_text = f"{d} дн." if d > 1 else f"{d} день"
                low.append((p['name'], d_text, cnt))
    return low

async def add_keyauth_keys(product_type, product_name, days, keys_list):
    async with aiosqlite.connect(DB_NAME) as db:
        now = datetime.now().isoformat()
        for k in keys_list:
            try: await db.execute('INSERT OR IGNORE INTO keyauth_pool (keyauth_key, product_type, product_name, duration_days, added_date) VALUES (?, ?, ?, ?, ?)', (k.strip(), product_type, product_name, days, now))
            except: pass
        await db.commit()

async def add_key(key, product_type, product_name, days, user_id, order_id=None):
    async with aiosqlite.connect(DB_NAME) as db:
        exp = (datetime.now() + timedelta(days=days)).isoformat()
        await db.execute('INSERT INTO keys (key, product_type, product_name, days, is_used, used_by, order_id, created_at, expires_at) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)', (key, product_type, product_name, days, user_id, order_id, datetime.now().isoformat(), exp))
        await db.commit()

async def get_user_keys(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute('SELECT * FROM keys WHERE used_by = ? AND is_used = 1 ORDER BY created_at DESC', (user_id,))
        return await c.fetchall()

async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        s = {}
        c = await db.execute('SELECT COUNT(*) FROM users'); s['users'] = (await c.fetchone())[0]
        c = await db.execute('SELECT COUNT(*) FROM orders'); s['orders'] = (await c.fetchone())[0]
        c = await db.execute("SELECT COUNT(*) FROM orders WHERE status='completed'"); s['completed'] = (await c.fetchone())[0]
        c = await db.execute("SELECT COALESCE(SUM(amount),0) FROM orders WHERE status='completed'"); s['revenue'] = (await c.fetchone())[0]
        c = await db.execute('SELECT COUNT(*) FROM keyauth_pool WHERE is_used = 0'); s['keyauth_keys'] = (await c.fetchone())[0]
        return s

# ============ УВЕДОМЛЕНИЯ О КЛЮЧАХ ============
async def notify_low_keys():
    """Отправляет уведомление админам о нехватке ключей"""
    low = await check_all_keys()
    if low:
        for admin_id in ADMIN_IDS:
            text = "⚠️ <b>ВНИМАНИЕ! МАЛО КЛЮЧЕЙ!</b>\n\n"
            text += "━━━━━━━━━━━━━━━━━━━━\n\n"
            for name, d_text, cnt in low:
                text += f"📦 <b>{name}</b>\n"
                text += f"⏱️ {d_text}\n"
                text += f"🔑 Осталось: <b>{cnt} шт.</b>\n\n"
            text += "━━━━━━━━━━━━━━━━━━━━\n\n"
            text += "🔴 Срочно добавьте ключи!\n"
            text += "Админ-панель → KEYAUTH → Добавить"
            try: await bot.send_message(admin_id, text)
            except: pass

# ============ КЛАВИАТУРЫ ============
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 МАГАЗИН", callback_data="shop")
    builder.button(text="🔑 МОИ КЛЮЧИ", callback_data="my_keys")
    builder.button(text="👤 ПРОФИЛЬ", callback_data="profile")
    builder.button(text="⭐ ОТЗЫВЫ", url=REVIEWS_LINK)
    builder.button(text="🆘 ПОДДЕРЖКА", url=SUPPORT_LINK)
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def shop_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔷 INTERNAL PANEL", callback_data="b_internal")
    builder.button(text="📡 EXTERNAL PANEL", callback_data="b_external")
    builder.button(text="🚀 BYPASS PANEL", callback_data="b_bypass")
    builder.button(text="🎯 AIMBOT PANEL", callback_data="b_aimbot")
    builder.button(text="🤖 DRIP CLIENT ANDROID", callback_data="b_drip")
    builder.button(text="🍏 FLUORITE IOS", callback_data="b_fluorite")
    builder.button(text="🔙 НАЗАД", callback_data="main")
    builder.adjust(1)
    return builder.as_markup()

def pay_menu(prod, days):
    builder = InlineKeyboardBuilder()
    builder.button(text=f"💳 {DUSHANBE_NAME}", callback_data=f"pay_dushanbe_{prod}_{days}")
    builder.button(text=f"💳 {YUMANI_NAME}", callback_data=f"pay_yumani_{prod}_{days}")
    builder.button(text="⭐ Telegram Stars", callback_data=f"stars_{prod}_{days}")
    builder.button(text="🟡 Binance", callback_data=f"pay_binance_{prod}_{days}")
    builder.button(text="🔙 НАЗАД", callback_data=f"b_{prod}")
    builder.adjust(1)
    return builder.as_markup()

# В admin_menu() добавить:
def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 СТАТИСТИКА", callback_data="a_stats")
    builder.button(text="📦 ЗАКАЗЫ", callback_data="a_orders")
    builder.button(text="🔑 KEYAUTH", callback_data="a_keyauth")
    builder.button(text="🔍 ПРОВЕРИТЬ КЛЮЧИ", callback_data="a_check_keys")
    builder.button(text="➕ KEYAUTH INT", callback_data="akp_internal")
    builder.button(text="➕ KEYAUTH AIM", callback_data="akp_aimbot")
    builder.button(text="➕ KEYAUTH DRIP", callback_data="akp_drip")
    builder.button(text="➕ KEYAUTH FLUOR", callback_data="akp_fluorite")
    builder.button(text="➕ KEYAUTH BYPASS", callback_data="akp_bypass")
    builder.button(text="➕ KEYAUTH EXTERNAL", callback_data="akp_external")
    builder.button(text="🤝 РЕСЕЛЛЕРЫ", callback_data="a_resellers")
    builder.button(text="➕ ДОБАВИТЬ", callback_data="a_add_reseller")
    builder.button(text="❌ УДАЛИТЬ", callback_data="a_del_reseller")
    builder.button(text="💰 ЦЕНЫ", callback_data="a_set_price")
    builder.button(text="👥 ПОЛЬЗОВАТЕЛИ", callback_data="a_users")
    builder.button(text="📢 РАССЫЛКА", callback_data="a_broadcast")
    builder.button(text="🔙 НАЗАД", callback_data="main")
    builder.adjust(2, 2, 2, 2, 2, 2, 2, 1)
    return builder.as_markup()

def sub_check_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 ПОДПИСАТЬСЯ НА КАНАЛ", url=REQUIRED_CHANNEL_LINK)
    builder.button(text="✅ ПРОВЕРИТЬ ПОДПИСКУ", callback_data="check_sub")
    builder.adjust(1)
    return builder.as_markup()

async def require_subscription(message: types.Message):
    if await is_admin(message.from_user.id): return True
    if not await check_subscription(message.from_user.id):
        await message.answer(
            f"🚫 <b>ДОСТУП ЗАКРЫТ</b> 🚫\n\n"
            f"Без подписки на канал пользоваться ботом невозможно.\n\n"
            f"🔗 {REQUIRED_CHANNEL_LINK}\n\n"
            f"<b>❗️ Что ты получаешь в канале:</b>\n"
            f"• Все обновления панелей раньше всех\n"
            f"• Закрытые промокоды и скидки\n"
            f"• Рабочие гайды и настройки\n"
            f"• Важные новости без мусора\n\n"
            f"⚠️ Без подписки — функционал бота заблокирован.\n\n"
            f"✅ Подписался? Тогда жми кнопку ниже 👇\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=sub_check_keyboard()
        )
        return False
    return True

# ============ /start ============
@dp.message(Command("start"))
async def start(message: types.Message):
    await init_db()
    if not await require_subscription(message): return
    
    uid = message.from_user.id
    await add_user(uid, message.from_user.username or f"user{uid}", message.from_user.first_name or "User")
    
    try:
        photo = FSInputFile("images/ChatGPT Image Apr 27, 2026, 10_53_13 PM.png")
        await message.answer_photo(photo=photo, caption="""⚡️ <b>EXPLOIT XITERS</b> ⚡️
🔥 <b>ДОМИНИРУЙ В КАЖДОЙ КАТКЕ</b>

🛒 <b>МАГАЗИН ПАНЕЛЕЙ</b>

🔷 <b>INTERNAL</b> | 🎯 <b>AIMBOT</b>
🤖 <b>DRIP ANDROID</b> | 🍏 <b>FLUORITE IOS</b>

💳 <b>Оплата:</b> Душанбе Сити • Юмани • Stars • Binance

✅ Всё проверено и работает
⚡ Ключ приходит сразу после оплаты

👑 <b>Не играй как все - играй сильнее</b>""", parse_mode='HTML')
    except: pass
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 МАГАЗИН", callback_data="shop")
    builder.button(text="🔑 МОИ КЛЮЧИ", callback_data="my_keys")
    builder.button(text="👤 ПРОФИЛЬ", callback_data="profile")
    builder.button(text="⭐ ОТЗЫВЫ", url=REVIEWS_LINK)
    builder.button(text="🆘 ПОДДЕРЖКА", url=SUPPORT_LINK)
    if await is_admin(uid): builder.button(text="🔐 АДМИН-ПАНЕЛЬ", callback_data="admin_panel")
    builder.adjust(2, 2, 1)
    await message.answer("👇 <b>Выберите действие:</b>", reply_markup=builder.as_markup())

# ============ CALLBACKS ============
@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.delete()
        await start(call.message)
    else:
        await call.answer("❌ Вы не подписаны на канал!", show_alert=True)

@dp.callback_query()
async def callbacks(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    uid = call.from_user.id
    
    if data not in ["check_sub"]:
        if not await is_admin(uid) and not await check_subscription(uid):
            await call.answer("❌ Подпишитесь на канал!", show_alert=True)
            return
    
    await call.answer()
    
    if data == "main":
        await call.message.answer("🔥 <b>EXPLOIT XITERS</b>\n\nГлавное меню:", reply_markup=main_menu())
    
    elif data == "shop":
        await call.message.answer("🛍 <b>МАГАЗИН ПАНЕЛЕЙ</b>\n\nВыберите продукт:", reply_markup=shop_menu())
    
    elif data.startswith("b_"):
        prod = data.replace("b_", "")
        p = PRODUCTS[prod]
        prices = await get_prices(uid, prod)
        
        builder = InlineKeyboardBuilder()
        for d, price in sorted(prices.items()):
            t = f"{d} дн." if d > 1 else f"{d} день" if d == 1 else f"{d} мес." if d == 30 else f"{d} дн."
            builder.button(text=f"{t} — {price}₽", callback_data=f"d_{prod}_{d}")
        builder.button(text="🔙 НАЗАД", callback_data="shop")
        builder.adjust(1)
        
        try:
            photo = FSInputFile(f"images/{prod}.jpg")
            await call.message.answer_photo(photo=photo, caption=f"{p['emoji']} <b>{p['name']}</b>\n\n{p['desc']}\n\n<b>⏱ Выберите срок:</b>", reply_markup=builder.as_markup(), parse_mode='HTML')
        except:
            await call.message.answer(f"{p['emoji']} <b>{p['name']}</b>\n\n{p['desc']}\n\n<b>⏱ Выберите срок:</b>", reply_markup=builder.as_markup(), parse_mode='HTML')
    
    elif data.startswith("d_"):
        parts = data.split("_", 2)
        prod = parts[1]
        days = int(parts[2])
        p = PRODUCTS[prod]
        prices = await get_prices(uid, prod)
        price = prices[days]
        
        if days == 30 and prod == 'drip':
            d_text = "1 месяц"
        elif days == 1:
            d_text = "1 день"
        else:
            d_text = f"{days} дн."
        
        text = f"{p['emoji']} <b>{p['name']}</b>\n\n━━━━━━━━━━━━━━━━━━━━\n\n⏱️ <b>Срок:</b> {d_text}\n💰 <b>Цена:</b> {price}₽\n\n━━━━━━━━━━━━━━━━━━━━\n\n<b>💳 Выберите способ оплаты:</b>"
        await call.message.answer(text, reply_markup=pay_menu(prod, days))
    
    elif data.startswith("pay_dushanbe_") or data.startswith("pay_yumani_") or data.startswith("pay_binance_"):
        parts = data.split("_", 3)
        method = parts[1]
        prod = parts[2]
        days = int(parts[3])
        
        p = PRODUCTS[prod]
        prices = await get_prices(uid, prod)
        price = prices[days]
        
        if days == 30 and prod == 'drip':
            d_text = "1 месяц"
        elif days == 1:
            d_text = "1 день"
        else:
            d_text = f"{days} дн."
        
        oid = await add_order(uid, call.from_user.username or f"user{uid}", prod, p['name'], days, price, method)
        
        if method == "dushanbe":
            pay_info = f"💳 <b>{DUSHANBE_NAME}</b>\n<code>{DUSHANBE_CARD}</code>"
        elif method == "yumani":
            pay_info = f"💳 <b>{YUMANI_NAME}</b>\n<code>{YUMANI_CARD}</code>"
        else:
            pay_info = f"🟡 <b>Binance ID:</b>\n<code>{BINANCE_ID}</code>"
        
        text = f"💳 <b>ОПЛАТА ЗАКАЗА №{oid}</b>\n\n━━━━━━━━━━━━━━━━━━━━\n📦 <b>Товар:</b> {p['name']}\n⏱️ <b>Срок:</b> {d_text}\n💰 <b>Сумма:</b> {price}₽\n━━━━━━━━━━━━━━━━━━━━\n\n{pay_info}\n\n⚠️ <i>После оплаты нажмите кнопку «Я ОПЛАТИЛ»</i>"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я ОПЛАТИЛ", callback_data=f"paid_{oid}")],
            [InlineKeyboardButton(text="🔙 НАЗАД", callback_data=f"d_{prod}_{days}")]
        ])
        await call.message.answer(text, reply_markup=kb)
    
    elif data.startswith("paid_"):
        oid = int(data.replace("paid_", ""))
        
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            c = await db.execute('SELECT * FROM orders WHERE id = ?', (oid,))
            order = await c.fetchone()
        
        if order:
            for aid in ADMIN_IDS:
                try:
                    if order['days'] == 30 and order['product_type'] == 'drip':
                        d_text = "1 месяц"
                    elif order['days'] == 1:
                        d_text = "1 день"
                    else:
                        d_text = f"{order['days']} дн."
                    
                    await bot.send_message(aid,
                        f"🔔 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 <b>Заказ №{oid}</b>\n"
                        f"👤 <b>От:</b> @{order['username']} (ID: {order['user_id']})\n"
                        f"📦 <b>Товар:</b> {order['product_name']}\n"
                        f"⏱️ <b>Срок:</b> {d_text}\n"
                        f"💰 <b>Сумма:</b> {order['amount']}₽\n"
                        f"💳 <b>Оплата:</b> {order['payment_method']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"✅ <code>/approve {oid}</code> — подтвердить\n"
                        f"❌ <code>/cancel {oid}</code> — отменить"
                    )
                except: pass
        
        await call.message.answer("✅ <b>ЗАКАЗ ОТПРАВЛЕН!</b>\n\nОжидайте подтверждения администратора.\nОбычно это занимает 1-5 минут.\n\n💬 Поддержка: @ExploitOrig", reply_markup=main_menu())
    
    elif data.startswith("stars_"):
        parts = data.split("_", 2)
        prod = parts[1]
        days = int(parts[2])
        p = PRODUCTS[prod]
        prices = await get_prices(uid, prod)
        price = prices[days]
        await bot.send_invoice(chat_id=uid, title=f"{p['name']} - {days} дн.", description=p['desc'][:200],
            payload=f"sp_{prod}_{days}", provider_token="", currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=int(price*1.2))])
    
    elif data == "my_keys":
        keys = await get_user_keys(uid)
        text = "🔑 <b>ВАШИ КЛЮЧИ</b>\n\n"
        if keys:
            for k in keys:
                try:
                    exp = datetime.fromisoformat(k['expires_at']); left = (exp - datetime.now()).days
                except: left = 0
                s = "✅ Активен" if left > 0 else "❌ Истёк"
                text += f"🎮 {k['product_name']}\n🔑 <code>{k['key']}</code>\n⏱ {max(0,left)} дн. {s}\n\n"
        else: text += "😔 Нет ключей"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍 В МАГАЗИН", callback_data="shop")],
            [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="main")]
        ])
        await call.message.answer(text, reply_markup=kb)
    
    elif data == "profile":
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            c = await db.execute('SELECT * FROM users WHERE user_id = ?', (uid,)); u = await c.fetchone()
            c = await db.execute("SELECT COUNT(*) FROM orders WHERE user_id=? AND status='completed'", (uid,)); orders = (await c.fetchone())[0]
        reseller_text = ""
        if await is_reseller(uid):
            async with aiosqlite.connect(DB_NAME) as db:
                c = await db.execute('SELECT balance, total_earned FROM resellers WHERE user_id = ?', (uid,)); r = await c.fetchone()
                if r: reseller_text = f"\n💼 Баланс: {r[0]}₽\n💰 Заработано: {r[1]}₽"
        await call.message.answer(f"👤 <b>ПРОФИЛЬ</b>\n\n🆔 {uid}\n👑 Админ: {'✅' if await is_admin(uid) else '❌'}\n🤝 Реселлер: {'✅' if await is_reseller(uid) else '❌'}\n💰 Потрачено: {u['total_spent']}₽\n📦 Заказов: {orders}{reseller_text}", reply_markup=main_menu())
    
    # ============ АДМИН-ПАНЕЛЬ ============
    elif data == "admin_panel":
        if not await is_admin(uid): await call.answer("❌ Нет доступа!", show_alert=True); return
        s = await get_stats(); pending = await get_pending_orders()
        text = f"🔐 <b>АДМИН-ПАНЕЛЬ</b>\n\n👥 {s['users']} | 📦 {s['orders']} | ✅ {s['completed']} | 💰 {s['revenue']}₽ | 🔑 {s['keyauth_keys']} | ⏳ {len(pending)}"
        await call.message.answer(text, reply_markup=admin_menu())
    
    elif data == "a_stats":
        if not await is_admin(uid): return
        s = await get_stats()
        await call.message.answer(f"📊 👥{s['users']} | 📦{s['orders']} | ✅{s['completed']} | 💰{s['revenue']}₽", reply_markup=admin_menu())
    
    elif data == "a_orders":
        if not await is_admin(uid): return
        orders = await get_all_orders(30)
        text = "📦 <b>ЗАКАЗЫ</b>\n\n"
        for o in orders:
            s = "✅" if o['status'] == 'completed' else "⏳"
            text += f"№{o['id']} | {o['product_name'][:20]} | {o['days']}д | {o['amount']}₽ | {s}\n"
        await call.message.answer(text, reply_markup=admin_menu())
    
    elif data == "a_keyauth":
        if not await is_admin(uid): return
        keys = await get_keyauth_stats()
        text = "🔑 <b>KEYAUTH КЛЮЧИ</b>\n\n"
        if keys:
            for k in keys:
                text += f"📦 {k[0]} | {k[1]}д | Всего: {k[2]} | Своб: {k[3]}\n"
        else: text += "Нет ключей"
        await call.message.answer(text, reply_markup=admin_menu())
    
    elif data == "a_check_keys":
        if not await is_admin(uid): return
        low = await check_all_keys()
        if low:
            text = "🔍 <b>ПРОВЕРКА КЛЮЧЕЙ</b>\n\n⚠️ Мало ключей:\n\n"
            for name, d_text, cnt in low:
                text += f"📦 <b>{name}</b>\n⏱️ {d_text} — <b>{cnt} шт.</b>\n\n"
            text += "Срочно добавьте!"
        else:
            text = "✅ <b>ВСЕ КЛЮЧИ В НАЛИЧИИ!</b>"
        await call.message.answer(text, reply_markup=admin_menu())
    
    elif data.startswith("akp_"):
        if not await is_admin(uid): return
        prod = data.replace("akp_", ""); await state.update_data(ak_product=prod)
        p = PRODUCTS[prod]
        builder = InlineKeyboardBuilder()
        for d in p['prices']:
            if d == 30 and prod == 'drip': t = "1 месяц"
            elif d == 1: t = "1 день"
            else: t = f"{d} дн."
            builder.button(text=t, callback_data=f"akd_{d}")
        builder.button(text="🔙 НАЗАД", callback_data="admin_panel")
        builder.adjust(len(p['prices']), 1)
        await call.message.answer(f"➕ KEYAUTH: {p['name']}\n\nСрок:", reply_markup=builder.as_markup())
    
    elif data.startswith("akd_"):
        if not await is_admin(uid): return
        days = int(data.replace("akd_", "")); await state.update_data(ak_days=days)
        await call.message.answer(f"➕ KEYAUTH ({days} дн.)\n\n<code>/addkeys KEY1\\nKEY2</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 НАЗАД", callback_data="admin_panel")]]))
    
    elif data == "a_resellers":
        if not await is_admin(uid): return
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            c = await db.execute('SELECT * FROM resellers ORDER BY added_date DESC'); resellers = await c.fetchall()
        text = "🤝 <b>РЕСЕЛЛЕРЫ</b>\n\n" if resellers else "🤝 Нет реселлеров"
        for r in resellers: text += f"🆔 {r['user_id']} | @{r['username']}\n💰 {r['balance']}₽\n\n"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ ДОБАВИТЬ", callback_data="a_add_reseller"),
             InlineKeyboardButton(text="❌ УДАЛИТЬ", callback_data="a_del_reseller")],
            [InlineKeyboardButton(text="💰 ЦЕНЫ", callback_data="a_set_price")],
            [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="admin_panel")]
        ])
        await call.message.answer(text, reply_markup=kb)
    
    elif data == "a_add_reseller":
        if not await is_admin(uid): return
        await state.set_state(AddReseller.waiting_for_user_id)
        await call.message.answer("➕ Отправьте Telegram ID:\n<code>123456789</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ОТМЕНА", callback_data="admin_panel")]]))
    
    elif data == "a_del_reseller":
        if not await is_admin(uid): return
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            c = await db.execute('SELECT * FROM resellers'); resellers = await c.fetchall()
        if not resellers: await call.message.answer("Нет реселлеров", reply_markup=admin_menu()); return
        builder = InlineKeyboardBuilder()
        for r in resellers: builder.button(text=f"❌ {r['username'] or r['user_id']}", callback_data=f"delres_{r['user_id']}")
        builder.button(text="🔙 НАЗАД", callback_data="admin_panel"); builder.adjust(1)
        await call.message.answer("❌ Выберите реселлера:", reply_markup=builder.as_markup())
    
    elif data.startswith("delres_"):
        if not await is_admin(uid): return
        rid = int(data.replace("delres_", "")); await delete_reseller(rid)
        await call.answer(f"✅ Удален!", show_alert=True)
        await call.message.answer(f"✅ Реселлер {rid} удален!", reply_markup=admin_menu())
    
    elif data == "a_set_price":
        if not await is_admin(uid): return
        builder = InlineKeyboardBuilder()
        builder.button(text="🔷 INTERNAL", callback_data="spp_internal")
        builder.button(text="🎯 AIMBOT", callback_data="spp_aimbot")
        builder.button(text="🤖 DRIP", callback_data="spp_drip")
        builder.button(text="🍏 FLUORITE", callback_data="spp_fluorite")
        builder.button(text="🚀 BYPASS", callback_data="spp_bypass")
        builder.button(text="📡 EXTERNAL", callback_data="spp_external")
        builder.button(text="🔙 НАЗАД", callback_data="admin_panel")
        await state.set_state(SetResellerPrice.waiting_for_product)
        await call.message.answer("💰 Выберите продукт:", reply_markup=builder.as_markup())
    
    elif data.startswith("spp_"):
        prod = data.replace("spp_", ""); await state.update_data(sp_product=prod)
        await state.set_state(SetResellerPrice.waiting_for_user)
        await call.message.answer(f"💰 {PRODUCTS[prod]['name']}\n\nОтправьте ID и цены:\n<code>ID цена1 цена2 цена3</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ОТМЕНА", callback_data="admin_panel")]]))
    
    elif data == "a_users":
        if not await is_admin(uid): return
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            c = await db.execute('SELECT user_id, username, total_spent FROM users ORDER BY registration_date DESC LIMIT 30'); users = await c.fetchall()
        text = "👥 <b>ПОЛЬЗОВАТЕЛИ</b>\n\n"
        for u in users: text += f"🆔 {u['user_id']} | @{u['username'] or '—'} | {u['total_spent']}₽\n"
        await call.message.answer(text, reply_markup=admin_menu())
    
    elif data == "a_broadcast":
        if not await is_admin(uid): return
        await call.message.answer("📢 <b>РАССЫЛКА</b>\n\n<code>/broadcast Текст</code>", reply_markup=admin_menu())

# ============ FSM РЕСЕЛЛЕРЫ ============
@dp.message(AddReseller.waiting_for_user_id)
async def add_reseller_handler(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    try: nid = int(message.text.strip()); await add_reseller(nid, f"user{nid}", message.from_user.id); await message.reply(f"✅ Реселлер {nid}!")
    except: await message.reply("❌ Только ID!")
    await state.clear()

@dp.message(SetResellerPrice.waiting_for_user)
async def price_handler(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    data = await state.get_data(); prod = data['sp_product']
    try:
        parts = message.text.split(); rid = int(parts[0])
        p = PRODUCTS[prod]
        price_keys = list(p['prices'].keys())
        prices = {}
        for i, k in enumerate(price_keys):
            prices[k] = int(parts[i+1])
        await set_reseller_prices(rid, prod, prices)
        await message.reply(f"✅ Цены для {rid}!\n{p['name']}\n{prices}")
    except: await message.reply("❌ Формат: ID цена1 цена2 цена3")
    await state.clear()

# ============ КОМАНДЫ ============
@dp.message(Command("addkeys"))
async def cmd_addkeys(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    data = await state.get_data(); prod = data.get('ak_product'); days = data.get('ak_days')
    if prod and days:
        keys_list = [k.strip() for k in message.text.replace('/addkeys', '').split('\n') if k.strip()]
        if keys_list: await add_keyauth_keys(prod, PRODUCTS[prod]['name'], days, keys_list); await message.reply(f"✅ +{len(keys_list)} ({PRODUCTS[prod]['name']}, {days}д)"); await state.clear()
        else: await message.reply("❌ Отправьте ключи!")
    else: await message.reply("❌ Выберите продукт и срок в админ-панели!")

@dp.message(Command("approve"))
async def approve(message: types.Message):
    if not await is_admin(message.from_user.id): return
    try:
        oid = int(message.text.split()[1]); order = await complete_order(oid)
        if order:
            keyauth = await get_keyauth_key(order['product_type'], order['days'])
            if keyauth: key = keyauth['keyauth_key']; kt = "✅ KeyAuth"
            else:
                if await get_keyauth_count(order['product_type'], order['days']) == 0:
                    await message.reply(
                        f"⚠️ <b>КЛЮЧИ ЗАКОНЧИЛИСЬ!</b>\n\n"
                        f"📦 {order['product_name']}\n"
                        f"⏱️ {order['days']} дн.\n\n"
                        f"Срочно добавьте ключи через админ-панель!"
                    )
                    # Уведомление о закончившихся ключах
                    await notify_low_keys()
                    return
                key = f"EX-{''.join(random.choices(string.ascii_uppercase+string.digits, k=12))}"; kt = "⚠️ Обычный"
            await add_key(key, order['product_type'], order['product_name'], order['days'], order['user_id'], oid)
            
            if order['days'] == 30 and order['product_type'] == 'drip':
                d_text = "1 месяц"
            elif order['days'] == 1:
                d_text = "1 день"
            else:
                d_text = f"{order['days']} дн." if order['days'] > 1 else f"{order['days']} день"
            
            await bot.send_message(order['user_id'],
                f"✅ <b>ЗАКАЗ АКТИВИРОВАН!</b>\n\n"
                f"📦 {order['product_name']}\n"
                f"🔑 <code>{key}</code>\n"
                f"⏱️ {d_text}\n\n"
                f"📂 Файлы: {FILES_CHANNEL}")
            await message.reply(f"✅ №{oid} | {order['product_name']}\n🔑 {key}\n{kt}")
            
            # Проверка ключей после выдачи
            await notify_low_keys()
        else: await message.reply("❌ Заказ не найден")
    except: await message.reply("❌ /approve ID")

@dp.message(Command("cancel"))
async def cancel(message: types.Message):
    if not await is_admin(message.from_user.id): return
    try:
        oid = int(message.text.split()[1])
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("UPDATE orders SET status='cancelled' WHERE id=?", (oid,))
            await db.commit()
        await message.reply(f"❌ Заказ №{oid} отменен!")
    except: await message.reply("❌ /cancel ID")

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not await is_admin(message.from_user.id): return
    s = await get_stats(); pending = await get_pending_orders()
    await message.answer(f"🔐 👥{s['users']} | 📦{s['orders']} | ✅{s['completed']} | 💰{s['revenue']}₽ | 🔑{s['keyauth_keys']} | ⏳{len(pending)}", reply_markup=admin_menu())

@dp.message(Command("addadmin"))
async def addadmin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        nid = int(message.text.split()[1])
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('INSERT OR REPLACE INTO admins VALUES (?, ?, ?, ?)', (nid, f"user{nid}", message.from_user.id, datetime.now().isoformat())); await db.commit()
        await bot.send_message(nid, "🎉 Вы стали админом EXPLOIT XITERS!"); await message.reply(f"✅ {nid}!")
    except: await message.reply("❌ /addadmin ID")

@dp.message(Command("broadcast"))
async def broadcast(message: types.Message):
    if not await is_admin(message.from_user.id): return
    text = message.text.replace('/broadcast', '').strip()
    if not text: await message.reply("❌ /broadcast Текст"); return
    async with aiosqlite.connect(DB_NAME) as db:
        c = await db.execute('SELECT user_id FROM users WHERE is_banned=0'); users = await c.fetchall()
    s = 0
    for u in users:
        try: await bot.send_message(u[0], f"📢 {text}"); s += 1; await asyncio.sleep(0.05)
        except: pass
    await message.reply(f"✅ {s}/{len(users)}")

# ============ STARS ============
@dp.pre_checkout_query()
async def checkout(q: PreCheckoutQuery): await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message(F.successful_payment)
async def success(msg: types.Message):
    p = msg.successful_payment.invoice_payload
    if p.startswith("sp_"):
        parts = p.split("_")
        prod = parts[1]
        days = int(parts[2])
        key = f"EX-{''.join(random.choices(string.ascii_uppercase+string.digits, k=12))}"
        await add_key(key, prod, PRODUCTS[prod]['name'], days, msg.from_user.id)
        await msg.answer(f"✅ <b>ОПЛАЧЕНО!</b>\n\n📦 {PRODUCTS[prod]['name']}\n🔑 <code>{key}</code>\n⏱️ {days} дн.\n\n📂 {FILES_CHANNEL}")
        await notify_low_keys()

# ============ ЗАПУСК ============
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    print("🔥 EXPLOIT XITERS БОТ ЗАПУЩЕН!")
    print(f"📢 Канал: {REQUIRED_CHANNEL_LINK}")
    print(f"📂 Файлы: {FILES_CHANNEL}")
    # Проверяем ключи при запуске
    await notify_low_keys()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())