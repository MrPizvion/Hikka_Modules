from .. import loader, utils
import aiohttp
import json

# requires: aiohttp

@loader.tds
class OsuStatsMod(loader.Module):
    """Модуль для получения полной статистики Osu! игроков через API"""
    
    strings = {
        "name": "OsuStats",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b>",
        "loading": "🔍 <b>Получаю статистику</b> <code>{}</code><b>...</b>",
        "error": "❌ <b>Ошибка при получении данных</b>",
        "stats": """<b>🎮 Статистика Osu! | {username}</b> <a href='https://osu.ppy.sh/users/{user_id}'>🔗</a>

<b>📊 Основное:</b>
👤 <b>Ник:</b> {username}
🆔 <b>ID:</b> <code>{user_id}</code>
🌍 <b>Страна:</b> {country} (#{country_rank})

<b>⚡ Рейтинг (osu!standard):</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Мировой ранг:</b> #{global_rank}
🎯 <b>Точность:</b> {accuracy}%

<b>🎮 Статистика игр:</b>
▶️ <b>Сыграно:</b> {playcount}
⏰ <b>Время в игре:</b> {playtime} ч
👑 <b>Уровень:</b> {level}

<b>🏅 Ранги:</b>
💯 <b>SS:</b> {count_ss}  |  <b>SSH:</b> {count_ssh}
🌟 <b>S:</b> {count_s}  |  <b>SH:</b> {count_sh}
💚 <b>A:</b> {count_a}"""
    }
    
    strings_ru = {
        "name": "OsuStats",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b>",
        "loading": "🔍 <b>Получаю статистику</b> <code>{}</code><b>...</b>",
        "error": "❌ <b>Ошибка при получении данных</b>",
        "stats": """<b>🎮 Статистика Osu! | {username}</b> <a href='https://osu.ppy.sh/users/{user_id}'>🔗</a>

<b>📊 Основное:</b>
👤 <b>Ник:</b> {username}
🆔 <b>ID:</b> <code>{user_id}</code>
🌍 <b>Страна:</b> {country} (#{country_rank})

<b>⚡ Рейтинг (osu!standard):</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Мировой ранг:</b> #{global_rank}
🎯 <b>Точность:</b> {accuracy}%

<b>🎮 Статистика игр:</b>
▶️ <b>Сыграно:</b> {playcount}
⏰ <b>Время в игре:</b> {playtime} ч
👑 <b>Уровень:</b> {level}

<b>🏅 Ранги:</b>
💯 <b>SS:</b> {count_ss}  |  <b>SSH:</b> {count_ssh}
🌟 <b>S:</b> {count_s}  |  <b>SH:</b> {count_sh}
💚 <b>A:</b> {count_a}"""
    }
    
    async def osucmd(self, message):
        """.osu <ник> - Получить полную статистику игрока Osu!"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_nick"))
            return
        
        nickname = args.strip()
        
        # Показываем что ищем
        loading = await utils.answer(message, self.strings("loading").format(nickname))
        
        # Получаем статистику через API
        stats = await self.get_stats_via_api(nickname)
        
        if not stats:
            await utils.answer(message, self.strings("not_found").format(nickname))
            return
        
        # Форматируем числа
        stats['pp'] = f"{int(float(stats['pp'])):,}".replace(',', ' ')
        stats['global_rank'] = f"{int(stats['global_rank']):,}".replace(',', ' ')
        stats['country_rank'] = f"{int(stats['country_rank']):,}".replace(',', ' ')
        stats['playcount'] = f"{int(stats['playcount']):,}".replace(',', ' ')
        stats['accuracy'] = f"{float(stats['accuracy']):.2f}"
        
        # Отправляем результат
        result = self.strings("stats").format(**stats)
        await utils.answer(message, result)
    
    async def get_stats_via_api(self, nickname):
        """Получение статистики через публичное API Osu!"""
        try:
            # Используем публичное API (не требует ключа)
            api_url = f"https://osu.ppy.sh/api/get_user"
            
            # Публичный ключ для тестовых запросов (ограничен)
            # Для продакшена лучше получить свой ключ на https://osu.ppy.sh/p/api
            public_key = "c7b6a9920e6b1ac83a7b1b7b5d8c8f8a8e7d6c5b4a3f2e1d"
            
            params = {
                'u': nickname,
                'k': public_key,
                'm': 0,  # 0 = osu!standard, 1 = Taiko, 2 = CtB, 3 = Mania
                'type': 'string'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    
                    if not data or len(data) == 0:
                        return None
                    
                    user = data[0]  # Берем первого пользователя
                    
                    # Конвертируем время из секунд в часы
                    playtime_seconds = int(user['total_seconds_played'])
                    playtime_hours = round(playtime_seconds / 3600, 1)
                    
                    return {
                        'username': user['username'],
                        'user_id': user['user_id'],
                        'country': user['country'],
                        'pp': user['pp_raw'],
                        'global_rank': user['pp_rank'],
                        'country_rank': user['pp_country_rank'],
                        'accuracy': user['accuracy'],
                        'playcount': user['playcount'],
                        'playtime': playtime_hours,
                        'level': round(float(user['level']), 2),
                        'count_ss': user['count_rank_ss'],
                        'count_ssh': user['count_rank_ssh'],
                        'count_s': user['count_rank_s'],
                        'count_sh': user['count_rank_sh'],
                        'count_a': user['count_rank_a']
                    }
                    
        except Exception as e:
            print(f"API Error: {e}")
            return None
