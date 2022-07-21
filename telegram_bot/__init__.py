from configparser import ConfigParser
from typing import Any

from telethon import TelegramClient, events, Button
from telethon.events import StopPropagation

from database import Database
from report_backend import ReportBackend, UnauthorizedError

config = ConfigParser()
config.read('config.ini')

bot = TelegramClient(
    'bot',
    config['telegram'].getint('api_id'),
    config['telegram']['api_hash']
).start(
    bot_token=config['telegram']['bot_token']
)

db = Database()
backend = ReportBackend(config['backend']['api_url'])

register_url = config['register']['register_url']


@bot.on(events.NewMessage(pattern='/start'))
async def handle_start(event: Any):
    """Обработчик команды /start. Регистрирует пользователя."""

    sender = await event.get_sender()
    await event.respond(f'Добро пожаловать, {sender.username}')

    await db.create_new_user(event.sender_id)
    await event.respond(f'Пожалуйста, получите токен для входа по ссылке {register_url} и введите его.')

    raise StopPropagation


@bot.on(events.NewMessage(pattern='/report'))
async def handle_report(event: Any):
    """Обработчик команды /report. Отправляет сообщение с выбором семестра."""

    user = await db.get_or_create_user(event.sender_id)

    try:
        semesters = await backend.fetch_semesters(user.token)
    except UnauthorizedError:
        await event.respond(
            'Ваш токен недействителен. Пожалуйста, сбросьте настройки бота командой /start.'
        )
        return

    if len(semesters) == 0:
        await event.respond('У Вас нет доступа ни к одному семестру.')
        return

    buttons = [[Button.inline(semester_name, f'sem {semester_id}')]
               for semester_id, semester_name in semesters.items()]

    await bot.send_message(event.sender_id, 'Выберите семестр:', buttons=buttons)

    raise StopPropagation


@bot.on(events.CallbackQuery(pattern=r'^sem \d+$'))
async def handle_semester_button(event: Any):
    """Обработчик колбэка кнопки выбора семестра. Отправляет сообщение с выбором предмета."""

    # см. pattern в CallbackQuery
    semester_id = int(event.data.split()[1])

    user = await db.get_or_create_user(event.sender_id)

    try:
        subjects = await backend.fetch_subjects(user.token, semester_id)
    except UnauthorizedError:
        await event.respond(
            'Ваш токен недействителен. Пожалуйста, сбросьте настройки бота командой /start.'
        )
        return

    if len(subjects) == 0:
        await event.respond('У Вас нет ни одного предмета в этом семестре.')
        return

    buttons = [[Button.inline(subject_name, f'sem {semester_id} sub {subject_id}')]
               for subject_id, subject_name in subjects.items()]

    await bot.send_message(event.sender_id, 'Выберите предмет:', buttons=buttons)


@bot.on(events.CallbackQuery(pattern=r'^sem \d+ sub \d+$'))
async def handle_subject_button(event: Any):
    """Обработчик колбэка кнопки выбора предмета. Отправляет сообщение с выбором отчёта."""

    # см. pattern в CallbackQuery
    split_data = event.data.split()
    semester_id = int(split_data[1])
    subject_id = int(split_data[3])

    user = await db.get_or_create_user(event.sender_id)

    try:
        reports = await backend.fetch_reports(user.token, semester_id, subject_id)
    except UnauthorizedError:
        await event.respond(
            'Ваш токен недействителен. Пожалуйста, сбросьте настройки бота командой /start.'
        )
        return

    if len(reports) == 0:
        await event.respond('У Вас нет ни одного отчёта по этому предмету.')
        return

    buttons = [[Button.inline(report_name, f'sem {semester_id} sub {subject_id} rep {report_id}')]
               for report_id, report_name in reports.items()]

    await bot.send_message(event.sender_id, 'Выберите отчёт:', buttons=buttons)


@bot.on(events.CallbackQuery(pattern=r'^sem \d+ sub \d+ rep \d+$'))
async def handle_report_button(event: Any):
    """Обработчик колбэка кнопки выбора отчёта. Загружает отчёт и отправляет его пользователю."""

    # см. pattern в CallbackQuery
    split_data = event.data.split()
    semester_id = int(split_data[1])
    subject_id = int(split_data[3])
    report_id = int(split_data[5])

    user = await db.get_or_create_user(event.sender_id)

    try:
        report = await backend.download_report(user.token, semester_id, subject_id, report_id)
    except UnauthorizedError:
        await event.respond(
            'Ваш токен недействителен. Пожалуйста, сбросьте настройки бота командой /start.'
        )
        return

    await bot.send_file(event.sender_id, report, caption='Ваш отчёт:')


@bot.on(events.NewMessage())
async def handle_message(event: Any):
    """Обработчик простого сообщения."""

    user = await db.get_or_create_user(event.sender_id)

    # если пользователь не зарегистрирован (у него нет токена),
    # то трактуем полученное сообщение как содержащее токен
    if user.token is None:
        await try_set_token(event.sender_id, event.message.message)
    else:
        await event.respond('Введите /report для получения отчёта.')


async def try_set_token(telegram_id: int, token: str):
    """Пытается установить токен для пользователя"""

    if await backend.check_token(token):
        await db.update_token(telegram_id, token)
        await bot.send_message(
            telegram_id,
            'Спасибо, Вы зарегистрированы!\n'
            'Введите /report для получения отчёта.'
        )
    else:
        await bot.send_message(telegram_id, f'Некорректный токен! Получите его заново: {register_url}')


bot.run_until_disconnected()
