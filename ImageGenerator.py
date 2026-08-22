# meta developer: @Edu_kak_xochu
# meta pic: https://img.icons8.com/color/48/000000/image.png
# meta banner: https://via.placeholder.com/300x100.png?text=Image+Generator

import asyncio
import aiohttp
import random
import urllib.parse
from telethon.tl.types import Message

from .. import loader, utils

@loader.tds
class ImageGeneratorMod(loader.Module):
    """Генератор изображений (без ограничений)"""
    
    strings = {
        "name": "ImageGenerator",
        "no_chats": "⚠️ <b>AI чат не создан!</b>\n\nСоздайте командой <code>.createchats</code>",
        "generating": "🎨 <b>Генерирую изображение...</b>",
        "generated": "✅ <b>Изображение сгенерировано!</b>",
        "error": "❌ <b>Ошибка генерации:</b> {error}",
        "no_prompt": "⚠️ <b>Введите описание изображения!</b>",
        "styles": "🎨 <b>Доступные стили:</b>\n\n1. Реалистичный\n2. Аниме\n3. Арт\n4. 3D\n5. Пиксель-арт\n\nИспользуйте: <code>.img &lt;стиль&gt; &lt;описание&gt;</code>",
    }
    
    strings_ru = {
        "no_chats": "⚠️ <b>AI чат не создан!</b>\n\nСоздайте командой <code>.createchats</code>",
        "generating": "🎨 <b>Генерирую изображение...</b>",
        "generated": "✅ <b>Изображение сгенерировано!</b>",
        "error": "❌ <b>Ошибка генерации:</b> {error}",
        "no_prompt": "⚠️ <b>Введите описание изображения!</b>",
        "styles": "🎨 <b>Доступные стили:</b>\n\n1. Реалистичный\n2. Аниме\n3. Арт\n4. 3D\n5. Пиксель-арт\n\nИспользуйте: <code>.img &lt;стиль&gt; &lt;описание&gt;</code>",
    }

    def __init__(self):
        self.styles = {
            1: "realistic",
            2: "anime",
            3: "artistic",
            4: "3d-render",
            5: "pixel-art",
        }

    async def imgcmd(self, message: Message):
        """Генерация изображения: .img <стиль> <описание>"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("styles"))
            return
        
        parts = args.split(maxsplit=1)
        
        if len(parts) == 1:
            style_num = 1
            prompt = parts[0]
        else:
            try:
                style_num = int(parts[0])
                if style_num not in self.styles:
                    await utils.answer(message, self.strings("styles"))
                    return
                prompt = parts[1]
            except ValueError:
                style_num = 1
                prompt = args
        
        if not prompt:
            await utils.answer(message, self.strings("no_prompt"))
            return
        
        await utils.answer(message, self.strings("generating"))
        
        style = self.styles[style_num]
        
        try:
            # Генерируем URL изображения
            image_url = self._generate_image_url(prompt, style)
            
            # Отправляем в AI чат
            chat_manager = self.lookup("ChatManagerMod")
            if chat_manager and chat_manager.chats_created:
                try:
                    chat_id = int(chat_manager.config["ai_chat_id"])
                    
                    # Скачиваем и отправляем изображение
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_url) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                
                                # Сохраняем во временный файл
                                import tempfile
                                import os
                                
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                                    tmp_file.write(image_data)
                                    tmp_path = tmp_file.name
                                
                                # Отправляем в чат
                                await self.client.send_file(
                                    chat_id,
                                    tmp_path,
                                    caption=f"🎨 <b>Сгенерировано:</b>\n{prompt}\n\n<b>Стиль:</b> {style}"
                                )
                                
                                # Удаляем временный файл
                                os.remove(tmp_path)
                                
                                await utils.answer(message, self.strings("generated"))
                            else:
                                await utils.answer(message, self.strings("error").format(error="Не удалось получить изображение"))
                except Exception as e:
                    await utils.answer(message, self.strings("error").format(error=str(e)))
            else:
                await utils.answer(message, self.strings("no_chats"))
                
        except Exception as e:
            await utils.answer(message, self.strings("error").format(error=str(e)))

    def _generate_image_url(self, prompt, style):
        """Генерирует URL изображения"""
        query = urllib.parse.quote(prompt)
        random_num = random.randint(1, 1000)
        
        # Добавляем стиль к запросу
        style_keywords = {
            "realistic": "realistic,photography",
            "anime": "anime,manga",
            "artistic": "art,painting",
            "3d-render": "3d,render",
            "pixel-art": "pixel,art",
        }
        
        style_query = style_keywords.get(style, "")
        
        # Используем Unsplash Source API (бесплатный, без ограничений)
        if style_query:
            url = f"https://source.unsplash.com/800x600/?{query},{style_query}"
        else:
            url = f"https://source.unsplash.com/800x600/?{query}"
        
        return url
