from .. import loader, utils
import os
import asyncio
import logging
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

# requires: ffmpeg

@loader.tds
class VideoToGifMod(loader.Module):
    """Модуль для создания GIF из видео 🎬➡️🎞️"""
    
    strings = {
        "name": "VideoToGif",
        "no_reply": "❌ <b>Ответь на видео!</b>\nПример: <code>.gif 10</code> (10 fps)",
        "not_video": "❌ <b>Это не видео!</b>",
        "loading": "🔄 <b>Создаю GIF...</b>",
        "fps_error": "❌ <b>Укажи число FPS от 1 до 30</b>",
        "success": "✅ <b>Готово!</b>\n⏱️ Время: {time}с\n🎞️ FPS: {fps}\n📁 Размер: {size} MB",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🎬 VideoToGif</b>

<b>📋 Команды:</b>
<code>.gif [fps]</code> - создать GIF из видео (ответом)
<code>.gif 15</code> - создать GIF с 15 FPS
<code>.gif 10</code> - создать GIF с 10 FPS

<b>✨ Примеры:</b>
1. Ответь на видео: <code>.gif 10</code>
2. Ответь на видео: <code>.gif 20</code>

<b>⚠️ FPS:</b> 1-30 (чем выше, тем больше размер)"""
    }
    
    strings_ru = {
        "name": "VideoToGif",
        "no_reply": "❌ <b>Ответь на видео!</b>\nПример: <code>.gif 10</code> (10 кадров/сек)",
        "not_video": "❌ <b>Это не видео!</b>",
        "loading": "🔄 <b>Создаю GIF...</b>",
        "fps_error": "❌ <b>Укажи число FPS от 1 до 30</b>",
        "success": "✅ <b>Готово!</b>\n⏱️ Время: {time}с\n🎞️ FPS: {fps}\n📁 Размер: {size} MB",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🎬 VideoToGif</b>

<b>📋 Команды:</b>
<code>.gif [fps]</code> - создать GIF из видео (ответом)
<code>.gif 15</code> - создать GIF с 15 FPS
<code>.gif 10</code> - создать GIF с 10 FPS

<b>✨ Примеры:</b>
1. Ответь на видео: <code>.gif 10</code>
2. Ответь на видео: <code>.gif 20</code>

<b>⚠️ FPS:</b> 1-30 (чем выше, тем больше размер)"""
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "max_size",
                20,
                "Максимальный размер GIF в MB",
                validator=loader.validators.Integer(minimum=1, maximum=50)
            ),
            loader.ConfigValue(
                "default_fps",
                10,
                "FPS по умолчанию",
                validator=loader.validators.Integer(minimum=1, maximum=30)
            ),
            loader.ConfigValue(
                "auto_delete",
                True,
                "Автоматически удалять исходное видео",
                validator=loader.validators.Boolean()
            )
        )
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        
        # Проверяем наличие ffmpeg
        try:
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            self.ffmpeg_available = process.returncode == 0
        except:
            self.ffmpeg_available = False
            
        if not self.ffmpeg_available:
            logger.warning("FFmpeg не найден! Установи: pkg install ffmpeg")
    
    async def gifcmd(self, message):
        """.gif [fps] - Создать GIF из видео (ответом)"""
        if not self.ffmpeg_available:
            await utils.answer(message, "❌ <b>FFmpeg не установлен!</b>\nУстанови: <code>pkg install ffmpeg</code>")
            return
        
        # Проверяем, есть ли ответ на сообщение
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("no_reply"))
            return
        
        # Проверяем, что это видео
        if not reply.video and not reply.document:
            await utils.answer(message, self.strings("not_video"))
            return
        
        # Получаем FPS из аргументов
        args = utils.get_args_raw(message)
        fps = self.config["default_fps"]
        
        if args:
            try:
                fps = int(args)
                if fps < 1 or fps > 30:
                    raise ValueError
            except:
                await utils.answer(message, self.strings("fps_error"))
                return
        
        # Создаём временные файлы
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"/data/data/com.termux/files/home/Hikka/temp/video_{timestamp}.mp4"
        gif_path = f"/data/data/com.termux/files/home/Hikka/temp/gif_{timestamp}.gif"
        
        # Создаём папку temp если её нет
        os.makedirs("/data/data/com.termux/files/home/Hikka/temp", exist_ok=True)
        
        # Отправляем статус
        msg = await utils.answer(message, self.strings("loading"))
        
        try:
            # Скачиваем видео
            await reply.download_media(file=video_path)
            
            # Конвертируем в GIF
            start_time = datetime.now()
            
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"fps={fps},scale=480:-1:flags=lanczos",
                "-c:v", "gif",
                "-y",  # Перезаписывать если есть
                gif_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Проверяем размер
            gif_size = os.path.getsize(gif_path) / (1024 * 1024)  # в MB
            
            if gif_size > self.config["max_size"]:
                os.remove(gif_path)
                await utils.answer(msg, f"❌ <b>GIF слишком большой!</b> ({gif_size:.1f} MB)\nМаксимум: {self.config['max_size']} MB\nПопробуй уменьшить FPS")
                return
            
            # Отправляем GIF
            await self.client.send_file(
                message.to_id,
                gif_path,
                reply_to=reply.id if reply else None,
                caption=self.strings("success").format(
                    time=round(duration, 1),
                    fps=fps,
                    size=round(gif_size, 1)
                )
            )
            
            # Удаляем временные файлы
            os.remove(gif_path)
            if self.config["auto_delete"] and os.path.exists(video_path):
                os.remove(video_path)
            
        except Exception as e:
            logger.exception(f"GIF creation error: {e}")
            await utils.answer(msg, self.strings("error").format(str(e)))
        
        finally:
            # Удаляем видео если осталось
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except:
                    pass
