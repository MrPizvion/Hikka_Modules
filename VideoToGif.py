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
        "no_reply": "❌ <b>Ответь на видео!</b>\nПример: <code>.gif 15 10</code>",
        "not_video": "❌ <b>Это не видео!</b>",
        "loading": "🔄 <b>Создаю GIF...</b>",
        "installing": "📦 <b>Устанавливаю FFmpeg...</b>\nЭто займёт около минуты",
        "install_error": "❌ <b>Не удалось установить FFmpeg</b>\nУстанови вручную: <code>pkg install ffmpeg</code>",
        "args_error": "❌ <b>Неверные аргументы!</b>\nИспользуй: <code>.gif [fps] [размер]</code>\nFPS: 1-30, Размер: 1-20 MB",
        "fps_error": "❌ <b>FPS должен быть от 1 до 30</b>",
        "size_error": "❌ <b>Размер должен быть от 1 до 20 MB</b>",
        "success": "✅ <b>Готово!</b>\n⏱️ Время: {time}с\n🎞️ FPS: {fps}\n📁 Размер: {size} MB\n⚙️ Цель: {target_size} MB",
        "too_big": "❌ <b>GIF слишком большой!</b>\nПолучилось: {size} MB\nЦель: {target} MB\nПопробуй уменьшить FPS или размер",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🎬 VideoToGif</b>

<b>📋 Команды:</b>
<code>.gif [fps] [размер]</code> - создать GIF (ответом)

<b>✨ Примеры:</b>
<code>.gif</code> - 10 fps, 10 MB
<code>.gif 15</code> - 15 fps, 10 MB
<code>.gif 20 5</code> - 20 fps, 5 MB
<code>.gif 10 15</code> - 10 fps, 15 MB

<b>📊 Параметры:</b>
FPS: 1-30 (качество плавности)
Размер: 1-20 MB (конечный размер)

<b>⚠️ FFmpeg установится автоматически!</b>"""
    }
    
    strings_ru = {
        "name": "VideoToGif",
        "no_reply": "❌ <b>Ответь на видео!</b>\nПример: <code>.gif 15 10</code>",
        "not_video": "❌ <b>Это не видео!</b>",
        "loading": "🔄 <b>Создаю GIF...</b>",
        "installing": "📦 <b>Устанавливаю FFmpeg...</b>\nЭто займёт около минуты",
        "install_error": "❌ <b>Не удалось установить FFmpeg</b>\nУстанови вручную: <code>pkg install ffmpeg</code>",
        "args_error": "❌ <b>Неверные аргументы!</b>\nИспользуй: <code>.gif [fps] [размер]</code>\nFPS: 1-30, Размер: 1-20 MB",
        "fps_error": "❌ <b>FPS должен быть от 1 до 30</b>",
        "size_error": "❌ <b>Размер должен быть от 1 до 20 MB</b>",
        "success": "✅ <b>Готово!</b>\n⏱️ Время: {time}с\n🎞️ FPS: {fps}\n📁 Размер: {size} MB\n⚙️ Цель: {target_size} MB",
        "too_big": "❌ <b>GIF слишком большой!</b>\nПолучилось: {size} MB\nЦель: {target} MB\nПопробуй уменьшить FPS или размер",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🎬 VideoToGif</b>

<b>📋 Команды:</b>
<code>.gif [fps] [размер]</code> - создать GIF (ответом)

<b>✨ Примеры:</b>
<code>.gif</code> - 10 fps, 10 MB
<code>.gif 15</code> - 15 fps, 10 MB
<code>.gif 20 5</code> - 20 fps, 5 MB
<code>.gif 10 15</code> - 10 fps, 15 MB

<b>📊 Параметры:</b>
FPS: 1-30 (качество плавности)
Размер: 1-20 MB (конечный размер)

<b>⚠️ FFmpeg установится автоматически!</b>"""
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_fps",
                10,
                "FPS по умолчанию (1-30)",
                validator=loader.validators.Integer(minimum=1, maximum=30)
            ),
            loader.ConfigValue(
                "default_size",
                10,
                "Размер по умолчанию в MB (1-20)",
                validator=loader.validators.Integer(minimum=1, maximum=20)
            ),
            loader.ConfigValue(
                "auto_delete",
                True,
                "Удалять исходное видео",
                validator=loader.validators.Boolean()
            )
        )
        self.ffmpeg_checked = False
        self.ffmpeg_available = False
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
    
    async def _check_ffmpeg(self, message=None):
        """Проверяет наличие ffmpeg и устанавливает если нет"""
        if self.ffmpeg_checked:
            return self.ffmpeg_available
        
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
        
        if not self.ffmpeg_available and message:
            # Пытаемся установить ffmpeg
            status = await utils.answer(message, self.strings("installing"))
            
            try:
                # Обновляем пакеты
                process = await asyncio.create_subprocess_exec(
                    "pkg", "update", "-y",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # Устанавливаем ffmpeg
                process = await asyncio.create_subprocess_exec(
                    "pkg", "install", "ffmpeg", "-y",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # Проверяем снова
                process = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                self.ffmpeg_available = process.returncode == 0
                
                if self.ffmpeg_available:
                    await utils.answer(status, "✅ <b>FFmpeg успешно установлен!</b>")
                else:
                    await utils.answer(status, self.strings("install_error"))
                    
            except Exception as e:
                logger.error(f"FFmpeg installation error: {e}")
                await utils.answer(status, self.strings("install_error"))
        
        self.ffmpeg_checked = True
        return self.ffmpeg_available
    
    async def gifcmd(self, message):
        """.gif [fps] [размер] - Создать GIF из видео (ответом)"""
        
        # Проверяем ответ
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("no_reply"))
            return
        
        # Проверяем видео
        if not reply.video and not reply.document:
            await utils.answer(message, self.strings("not_video"))
            return
        
        # Проверяем/устанавливаем ffmpeg
        if not await self._check_ffmpeg(message):
            return
        
        # Парсим аргументы
        args = utils.get_args_raw(message).split()
        fps = self.config["default_fps"]
        target_size = self.config["default_size"]
        
        if len(args) >= 1 and args[0]:
            try:
                fps = int(args[0])
                if fps < 1 or fps > 30:
                    await utils.answer(message, self.strings("fps_error"))
                    return
            except:
                await utils.answer(message, self.strings("args_error"))
                return
        
        if len(args) >= 2 and args[1]:
            try:
                target_size = int(args[1])
                if target_size < 1 or target_size > 20:
                    await utils.answer(message, self.strings("size_error"))
                    return
            except:
                await utils.answer(message, self.strings("args_error"))
                return
        
        # Создаём временные файлы
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"/data/data/com.termux/files/home/Hikka/temp/video_{timestamp}.mp4"
        gif_path = f"/data/data/com.termux/files/home/Hikka/temp/gif_{timestamp}.gif"
        
        os.makedirs("/data/data/com.termux/files/home/Hikka/temp", exist_ok=True)
        
        # Отправляем статус
        msg = await utils.answer(message, self.strings("loading"))
        
        try:
            # Скачиваем видео
            await reply.download_media(file=video_path)
            
            # Получаем информацию о видео
            probe = await asyncio.create_subprocess_exec(
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await probe.communicate()
            dimensions = stdout.decode().strip().split('\n')
            
            # Определяем размер для масштабирования
            if len(dimensions) >= 2 and dimensions[0] and dimensions[1]:
                width = int(dimensions[0])
                height = int(dimensions[1])
                
                # Вычисляем новый размер в зависимости от целевого MB
                if target_size <= 5:
                    scale = "320:-1"  # Маленький
                elif target_size <= 10:
                    scale = "480:-1"  # Средний
                elif target_size <= 15:
                    scale = "640:-1"  # Большой
                else:
                    scale = "800:-1"  # Очень большой
            else:
                scale = "480:-1"
            
            # Конвертируем в GIF
            start_time = datetime.now()
            
            # Пробуем сначала с указанными параметрами
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"fps={fps},scale={scale}:flags=lanczos",
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
                gif_size = os.path.getsize(gif_path) / (1024 * 1024)  # в MB
                
                # Если получилось больше чем нужно, пробуем сжать
                if gif_size > target_size:
                    # Уменьшаем FPS и размер
                    new_fps = max(5, fps - 5)
                    new_scale = "320:-1" if scale != "320:-1" else "240:-1"
                    
                    cmd2 = [
                        "ffmpeg",
                        "-i", video_path,
                        "-vf", f"fps={new_fps},scale={new_scale}:flags=lanczos",
                        "-c:v", "gif",
                        "-y",
                        gif_path
                    ]
                    
                    process2 = await asyncio.create_subprocess_exec(
                        *cmd2,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await process2.communicate()
                    
                    if os.path.exists(gif_path):
                        gif_size = os.path.getsize(gif_path) / (1024 * 1024)
                        fps = new_fps
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Проверяем итоговый размер
                if gif_size > 20:  # Больше 20 MB нельзя отправить
                    await utils.answer(msg, self.strings("too_big").format(
                        size=round(gif_size, 1),
                        target=target_size
                    ))
                    if os.path.exists(gif_path):
                        os.remove(gif_path)
                    return
                
                # Отправляем GIF
                await self.client.send_file(
                    message.to_id,
                    gif_path,
                    reply_to=reply.id if reply else None,
                    caption=self.strings("success").format(
                        time=round(duration, 1),
                        fps=fps,
                        size=round(gif_size, 1),
                        target_size=target_size
                    )
                )
                
                # Удаляем временные файлы
                if os.path.exists(gif_path):
                    os.remove(gif_path)
            else:
                raise Exception("GIF file not created")
            
        except Exception as e:
            logger.exception(f"GIF creation error: {e}")
            await utils.answer(msg, self.strings("error").format(str(e)))
        
        finally:
            # Удаляем видео если осталось
            if os.path.exists(video_path):
                try:
                    if self.config["auto_delete"]:
                        os.remove(video_path)
                except:
                    pass
