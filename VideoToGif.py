from .. import loader, utils
import os
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@loader.tds
class VideoToGifMod(loader.Module):
    """Создание GIF из видео 🎬➡️🎞️"""
    
    strings = {
        "name": "VideoToGif",
        "no_reply": "❌ <b>Ответь на видео!</b>\nПример: <code>.gif 15 10</code>",
        "not_video": "❌ <b>Это не видео!</b>",
        "downloading": "📥 <b>Скачиваю видео...</b>",
        "converting": "🔄 <b>Конвертирую в GIF...</b>",
        "uploading": "📤 <b>Отправляю...</b>",
        "args_error": "❌ <b>Используй:</b> <code>.gif [fps] [размер]</code>\nFPS: 1-30, Размер: 1-20 MB",
        "fps_error": "❌ <b>FPS от 1 до 30</b>",
        "size_error": "❌ <b>Размер от 1 до 20 MB</b>",
        "success": "✅ <b>Готово!</b>\n🎞️ {fps} FPS | 📁 {size} MB | ⏱️ {time}с",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🎬 VideoToGif</b>

<code>.gif [fps] [размер]</code> - ответом на видео

<b>✨ Примеры:</b>
<code>.gif</code> - 10 fps, 10 MB
<code>.gif 15</code> - 15 fps, 10 MB
<code>.gif 20 5</code> - 20 fps, 5 MB

<b>📊 Параметры:</b>
FPS: 1-30 (плавность)
Размер: 1-20 MB (конечный размер)

<b>⚡ Требуется FFmpeg:</b>
<code>pkg install ffmpeg</code>"""
    }
    
    strings_ru = {
        "name": "VideoToGif",
        "no_reply": "❌ <b>Ответь на видео!</b>\nПример: <code>.gif 15 10</code>",
        "not_video": "❌ <b>Это не видео!</b>",
        "downloading": "📥 <b>Скачиваю видео...</b>",
        "converting": "🔄 <b>Конвертирую в GIF...</b>",
        "uploading": "📤 <b>Отправляю...</b>",
        "args_error": "❌ <b>Используй:</b> <code>.gif [fps] [размер]</code>\nFPS: 1-30, Размер: 1-20 MB",
        "fps_error": "❌ <b>FPS от 1 до 30</b>",
        "size_error": "❌ <b>Размер от 1 до 20 MB</b>",
        "success": "✅ <b>Готово!</b>\n🎞️ {fps} FPS | 📁 {size} MB | ⏱️ {time}с",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🎬 VideoToGif</b>

<code>.gif [fps] [размер]</code> - ответом на видео

<b>✨ Примеры:</b>
<code>.gif</code> - 10 fps, 10 MB
<code>.gif 15</code> - 15 fps, 10 MB
<code>.gif 20 5</code> - 20 fps, 5 MB

<b>📊 Параметры:</b>
FPS: 1-30 (плавность)
Размер: 1-20 MB (конечный размер)

<b>⚡ Требуется FFmpeg:</b>
<code>pkg install ffmpeg</code>"""
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("default_fps", 10, "FPS (1-30)"),
            loader.ConfigValue("default_size", 10, "Размер MB (1-20)"),
        )
        self.ffmpeg_checked = False
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        
        # Проверяем FFmpeg
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
    
    async def gifcmd(self, message):
        """Создать GIF из видео"""
        if not self.ffmpeg_available:
            await utils.answer(message, "❌ <b>FFmpeg не найден!</b>\nУстанови: <code>pkg install ffmpeg</code>")
            return
        
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("no_reply"))
            return
        
        if not reply.video and not reply.document:
            await utils.answer(message, self.strings("not_video"))
            return
        
        # Парсим аргументы
        args = utils.get_args_raw(message).split()
        fps = self.config["default_fps"]
        target_size = self.config["default_size"]
        
        if len(args) >= 1 and args[0]:
            try:
                fps = int(args[0])
                if not 1 <= fps <= 30:
                    return await utils.answer(message, self.strings("fps_error"))
            except:
                return await utils.answer(message, self.strings("args_error"))
        
        if len(args) >= 2 and args[1]:
            try:
                target_size = int(args[1])
                if not 1 <= target_size <= 20:
                    return await utils.answer(message, self.strings("size_error"))
            except:
                return await utils.answer(message, self.strings("args_error"))
        
        # Создаём временные файлы
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"/data/data/com.termux/files/home/Hikka/temp/video_{timestamp}.mp4"
        gif_path = f"/data/data/com.termux/files/home/Hikka/temp/gif_{timestamp}.gif"
        
        os.makedirs("/data/data/com.termux/files/home/Hikka/temp", exist_ok=True)
        
        try:
            # Скачиваем
            msg = await utils.answer(message, self.strings("downloading"))
            await reply.download_media(file=video_path)
            
            # Конвертируем
            await utils.answer(msg, self.strings("converting"))
            start_time = datetime.now()
            
            # Определяем размер
            if target_size <= 5:
                scale = "320:-1"
            elif target_size <= 10:
                scale = "480:-1"
            elif target_size <= 15:
                scale = "640:-1"
            else:
                scale = "800:-1"
            
            # Конвертируем в GIF с оптимизацией
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"fps={fps},scale={scale}:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                "-c:v", "gif",
                "-y",
                gif_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            # Проверяем размер
            if os.path.exists(gif_path):
                gif_size = os.path.getsize(gif_path) / (1024 * 1024)
                
                # Если больше 20 MB - ошибка
                if gif_size > 20:
                    os.remove(gif_path)
                    await utils.answer(msg, f"❌ <b>Слишком большой!</b> {round(gif_size, 1)} MB")
                    return
                
                # Отправляем
                await utils.answer(msg, self.strings("uploading"))
                
                await self.client.send_file(
                    message.to_id,
                    gif_path,
                    reply_to=reply.id,
                    video_note=False,
                    attributes=[],  # Пустые атрибуты = GIF
                    force_document=False,  # Не как файл
                    caption=self.strings("success").format(
                        fps=fps,
                        size=round(gif_size, 1),
                        time=round((datetime.now() - start_time).total_seconds(), 1)
                    )
                )
                
                # Удаляем
                os.remove(gif_path)
            
            # Удаляем видео
            if os.path.exists(video_path):
                os.remove(video_path)
            
        except Exception as e:
            logger.exception(f"GIF error: {e}")
            await utils.answer(message, self.strings("error").format(str(e)))
            
            # Чистим файлы
            for path in [video_path, gif_path]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
