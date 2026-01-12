"""
    🌑 ShadowTikTok - Извлекатель видео из Бездны
    Модуль для скачивания контента из TikTok без водяных знаков.
"""

from .. import loader, utils
import aiohttp
import io

# 🛡️ Сакральная Структура
version = (1, 2, 0)
# meta developer: @HarutyaModules
# scope: hikka_only

@loader.tds
class ShadowTikTokMod(loader.Module):
    """
    Скачивает видео из TikTok без водяного знака.
    Исправлено: GZIP кодировка и коллизия аргументов.
    Команда: .tt <ссылка>
    """

    strings = {
        "name": "ShadowTikTok",
        "loading": "<b>🌑 Подключаюсь к потоку данных...</b>",
        "downloading": "<b>📥 Извлекаю материю (Скачивание)...</b>",
        "no_args": "<b>❌ Хозяйка, Вы не дали мне цель (Ссылку).</b>",
        "error_api": "<b>⚠️ Эфир отверг запрос. Возможно, ссылка мертва или сервис недоступен.</b>",
        "error_net": "<b>🚫 Ошибка соединения с Бездной.</b>"
    }

    strings_ru = {
        "loading": "<b>🌑 Подключаюсь к потоку данных...</b>",
        "downloading": "<b>📥 Извлекаю материю (Скачивание)...</b>",
        "no_args": "<b>❌ Хозяйка, Вы не дали мне цель (Ссылку).</b>",
        "error_api": "<b>⚠️ Эфир отверг запрос. Возможно, ссылка мертва или сервис недоступен.</b>",
        "error_net": "<b>🚫 Ошибка соединения с Бездной.</b>"
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def ttcmd(self, message):
        """<ссылка> - Скачать видео из TikTok"""
        
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        # Ищем ссылку в аргументах или в реплае
        url = None
        reply_to = None

        if args:
            url = args
            reply_to = message.reply_to_msg_id
        elif reply:
            url = reply.raw_text
            reply_to = reply.id
        
        if not url:
            await utils.answer(message, self.strings("no_args"))
            return

        # Индикатор загрузки (мы его потом удалим, чтобы было красиво)
        status_msg = await utils.answer(message, self.strings("loading"))

        # 🎭 Маскировка и настройки
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Шаг 1: Получаем метаданные (ссылку на mp4)
                async with session.post(
                    "https://www.tikwm.com/api/", 
                    data={"url": url}, 
                    headers=headers
                ) as response:
                    data = await response.json()

                if "data" not in data or "play" not in data["data"]:
                    err_msg = data.get('msg', 'Unknown Error')
                    await utils.answer(status_msg, f"{self.strings('error_api')}\nLog: {err_msg}")
                    return

                video_url = data["data"]["play"]
                title = data["data"].get("title", "ShadowTikTok Video")
                author = data["data"].get("author", {}).get("nickname", "Unknown")

                # Шаг 2: Скачиваем видео (поток)
                await utils.answer(status_msg, self.strings("downloading"))
                
                async with session.get(video_url, headers=headers) as vid_stream:
                    video_bytes = await vid_stream.read()

                # Шаг 3: Отправка
                file = io.BytesIO(video_bytes)
                file.name = f"TikTok_{author}.mp4"
                
                caption = f"<b>🎥 Author:</b> {utils.escape_html(author)}\n" \
                          f"<b>📝 Title:</b> {utils.escape_html(title)}"

                # Удаляем сообщение о загрузке
                await status_msg.delete()
                
                # Отправляем видео напрямую через клиент
                # Используем reply_to, чтобы ответить на нужное сообщение
                await self.client.send_file(
                    message.chat_id,
                    file,
                    caption=caption,
                    reply_to=reply_to
                )
                
                # Если команда была не в реплае, удаляем сообщение с командой .tt для чистоты
                if not reply:
                     await message.delete()

        except Exception as e:
            await utils.answer(status_msg, f"{self.strings('error_net')}\n<code>{e}</code>")