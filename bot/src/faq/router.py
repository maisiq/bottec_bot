from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import bot

router = Router()


FAQ = [
    {"question": "Как зарегистрироваться?", "answer": "Нажмите /start и следуйте инструкциям."},
    {"question": "Как изменить пароль?", "answer": "Перейдите в настройки и выберите 'Сменить пароль'."},
    {"question": "Что делать, если забыл пароль?", "answer": "Используйте функцию 'Восстановить пароль' на сайте."},
    {"question": "Как связаться с поддержкой?", "answer": "Напишите на support@example.com."},
]


@router.message(F.text.lower() == 'faq')
async def cart_handler(message: Message, state: FSMContext) -> None:
    bot_info = await bot.get_me()
    bot_info.username
    await message.answer(
        f"Задайте вопрос в формате: @{bot_info.username} *ваш вопрос*\n"
        "или связавшись с оператором @op_login"
    )


@router.inline_query()
async def inline_faq(inline_query: types.InlineQuery):
    query_text = inline_query.query.lower()
    results = []

    for idx, faq in enumerate(FAQ):
        if not query_text or query_text in faq["question"].lower():
            result = types.InlineQueryResultArticle(
                id=str(idx),
                title=faq["question"],
                description=faq["answer"][:50] + "...",
                input_message_content=types.InputTextMessageContent(
                    message_text=f"<b>{faq['question']}</b>\n{faq['answer']}",
                    parse_mode="HTML"
                )
            )
            results.append(result)

    button = types.InlineQueryResultsButton(text="Связаться с поддержкой", start_parameter="support")
    await inline_query.answer(results, is_personal=True, button=button)
