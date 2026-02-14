from .. import loader, utils
import aiohttp

@loader.tds
class OsuProfileMod(loader.Module):
    """Модуль для проверки профилей Osu!"""
    
    strings = {
        "name": "OsuProfile",
        "no_nick": "🚫 Укажи никнейм игрока\nПример: .osu peppy",
        "not_found": "❌ Игрок {} не найден",
        "profile": """<b>🎮 Osu! Профиль: {}</b>

🔗 <a href='{}'>Открыть профиль на сайте</a>"""
    }
    
    strings_ru = {
        "name": "OsuProfile",
        "no_nick": "🚫 Укажи никнейм игрока\nПример: .osu peppy",
        "not_found": "❌ Игрок {} не найден",
        "profile": """<b>🎮 Профиль Osu!: {}</b>

🔗 <a href='{}'>Открыть профиль на сайте</a>"""
    }
    
    async def osucmd(self, message):
        """.osu <ник> - Проверить профиль Osu!"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_nick"))
            return
        
        nickname = args.strip()
        profile_url = f"https://osu.ppy.sh/users/{nickname}"
        
        # Проверяем существует ли профиль
        async with aiohttp.ClientSession() as session:
            async with session.get(profile_url, allow_redirects=True) as resp:
                if resp.status == 200 and "search" not in str(resp.url):
                    await utils.answer(
                        message, 
                        self.strings("profile").format(nickname, profile_url)
                    )
                else:
                    await utils.answer(
                        message, 
                        self.strings("not_found").format(nickname)
                    )
    
    async def osucheckcmd(self, message):
        """.osucheck <ник> - Быстрая ссылка на профиль"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_nick"))
            return
        
        nickname = args.strip()
        profile_url = f"https://osu.ppy.sh/users/{nickname}"
        
        await utils.answer(
            message,
            f"🔗 <a href='{profile_url}'>Профиль {nickname}</a>"
        )
