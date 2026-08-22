# meta developer: @Edu_kak_xochu
# meta pic: https://img.icons8.com/color/48/000000/technical.png
# meta banner: https://via.placeholder.com/300x100.png?text=Tech+Utils

import asyncio
import subprocess
import socket
import platform
import os
from telethon.tl.types import Message

from .. import loader, utils

@loader.tds
class TechUtilsMod(loader.Module):
    """Технические утилиты: пинг, DNS, порты, конвертер файлов, скриншоты"""
    
    strings = {
        "name": "TechUtils",
        "no_chats": "⚠️ <b>Технический чат не создан!</b>\n\nСоздайте командой <code>.createchats</code>",
        "ping_result": "📡 <b>Результаты пинга:</b>\n\n{results}",
        "ping_error": "❌ <b>Ошибка пинга:</b> {error}",
        "dns_result": "🌐 <b>DNS записи для {domain}:</b>\n\n{records}",
        "dns_error": "❌ <b>Ошибка DNS:</b> {error}",
        "port_open": "✅ <b>Порт {port} открыт</b>",
        "port_closed": "❌ <b>Порт {port} закрыт</b>",
        "port_scan": "🔍 <b>Сканирование портов {host}:</b>\n\n{results}",
        "converting": "🔄 <b>Конвертирую файл...</b>",
        "converted": "✅ <b>Файл сконвертирован!</b>",
        "convert_error": "❌ <b>Ошибка конвертации:</b> {error}",
        "screenshotting": "📸 <b>Делаю скриншот...</b>",
        "screenshot_done": "✅ <b>Скриншот сделан!</b>",
        "screenshot_error": "❌ <b>Ошибка скриншота:</b> {error}",
        "no_url": "⚠️ <b>Укажите URL сайта!</b>",
        "no_domain": "⚠️ <b>Укажите домен!</b>",
        "no_host": "⚠️ <b>Укажите хост!</b>",
        "no_file": "⚠️ <b>Ответьте на файл для конвертации!</b>",
    }
    
    strings_ru = {
        "no_chats": "⚠️ <b>Технический чат не создан!</b>\n\nСоздайте командой <code>.createchats</code>",
        "ping_result": "📡 <b>Результаты пинга:</b>\n\n{results}",
        "ping_error": "❌ <b>Ошибка пинга:</b> {error}",
        "dns_result": "🌐 <b>DNS записи для {domain}:</b>\n\n{records}",
        "dns_error": "❌ <b>Ошибка DNS:</b> {error}",
        "port_open": "✅ <b>Порт {port} открыт</b>",
        "port_closed": "❌ <b>Порт {port} закрыт</b>",
        "port_scan": "🔍 <b>Сканирование портов {host}:</b>\n\n{results}",
        "converting": "🔄 <b>Конвертирую файл...</b>",
        "converted": "✅ <b>Файл сконвертирован!</b>",
        "convert_error": "❌ <b>Ошибка конвертации:</b> {error}",
        "screenshotting": "📸 <b>Делаю скриншот...</b>",
        "screenshot_done": "✅ <b>Скриншот сделан!</b>",
        "screenshot_error": "❌ <b>Ошибка скриншота:</b> {error}",
        "no_url": "⚠️ <b>Укажите URL сайта!</b>",
        "no_domain": "⚠️ <b>Укажите домен!</b>",
        "no_host": "⚠️ <b>Укажите хост!</b>",
        "no_file": "⚠️ <b>Ответьте на файл для конвертации!</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "common_ports",
                [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080],
                "Порты для сканирования",
                validator=loader.validators.Series(loader.validators.Integer()),
            ),
        )

    async def pingcmd(self, message: Message):
        """Пинг хоста: .ping <host>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите хост!</b>")
            return
        
        host = args.split()[0]
        count = "-n 4" if platform.system().lower() == "windows" else "-c 4"
        
        try:
            result = subprocess.run(
                f"ping {count} {host}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            await self._send_to_tech_chat(
                message,
                f"📡 <b>Пинг {host}:</b>\n\n<code>{result.stdout[-500:]}</code>"
            )
        except subprocess.TimeoutExpired:
            await utils.answer(message, "⏱ <b>Таймаут пинга!</b>")
        except Exception as e:
            await utils.answer(message, f"❌ <b>Ошибка:</b> {e}")

    async def dnscmd(self, message: Message):
        """DNS запрос: .dns <domain>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите домен!</b>")
            return
        
        domain = args.strip()
        
        try:
            import dns.resolver
            
            records_text = ""
            
            # A записи
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                records_text += "<b>A записи:</b>\n"
                for record in a_records:
                    records_text += f"• {record}\n"
            except:
                records_text += "<b>A записи:</b> не найдены\n"
            
            # MX записи
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                records_text += "\n<b>MX записи:</b>\n"
                for record in mx_records:
                    records_text += f"• {record.exchange} (приоритет: {record.preference})\n"
            except:
                records_text += "\n<b>MX записи:</b> не найдены\n"
            
            # NS записи
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                records_text += "\n<b>NS записи:</b>\n"
                for record in ns_records:
                    records_text += f"• {record}\n"
            except:
                records_text += "\n<b>NS записи:</b> не найдены\n"
            
            await self._send_to_tech_chat(
                message,
                f"🌐 <b>DNS записи для {domain}:</b>\n\n{records_text}"
            )
            
        except ImportError:
            await utils.answer(message, "❌ <b>Установите dnspython:</b> <code>pip install dnspython</code>")
        except Exception as e:
            await utils.answer(message, f"❌ <b>Ошибка DNS:</b> {e}")

    async def portscanecmd(self, message: Message):
        """Сканирование портов: .portscan <host> [start_port] [end_port]"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите хост!</b>")
            return
        
        parts = args.split()
        host = parts[0]
        
        if len(parts) >= 3:
            start_port = int(parts[1])
            end_port = int(parts[2])
            ports = range(start_port, end_port + 1)
        else:
            ports = self.config["common_ports"]
        
        open_ports = []
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        results = ""
        if open_ports:
            results += "<b>Открытые порты:</b>\n"
            for port in open_ports:
                results += f"✅ {port}\n"
        else:
            results += "❌ <b>Открытых портов не найдено</b>"
        
        await self._send_to_tech_chat(
            message,
            f"🔍 <b>Сканирование {host}:</b>\n\n{results}"
        )

    async def convertcmd(self, message: Message):
        """Конвертация файла: ответьте на файл и напишите .convert <формат>"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        if not reply or not reply.media:
            await utils.answer(message, "⚠️ <b>Ответьте на файл!</b>")
            return
        
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите формат: .convert pdf/docx/png/jpg</b>")
            return
        
        target_format = args.strip().lower()
        
        await utils.answer(message, "🔄 <b>Конвертирую...</b>")
        
        try:
            # Скачиваем файл
            file_path = await reply.download_media()
            
            # Конвертация изображений
            if target_format in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
                from PIL import Image
                
                img = Image.open(file_path)
                output_path = f"{os.path.splitext(file_path)[0]}.{target_format}"
                img.save(output_path, target_format.upper())
                
                await self._send_to_tech_chat(
                    message,
                    f"✅ <b>Файл сконвертирован в {target_format.upper()}</b>",
                    output_path
                )
            
            # Конвертация документов
            elif target_format in ['pdf', 'docx', 'txt']:
                if target_format == 'txt':
                    import docx
                    
                    doc = docx.Document(file_path)
                    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                    
                    output_path = f"{os.path.splitext(file_path)[0]}.txt"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    
                    await self._send_to_tech_chat(
                        message,
                        f"✅ <b>Файл сконвертирован в TXT</b>",
                        output_path
                    )
                else:
                    await utils.answer(message, f"❌ <b>Конвертация в {target_format} пока не поддерживается</b>")
            else:
                await utils.answer(message, f"❌ <b>Неподдерживаемый формат: {target_format}</b>")
            
            # Удаляем временный файл
            if os.path.exists(file_path):
                os.remove(file_path)
                
        except ImportError as e:
            await utils.answer(message, f"❌ <b>Установите библиотеку:</b> {e}")
        except Exception as e:
            await utils.answer(message, f"❌ <b>Ошибка конвертации:</b> {e}")

    async def screenshotcmd(self, message: Message):
        """Скриншот сайта: .screenshot <url>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите URL!</b>")
            return
        
        url = args.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        await utils.answer(message, "📸 <b>Делаю скриншот...</b>")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            driver.save_screenshot('screenshot.png')
            driver.quit()
            
            await self._send_to_tech_chat(
                message,
                f"📸 <b>Скриншот {url}</b>",
                'screenshot.png'
            )
            
            os.remove('screenshot.png')
            
        except ImportError:
            await utils.answer(message, "❌ <b>Установите selenium:</b> <code>pip install selenium</code>")
        except Exception as e:
            await utils.answer(message, f"❌ <b>Ошибка:</b> {e}")

    async def _send_to_tech_chat(self, message, text, file=None):
        """Отправляет результат в технический чат"""
        chat_manager = self.lookup("ChatManagerMod")
        
        if chat_manager and chat_manager.chats_created:
            try:
                if file:
                    await self.client.send_file(
                        chat_manager.config["tech_chat_id"],
                        file,
                        caption=text
                    )
                else:
                    await self.client.send_message(
                        chat_manager.config["tech_chat_id"],
                        text
                    )
                await utils.answer(message, "✅ <b>Отправлено в технический чат!</b>")
            except:
                await utils.answer(message, self.strings("no_chats"))
        else:
            await utils.answer(message, self.strings("no_chats"))
