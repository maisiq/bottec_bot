from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from cart.cart import Cart
from db.config import get_connection
from db.repository import RawSQLRepository
from utils import are_keyboards_equal

ITEMS_PER_PAGE = 6

router = Router()


# Pagination

class PaginationState(StatesGroup):
    category = State()
    subcategory = State()
    product = State()


async def get_items_by_state(data: dict, cur_state: State):
    items = []
    async with get_connection() as conn:
        repo = RawSQLRepository(conn)
        match cur_state:
            case PaginationState.category:
                items = await repo.get_categories()
            case PaginationState.subcategory:
                items = await repo.get_subcategories(data['category'])
            case PaginationState.product:
                items = await repo.get_products(data['subcategory'])
            case _:
                raise ValueError('Bad current state: ', cur_state)
    return items


async def display_page(
    message: Message | CallbackQuery,
    state: FSMContext,
    display_text: str = 'Выберите:',
):
    data = await state.get_data()
    page = data.get('page', 0)
    cur_state = await state.get_state()
    data_type = cur_state.split(':')[1]

    items = await get_items_by_state(data, cur_state)

    if not items:
        await message.answer('К сожалению, там пока ничего нет')
        return

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    show_items = items[start:end]

    builder = InlineKeyboardBuilder()

    for item in show_items:
        if data_type == 'product':
            builder.button(text=item.name, callback_data=f'{data_type}_{str(item.id)}')
        else:
            builder.button(text=item[1], callback_data=f'{data_type}_{item[0]}')

    if cur_state == PaginationState.subcategory:
        builder.button(text='↩️ Вернуться', callback_data='catalog')
    elif cur_state == PaginationState.product:
        category = data['category']
        builder.button(text='↩️ Вернуться', callback_data=f'category_{category}')

    if page > 0:
        builder.button(text="⬅️ Назад", callback_data="prev_page")
    if end < len(items):
        builder.button(text="Вперед ➡️", callback_data="next_page")

    adjust_items = [2] * int(len(items) / 2)  # [n] columns * number of rows
    builder.adjust(*adjust_items, 1, 2)

    if isinstance(message, CallbackQuery):
        await message.message.edit_text(display_text, reply_markup=builder.as_markup())
        await message.answer()
    else:
        await message.answer(display_text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "prev_page")
async def prev_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(page=data["page"] - 1)
    await display_page(callback, state)


@router.callback_query(F.data == "next_page")
async def next_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(page=data["page"] + 1)
    await display_page(callback, state)


# Handlers

@router.message(F.text.lower() == 'каталог')
async def catalog_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(PaginationState.category)
    await state.update_data(page=0)
    await display_page(message, state)


def get_product_in_cart_nav_keyboard(product_id, cart):
    kb = [
        [InlineKeyboardButton(text=f'В корзине: {cart[product_id]['quantity']} шт.', callback_data='product-info')],
        [InlineKeyboardButton(text='+', callback_data=f'product-cart_plus_{product_id}'),
         InlineKeyboardButton(text='-', callback_data=f'product-cart_minus_{product_id}')],
        [InlineKeyboardButton(text='Убрать из корзины', callback_data=f'product-cart_delete_{product_id}')]
    ]
    return kb


@router.callback_query(F.data.startswith("product_"))
async def product_detail_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PaginationState.product)
    cart = await Cart().init(state)
    product_id = callback.data.split("_")[1]

    async with get_connection() as conn:
        repo = RawSQLRepository(conn)
        product = await repo.get_product_by_id(product_id)

    kb = []

    if product_id in cart:
        kb = get_product_in_cart_nav_keyboard(product_id, cart)
    else:
        kb.append([InlineKeyboardButton(text='Добавить в корзину', callback_data=f'product-cart_add_{product_id}')])
    builder = InlineKeyboardBuilder(kb)

    caption = (
        f'Название(id): {product.name}\n'
        f'Описание: {product.description}\n'
        f'Стоимость: {str(product.price)} руб.\n'
    )

    await callback.message.bot.send_photo(
        callback.message.chat.id,
        product.image,
        caption=caption,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("subcategory_"))
async def products(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(PaginationState.product)

    _, subcategory = callback.data.split('_')
    await state.update_data(page=0, subcategory=subcategory)
    await display_page(callback, state)


@router.callback_query(F.data.startswith("category_"))
async def subcategories(callback: CallbackQuery, state: FSMContext) -> None:
    _, category = callback.data.split('_')

    await state.set_state(PaginationState.subcategory)
    await state.update_data(page=0, category=category)
    await display_page(callback, state)


@router.callback_query(F.data.startswith("product-cart"))
async def cart_handler(callback: CallbackQuery, state: FSMContext):
    _, action, product_id = callback.data.split("_")

    cart = await Cart().init(state)

    async with get_connection() as conn:
        repo = RawSQLRepository(conn)
        product = await repo.get_product_by_id(product_id)

    match action:
        case 'add' | 'plus':
            cart.add(product)
            await callback.answer('Товар добавлен в корзину')
        case 'minus':
            cart.decrease(product)
            await callback.answer('Количество товаров уменьшено')
        case 'delete':
            cart.delete(product)
            await callback.answer('Товар удален из корзины')
    await cart.save()

    kb = []

    if product_id in cart:
        kb = get_product_in_cart_nav_keyboard(product_id, cart)
    else:
        kb.append([InlineKeyboardButton(text='Добавить в корзину', callback_data=f'product-cart_add_{product_id}')])
    builder = InlineKeyboardBuilder(kb)

    curr_kb = callback.message.reply_markup.inline_keyboard
    new_kb = builder.as_markup().inline_keyboard

    if not are_keyboards_equal(curr_kb, new_kb):
        await callback.message.edit_reply_markup(callback.inline_message_id, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == 'product-info')
async def product_info_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Текущее значение конкретного товара в корзине')


@router.callback_query(F.data == 'catalog')
async def categories_on_return_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(page=0)
    await state.set_state(PaginationState.category)
    await display_page(callback, state)
