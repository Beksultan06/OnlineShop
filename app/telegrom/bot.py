import os
import django
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from asgiref.sync import sync_to_async

# Подключаем Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from app.shop.models import Product, Order

TOKEN = "8420115725:AAGhOwGmXk4S2GDO-MhEAU9tGtIhITiYpeE"
ADMIN_CHAT_ID = 5199401134  # замените на свой ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

# FSM для оформления заказа
class OrderForm(StatesGroup):
    name = State()
    phone = State()
    address = State()

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет! Я магазин OnlineShop 🛍️\nНапиши /products чтобы посмотреть товары."
    )

# Функция для показа товаров
async def show_products(message: types.Message):
    products = await sync_to_async(list)(Product.objects.all())
    if not products:
        await message.answer("Товаров пока нет 😔")
        return

    for product in products:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📄 Подробнее", callback_data=f"details_{product.id}")]
        ])
        await message.answer(f"📦 {product.name}\n💰 {product.price}", reply_markup=keyboard)

# Показ товаров командой /products
@dp.message(Command("products"))
async def products_handler(message: types.Message):
    await show_products(message)

# Показ деталей товара
@dp.callback_query(lambda c: c.data.startswith("details_"))
async def show_details(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    product = await sync_to_async(Product.objects.get)(id=product_id)
    await state.update_data(product_id=product_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ])
    await callback.message.answer(
        f"📦 {product.name}\n💰 Цена: {product.price}\n\n{product.description}\n\nПодтвердите заказ?",
        reply_markup=keyboard
    )
    await callback.answer()

# Подтверждение заказа → сбор имени
@dp.callback_query(lambda c: c.data == "confirm_order")
async def ask_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваше имя:")
    await state.set_state(OrderForm.name)
    await callback.answer()

# Сбор имени
@dp.message(StateFilter(OrderForm.name))
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("Введите ваш телефон:")
    await state.set_state(OrderForm.phone)

# Сбор телефона
@dp.message(StateFilter(OrderForm.phone))
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(user_phone=message.text)
    await message.answer("Введите адрес доставки:")
    await state.set_state(OrderForm.address)

# Сбор адреса и создание заказа
@dp.message(StateFilter(OrderForm.address))
async def process_address(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    product = await sync_to_async(Product.objects.get)(id=user_data["product_id"])

    # Создание заказа
    await sync_to_async(Order.objects.create)(
        product=product,
        quantity=1,
        user_name=user_data["user_name"],
        user_phone=user_data["user_phone"],
        user_address=message.text
    )

    # Сообщение пользователю
    await message.answer(
        f"✅ Ваш заказ оформлен!\n\n"
        f"📦 Товар: {product.name}\n"
        f"💰 Цена: {product.price}\n"
        f"🧑‍💼 Имя: {user_data['user_name']}\n"
        f"📞 Телефон: {user_data['user_phone']}\n"
        f"🏠 Адрес: {message.text}\n\n"
        f"Теперь вы можете просмотреть другие товары:"
    )

    # Показываем товары снова
    await show_products(message)

    # Уведомление админу
    await bot.send_message(
        ADMIN_CHAT_ID,
        f"🆕 Новый заказ!\n"
        f"Товар: {product.name}\n"
        f"Цена: {product.price}\n"
        f"Имя: {user_data['user_name']}\n"
        f"Телефон: {user_data['user_phone']}\n"
        f"Адрес: {message.text}\n"
        f"Пользователь: {message.from_user.full_name}"
    )

    await state.clear()

# Отмена заказа
@dp.callback_query(lambda c: c.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Заказ отменён")
    await state.clear()
    await callback.answer()

# Запуск бота
async def main():
    print("✅ Магазин-бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
