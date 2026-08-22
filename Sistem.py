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
        "help": "📖 <b>Команды TechUtils:</b>\n\n<b>.tping</b> - пинг хоста\n<b>.tdns</b> - DNS запросы\n<b>.tport</b> - сканирование портов\n<b>.tconvert</b> - конвертация файлов\n<b>.tscreen</b> - скриншот сайта\n<b>.techhelp</b> - справка",
    }
    
    strings_ru = {
        "no_chats": "⚠️ <b>Технический чат не создан!</b>\n\nСоздайте командой <code>.createchats</code>",
        "ping_result": "📡 <b>Результаты пинга:</b>\n\n{results}",
        "ping_error": "❌ <b>Ошибка пинга:</b> {error}",
        "dns_result": "🌐 <b>DNS записи для {domain}:</b>\n\n{records}",
        "dns_error": "❌ <b>Ошибка DNS:</b> {error}",
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
        "help": "📖 <b>Команды TechUtils:</b>\n\n<b>.tping</b> - пинг хоста\n<b>.tdns</b> - DNS запросы\n<b>.tport</b> - сканирование портов\n<b>.tconvert</b> - конвертация файлов\n<b>.tscreen</b> - скриншот сайта\n<b>.techhelp</b> - справка",
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

    @loader.command()
    async def tpingcmd(self, message: Message):
        """Пинг хоста: .tping <host>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите хост!</b>\n\nПример: <code>.tping google.com</code>")
            return
        
        host = args.split()[0]
        count = "-n 4" if platform.system().lower() == "windows" else "-c 4"
        
        await utils.answer(message, f"📡 <b>Пингую {host}...</b>")
        
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

    @loader.command()
    async def tdnscmd(self, message: Message):
        """DNS запрос: .tdns <domain>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите домен!</b>\n\nПример: <code>.tdns google.com</code>")
            return
        
        domain = args.strip()
        
        await utils.answer(message, f"🌐 <b>Запрашиваю DNS для {domain}...</b>")
        
        try:
            import dns.resolver
            
            records_text = ""
            
            # A записи
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                records_text += "<b>A записи:</b>\n"
                for record in a_records[:5]:
                    records_text += f"• {record}\n"
            except:
                records_text += "<b>A записи:</b> не найдены\n"
            
            # MX записи
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                records_text += "\n<b>MX записи:</b>\n"
                for record in mx_records[:5]:
                    records_text += f"• {record.exchange} (приоритет: {record.preference})\n"
            except:
                records_text += "\n<b>MX записи:</b> не найдены\n"
            
            # NS записи
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                records_text += "\n<b>NS записи:</b>\n"
                for record in ns_records[:5]:
                    records_text += f"• {record}\n"
            except:
                records_text += "\n<b>NS записи:</b> не найдены\n"
            
            # TXT записи
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                records_text += "\n<b>TXT записи:</b>\n"
                for record in txt_records[:3]:
                    records_text += f"• {record}\n"
            except:
                pass
            
            await self._send_to_tech_chat(
                message,
                f"🌐 <b>DNS записи для {domain}:</b>\n\n{records_text}"
            )
            
        except ImportError:
            await utils.answer(message, "❌ <b>Установите dnspython:</b> <code>pip install dnspython</code>")
        except Exception as e:
            await utils.answer(message, f"❌ <b>Ошибка DNS:</b> {e}")

    @loader.command()
    async def tportcmd(self, message: Message):
        """Сканирование портов: .tport <host> [start_port] [end_port]"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите хост!</b>\n\nПример: <code>.tport example.com</code> или <code>.tport example.com 80 1000</code>")
            return
        
        parts = args.split()
        host = parts[0]
        
        if len(parts) >= 3:
            try:
                start_port = int(parts[1])
                end_port = int(parts[2])
                ports = range(start_port, min(end_port + 1, start_port + 100))
            except ValueError:
                ports = self.config["common_ports"]
        else:
            ports = self.config["common_ports"]
        
        await utils.answer(message, f"🔍 <b>Сканирую {host}...</b>")
        
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                continue
        
        results = ""
        if open_ports:
            results += "<b>Открытые порты:</b>\n"
            for port in open_ports:
                # Определяем сервис
                service = self._get_service_name(port)
                results += f"✅ {port} {service}\n"
        else:
            results += "❌ <b>Открытых портов не найдено</b>"
        
        await self._send_to_tech_chat(
            message,
            f"🔍 <b>Сканирование {host}:</b>\n\n{results}"
        )

    @loader.command()
    async def tconvertcmd(self, message: Message):
        """Конвертация файла: ответьте на файл и напишите .tconvert <формат>"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        if not reply or not reply.media:
            await utils.answer(message, "⚠️ <b>Ответьте на файл!</b>\n\nПример: ответьте на изображение и напишите <code>.tconvert png</code>")
            return
        
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите формат:</b> <code>.tconvert pdf/docx/png/jpg</code>")
            return
        
        target_format = args.strip().lower()
        
        await utils.answer(message, "🔄 <b>Конвертирую...</b>")
        
        try:
            # Скачиваем файл
            file_path = await reply.download_media()
            
            # Конвертация изображений
            if target_format in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']:
                from PIL import Image
                
                img = Image.open(file_path)
                if target_format == 'jpg':
                    target_format = 'jpeg'
                
                output_path = f"{os.path.splitext(file_path)[0]}.{target_format}"
                
                # Конвертируем с учетом прозрачности
                if target_format in ['jpg', 'jpeg']:
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    img.save(output_path, 'JPEG', quality=95)
                else:
                    img.save(output_path, target_format.upper())
                
                await self._send_to_tech_chat(
                    message,
                    f"✅ <b>Файл сконвертирован в {target_format.upper()}</b>",
                    output_path
                )
                
                # Удаляем временные файлы
                if os.path.exists(output_path):
                    os.remove(output_path)
            
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
                    
                    if os.path.exists(output_path):
                        os.remove(output_path)
                else:
                    await utils.answer(message, f"❌ <b>Конвертация в {target_format} пока не поддерживается</b>")
            else:
                await utils.answer(message, f"❌ <b>Неподдерживаемый формат: {target_format}</b>")
            
            # Удаляем исходный файл
            if os.path.exists(file_path):
                os.remove(file_path)
                
        except ImportError as e:
            await utils.answer(message, f"❌ <b>Установите библиотеку:</b> {e}")
        except Exception as e:
            await utils.answer(message, f"❌ <b>Ошибка конвертации:</b> {e}")

    @loader.command()
    async def tscreencmd(self, message: Message):
        """Скриншот сайта: .tscreen <url>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "⚠️ <b>Укажите URL!</b>\n\nПример: <code>.tscreen example.com</code>")
            return
        
        url = args.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        await utils.answer(message, "📸 <b>Делаю скриншот...</b>")
        
        try:
            # Пробуем разные методы скриншота
            screenshot_path = await self._take_screenshot(url)
            
            if screenshot_path:
                await self._send_to_tech_chat(
                    message,
                    f"📸 <b>Скриншот {url}</b>",
                    screenshot_path
                )
                
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
            else:
                await utils.answer(message, "❌ <b>Не удалось сделать скриншот</b>")
            
        except Exception as e:
            await utils.answer(message, f"❌ <b>Ошибка:</b> {e}")

    async def _take_screenshot(self, url):
        """Делает скриншот сайта"""
        # Пробуем selenium
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1280,720')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            driver.save_screenshot('screenshot.png')
            driver.quit()
            
            return 'screenshot.png'
        except:
            pass
        
        # Пробуем pyppeteer
        try:
            import asyncio
            from pyppeteer import launch
            
            async def take_screenshot():
                browser = await launch(headless=True)
                page = await browser.newPage()
                await page.setViewport({'width': 1280, 'height': 720})
                await page.goto(url)
                await page.screenshot({'path': 'screenshot.png'})
                await browser.close()
            
            asyncio.get_event_loop().run_until_complete(take_screenshot())
            return 'screenshot.png'
        except:
            pass
        
        return None

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

    def _get_service_name(self, port):
        """Возвращает название сервиса по порту"""
        services = {
            21: "(FTP)",
            22: "(SSH)",
            23: "(Telnet)",
            25: "(SMTP)",
            53: "(DNS)",
            80: "(HTTP)",
            110: "(POP3)",
            143: "(IMAP)",
            443: "(HTTPS)",
            465: "(SMTPS)",
            587: "(SMTP)",
            993: "(IMAPS)",
            995: "(POP3S)",
            3306: "(MySQL)",
            3389: "(RDP)",
            5432: "(PostgreSQL)",
            8080: "(HTTP-Alt)",
        }
        return services.get(port, "")

    @loader.command()
    async def techhelpcmd(self, message: Message):
        """Показать справку по техническим командам"""
        await utils.answer(message, self.strings("help"))
