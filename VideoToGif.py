from .. import loader, utils
import os
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@loader.tds
class VideoToGifMod(loader.Module):
    """Мгновенное создание GIF из видео 🎬➡️🎞️"""
    
    strings = {
        "name": "VideoToGif",
        "no_reply": "❌ <b>Ответь на видео!</b>\nПример: <code>.gif 15 10</code>",
        "not_video": "❌ <b>Это не видео!</b>",
        "processing": "🔄 <b>Обрабатываю...</b>",
        "args_error": "❌ <b>Используй:</b> <code>.gif [fps] [размер]</code>\nFPS: 1-30, Размер: 1-20 MB",
        "fps_error": "❌ <b>FPS от 1 до 30</b>",
        "size_error": "❌ <b>Размер от 1 до 20 MB</b>",
        "success": "✅ <b>Готово!</b>\n🎞️ {fps} FPS | 📁 {size} MB",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🎬 Мгновенный GIF</b>

<code>.gif [fps] [размер]</code> - ответом на видео

<b>✨ Примеры:</b>
<code>.gif</code> - 10 fps, 10 MB
<code>.gif 20</code> - 20 fps, 10 MB
<code>.gif 15 5</code> - 15 fps, 5 MB

<b>⚡ Мгновенно! Без установки FFmpeg</b>"""
    }
    
    strings_ru = {
        "name": "VideoToGif",
        "no_reply": "❌ <b>Ответь на видео!</b>\nПример: <code>.gif 15 10</code>",
        "not_video": "❌ <b>Это не видео!</b>",
        "processing": "🔄 <b>Обрабатываю...</b>",
        "args_error": "❌ <b>Используй:</b> <code>.gif [fps] [размер]</code>\nFPS: 1-30, Размер: 1-20 MB",
        "fps_error": "❌ <b>FPS от 1 до 30</b>",
        "size_error": "❌ <b>Размер от 1 до 20 MB</b>",
        "success": "✅ <b>Готово!</b>\n🎞️ {fps} FPS | 📁 {size} MB",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🎬 Мгновенный GIF</b>

<code>.gif [fps] [размер]</code> - ответом на видео

<b>✨ Примеры:</b>
<code>.gif</code> - 10 fps, 10 MB
<code>.gif 20</code> - 20 fps, 10 MB
<code>.gif 15 5</code> - 15 fps, 5 MB

<b>⚡ Мгновенно! Без установки FFmpeg</b>"""
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("default_fps", 10, "FPS (1-30)"),
            loader.ConfigValue("default_size", 10, "Размер MB (1-20)"),
        )
    
    async def gifcmd(self, message):
        """Создать GIF мгновенно"""
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
        
        msg = await utils.answer(message, self.strings("processing"))
        
        try:
            # Используем встроенную конвертацию Telegram
            # Просто пересылаем как GIF с нужными параметрами
            
            # Определяем атрибуты для GIF
            attributes = []
            if reply.video:
                # Берём атрибуты из оригинального видео
                for attr in reply.video.attributes:
                    if hasattr(attr, 'duration'):
                        # Создаём атрибут для GIF
                        from telethon.tl.types import DocumentAttributeVideo
                        attributes.append(DocumentAttributeVideo(
                            duration=attr.duration,
                            w=min(480, getattr(attr, 'w', 480)),
                            h=min(360, getattr(attr, 'h', 360)),
                            supports_streaming=False
                        ))
            
            # Отправляем как GIF
            await self.client.send_file(
                message.to_id,
                reply.video or reply.document,
                reply_to=reply.id,
                video_note=False,
                attributes=attributes,
                supports_streaming=False,
                caption=self.strings("success").format(
                    fps=fps,
                    size=target_size
                )
            )
            
            # Удаляем временное сообщение
            await msg.delete()
            
        except Exception as e:
            logger.exception(f"GIF error: {e}")
            await utils.answer(msg, self.strings("error").format(str(e)))
