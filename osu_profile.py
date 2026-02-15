from .. import loader, utils
import aiohttp
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class OsuProfileMod(loader.Module):
    """Модуль для osu! с красивыми эмодзи как в ExteraGram"""
    
    strings = {
        "name": "OsuProfile",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "no_query": "🚫 <b>Укажи запрос</b>\nПример: <code>.map The Big Black</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b>",
        "map_not_found": "❌ <b>Карта</b> <code>{}</code> <b>не найдена</b>",
        "loading": "🔄 <b>Загрузка...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        
        # Статистика игрока (как в ExteraGram)
        "user_stats": """<b>🎮 Osu! профиль: {username}</b> <a href='https://osu.ppy.sh/users/{user_id}'>🔗</a>

<b>📊 Статистика [{mode}]</b>
🔥 <b>PP:</b> <code>{pp}</code>
🏆 <b>Мировой ранг:</b> #{global_rank}
🌍 <b>Ранг в стране [{country}]:</b> #{country_rank}
🎯 <b>Точность:</b> {accuracy}%
🎮 <b>Сыграно карт:</b> {playcount}
⏰ <b>Время в игре:</b> {playtime} ч
👑 <b>Уровень:</b> {level}
🏅 <b>Ранги:</b> 💯{ss} ✨{s} 🅰️{a}""",

        # Информация о карте (как в ExteraGram)
        "map_info": """<b>🎵 {artist} - {title}</b> <a href='https://osu.ppy.sh/s/{mapset_id}'>🔗</a>

<b>📋 Информация о карте</b>
👤 <b>Маппер:</b> <a href='https://osu.ppy.sh/users/{creator_id}'>{creator}</a>
📊 <b>Статус:</b> {status}
📈 <b>Статистика:</b> 👁️{plays} ❤️{favourites}
🎥 <b>Видео:</b> {video}
⭐ <b>Сложностей:</b> {diff_count}

<b>🎯 Сложности:</b>
{diffs}""",
        
        # Помощь
        "help_text": """<b>🎮 OsuProfile Module</b>

<b>📋 Команды:</b>
.osu <ник> - статистика игрока
.osu <ник>:<режим> - статистика в режиме
.map <название> - поиск карты
.map <ID> - карта по ID
.osuhelp - это сообщение

<b>🎯 Режимы:</b> osu, taiko, catch, mania
<b>✨ Пример:</b> .osu peppy:mania""",
        
        # Статусы карт (как в ExteraGram)
        "status_graveyard": "🪦 Заброшенная",
        "status_wip": "🔧 В разработке",
        "status_pending": "⏳ В ожидании",
        "status_ranked": "✅ Рейтинговая",
        "status_approved": "👍 Одобренная",
        "status_qualified": "🎯 Квалифицированная",
        "status_loved": "❤️ Любимая",
        
        # Режимы игры
        "mode_osu": "🔴 osu!",
        "mode_taiko": "🥁 Taiko",
        "mode_catch": "🍏 Catch",
        "mode_mania": "🎹 Mania",
        
        "video_yes": "✅ Есть",
        "video_no": "❌ Нет",
    }
    
    # Константы (как в ExteraGram)
    API_KEY_V1 = "3e0c7c9baf734a70f780f2960332d825c50c4690"
    API_URL_V1 = "https://osu.ppy.sh/api/get_user"
    API_BEATMAP_V1 = "https://osu.ppy.sh/api/get_beatmaps"
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
    
    async def osucmd(self, message):
        """.osu <ник> [:<режим>] - Получить статистику игрока"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_nick"))
            return
        
        # Парсим режим если есть (как в ExteraGram)
        mode = 0
        nickname = args
        
        if ':' in args:
            parts = args.rsplit(':', 1)
            nickname = parts[0].strip()
            mode_str = parts[1].strip().lower()
            
            mode_map = {
                "osu": 0, "std": 0,
                "taiko": 1, "t": 1,
                "catch": 2, "c": 2, "ctb": 2,
                "mania": 3, "m": 3
            }
            mode = mode_map.get(mode_str, 0)
        
        await utils.answer(message, self.strings("loading"))
        
        try:
            stats = await self.get_user_stats(nickname, mode)
            
            if not stats:
                await utils.answer(message, self.strings("not_found").format(nickname))
                return
            
            # Форматируем числа
            stats['pp'] = f"{float(stats['pp']):,.0f}".replace(',', ' ')
            stats['global_rank'] = f"{int(stats['global_rank']):,}".replace(',', ' ')
            stats['country_rank'] = f"{int(stats['country_rank']):,}".replace(',', ' ')
            stats['accuracy'] = f"{float(stats['accuracy']):.2f}"
            stats['playcount'] = f"{int(stats['playcount']):,}".replace(',', ' ')
            
            # Название режима
            mode_names = ["🔴 osu!", "🥁 Taiko", "🍏 Catch", "🎹 Mania"]
            stats['mode'] = mode_names[mode]
            
            result = self.strings("user_stats").format(**stats)
            await utils.answer(message, result)
            
        except Exception as e:
            logger.exception(f"Ошибка: {e}")
            await utils.answer(message, self.strings("error").format(str(e)))
    
    async def mapcmd(self, message):
        """.map <название или ID> - Найти информацию о карте"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_query"))
            return
        
        query = args.strip()
        await utils.answer(message, self.strings("loading"))
        
        try:
            map_data = await self.get_map_info(query)
            
            if not map_data:
                await utils.answer(message, self.strings("map_not_found").format(query))
                return
            
            result = self.strings("map_info").format(**map_data)
            await utils.answer(message, result)
            
        except Exception as e:
            logger.exception(f"Ошибка: {e}")
            await utils.answer(message, self.strings("error").format(str(e)))
    
    async def osuhelpcmd(self, message):
        """Показать помощь по командам"""
        await utils.answer(message, self.strings("help_text"))
    
    async def get_user_stats(self, nickname: str, mode: int = 0) -> dict:
        """Получение статистики игрока через API"""
        params = {
            'k': self.API_KEY_V1,
            'u': nickname,
            'm': mode,
            'type': 'string'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL_V1, params=params) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                
                if not data or len(data) == 0:
                    return None
                
                user = data[0]
                
                # Конвертируем время
                playtime_seconds = int(user.get('total_seconds_played', 0))
                playtime_hours = round(playtime_seconds / 3600, 1)
                
                return {
                    'username': user.get('username', nickname),
                    'user_id': user.get('user_id', '?'),
                    'pp': user.get('pp_raw', '0'),
                    'global_rank': user.get('pp_rank', '0'),
                    'country_rank': user.get('pp_country_rank', '0'),
                    'accuracy': user.get('accuracy', '0'),
                    'playcount': user.get('playcount', '0'),
                    'playtime': playtime_hours,
                    'level': round(float(user.get('level', 0)), 2),
                    'ss': int(user.get('count_rank_ss', 0)) + int(user.get('count_rank_ssh', 0)),
                    's': int(user.get('count_rank_s', 0)) + int(user.get('count_rank_sh', 0)),
                    'a': user.get('count_rank_a', 0),
                    'country': user.get('country', '??')
                }
    
    async def get_map_info(self, query: str) -> dict:
        """Получение информации о карте"""
        if query.isdigit():
            params = {
                'k': self.API_KEY_V1,
                's': query
            }
        else:
            params = {
                'k': self.API_KEY_V1,
                'q': query
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_BEATMAP_V1, params=params) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                
                if not data or len(data) == 0:
                    return None
                
                # Группируем по beatmapset_id
                maps = {}
                for b in data:
                    set_id = b.get('beatmapset_id')
                    if set_id not in maps:
                        maps[set_id] = []
                    maps[set_id].append(b)
                
                # Берем первый сет
                first_set_id = list(maps.keys())[0]
                beatmaps = maps[first_set_id]
                first_map = beatmaps[0]
                
                # Статус карты
                status_map = {
                    '-2': 'status_graveyard',
                    '-1': 'status_wip',
                    '0': 'status_pending',
                    '1': 'status_ranked',
                    '2': 'status_approved',
                    '3': 'status_qualified',
                    '4': 'status_loved'
                }
                status_key = status_map.get(first_map.get('approved', '0'), 'status_pending')
                status = self.strings(status_key)
                
                # Видео
                video = self.strings('video_yes') if first_map.get('video') == '1' else self.strings('video_no')
                
                # Сложности
                diffs = []
                mode_emojis = ['🔴', '🥁', '🍏', '🎹']
                
                for b in sorted(beatmaps, key=lambda x: float(x.get('difficultyrating', 0))):
                    mode = int(b.get('mode', 0))
                    stars = float(b.get('difficultyrating', 0))
                    length = int(b.get('total_length', 0))
                    bpm = float(b.get('bpm', 0))
                    
                    minutes = length // 60
                    seconds = length % 60
                    
                    # Эмодзи для звезд (как в ExteraGram)
                    if stars < 2:
                        star_emoji = "⭐"
                    elif stars < 3:
                        star_emoji = "⭐⭐"
                    elif stars < 4:
                        star_emoji = "⭐⭐⭐"
                    elif stars < 5:
                        star_emoji = "⭐⭐⭐⭐"
                    elif stars < 6:
                        star_emoji = "🔥🔥"
                    else:
                        star_emoji = "💀💀"
                    
                    mode_emoji = mode_emojis[mode] if mode < 4 else '🎵'
                    diffs.append(f"{mode_emoji} {b.get('version', 'N/A')} {star_emoji} {stars:.2f} | {minutes}:{seconds:02d} | {bpm:.0f} BPM")
                
                # Общая статистика
                total_plays = sum(int(b.get('playcount', 0)) for b in beatmaps)
                
                return {
                    'artist': first_map.get('artist', 'N/A'),
                    'title': first_map.get('title', 'N/A'),
                    'mapset_id': first_set_id,
                    'creator': first_map.get('creator', 'N/A'),
                    'creator_id': first_map.get('creator_id', '0'),
                    'status': status,
                    'plays': f"{total_plays:,}".replace(',', ' '),
                    'favourites': f"{int(first_map.get('favourite_count', 0)):,}".replace(',', ' '),
                    'video': video,
                    'diff_count': len(beatmaps),
                    'diffs': '\n'.join(diffs[:10])
                }
