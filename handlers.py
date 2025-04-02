import hashlib
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from questions import get_question
from gpt_helper import ask_gpt
from certificate import generate_certificate  # Импортируем функцию генерации сертификата
from aiogram.fsm.state import State, StatesGroup  # Импортируем State и StatesGroup
router = Router()

# Словари для отслеживания состояния пользователей
user_scores = {}
user_progress = {}

def safe_callback_data(option_text):
    return hashlib.md5(option_text.encode()).hexdigest()[:16]  # Обрезаем до 16 символов


# Главное меню (изменяем, чтобы блокировать "Викторину")
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Описание и правила")] # "Викторина" отключена во время прохождения
    ],
    resize_keyboard=True
)

menu_keyboard_quiz_active = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Описание и правила")],
        [KeyboardButton(text="🧠 Викторина")],
    ],
    resize_keyboard=True
)

# Обработчик кнопки "📜 Описание и правила"
@router.message(lambda message: message.text == "📜 Описание и правила")
async def show_rules(message: types.Message):
    rules_text = (
        "🧠 Добро пожаловать в AI Quiz!\n\n"
        "🔹 Викторина состоит из нескольких вопросов по AI.\n"
        "🔹 За каждый правильный ответ начисляются баллы.\n"
        "🔹 Можно посмотреть подсказку, если вопрос сложный.\n"
        "🔹 В конце викторины можно получить сертификат.\n\n"
        "💡 Готов начать? Жми '🧠 Викторина'!"
    )
    await message.answer(rules_text)

# Обработчик кнопки "🧠 Викторина" (начало викторины)
@router.message(lambda message: message.text == "🧠 Викторина")
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    user_scores[user_id] = 0  # Обнуляем счет
    user_progress[user_id] = 0  # Устанавливаем первый вопрос

    await message.answer("🧠 Начинаем викторину!", reply_markup=menu_keyboard)
    await send_question(message, user_id)




# Функция отправки вопроса с номерами вариантов
async def send_question(message: types.Message, user_id: int):
    index = user_progress.get(user_id, 0)
    question_data = get_question(index)

    if question_data is None:
        await message.answer(
            f"🎉 Викторина завершена! Ваш результат: {user_scores[user_id]} баллов.\n\n"
            "Вы можете получить сертификат!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🎓 Сертификат")]],
                resize_keyboard=True
            )
        )
        return

    if question_data:
        question_text, options, correct_answer, hint = question_data

        emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

        # Формируем текст вопроса с нумерацией через эмодзи
        question_text_formatted = f"🧐 Вопрос {index + 1}:\n\n{question_text}\n\n"
        for i, option in enumerate(options):
            question_text_formatted += f"{emoji_numbers[i]} {option}\n"

        # Inline-кнопки с номерами
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=str(i), callback_data=f"answer_{i}") for i in range(1, len(options) + 1)]
            ] + [[InlineKeyboardButton(text="🤔 Подсказка", callback_data="show_hint")]]
        )

        # Сохраняем правильный ответ
        user_progress[user_id] = (index, correct_answer)

        await message.answer(question_text_formatted, reply_markup=keyboard)





# Обработчик ответов
@router.callback_query(lambda c: c.data.startswith("answer_"))
async def check_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Получаем текущий индекс вопроса и правильный ответ
    index, correct_answer = user_progress.get(user_id, (0, None))
    question_data = get_question(index)

    if not question_data:
        await callback.answer("Ошибка! Вопрос не найден.")
        return

    _, options, correct_answer, _ = question_data  # Получаем варианты и правильный ответ

    # Получаем номер ответа пользователя
    user_choice = int(callback.data.split("_")[1])  # Получаем число после "answer_"

    # Определяем правильный номер ответа (по позиции в списке)
    correct_index = options.index(correct_answer) + 1  # +1, так как нумерация с 1

    if user_choice == correct_index:
        user_scores[user_id] += 1
        text = "✅ Верно! Отличная работа!"
    else:
        text = f"❌ Неверно. Правильный ответ: {correct_index}. {correct_answer}"

    await callback.message.answer(text)

    # Переход к следующему вопросу
    user_progress[user_id] = index + 1

    await send_question(callback.message, user_id)


# Класс состояний для получения ФИО
class CertificateState(StatesGroup):
    waiting_for_name = State()


# Обработчик кнопки "Сертификат"
@router.message(lambda message: message.text == "🎓 Сертификат")
async def request_certificate(message: types.Message, state: FSMContext):
    await message.answer("Введите свою Фамилию Имя для сертификата:")
    await state.set_state(CertificateState.waiting_for_name)


# Обработчик ввода ФИО
@router.message(CertificateState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.text
    user_score = user_scores.get(user_id, 0)  # Получаем баллы

    # Генерируем сертификат
    certificate_path = generate_certificate(user_name, user_score)

    # Отправляем сертификат
    await message.answer_document(types.FSInputFile(certificate_path), caption="🎓 Ваш сертификат!")
    # Отправляем дополнительное сообщение с ссылкой
    await message.answer(
        "Если хочешь учиться программированию бесплатно целый год, пройди по ссылке: "
        "[VK Клуб 1С](https://vk.com/1c_club_kostroma?ref=group_menu&w=app6094020_-96428497)",
        parse_mode="Markdown"
    )
    # Показываем кнопки снова после отправки сертификата
    await message.answer("Можно пройти викторину еще раз", reply_markup=menu_keyboard_quiz_active)

    await state.clear()



# Обработчик кнопки "🤔 Подсказка"
@router.callback_query(lambda c: c.data == "show_hint")
async def show_hint(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    index, _ = user_progress.get(user_id, (0, None))

    question_data = get_question(index)

    if question_data:
        _, _, _, hint = question_data  # Получаем подсказку
        await callback.message.answer(f"💡 Подсказка:\n\n{hint}")
    else:
        await callback.message.answer("🚫 Подсказка недоступна.")

# Добавляем обработчики в диспетчер
def setup_handlers(dp):
    dp.include_router(router)