from typing import Dict, Optional, Set, Tuple

import discord


class LocalizedMessageValidator:
    __slots__: Tuple[str, str] = (
        "_languages",
        "_success_messages",
    )

    def __init__(self, languages: Set[str] = {"en"}) -> None:
        self._languages: Set[str] = languages
        self._success_messages: Dict[str, str] = {
            "ar": "تم الرفع!",
            "az": "Server qabağa çıxarıldı!",
            "cs": "Úspěšný bump!",
            "de": "Bump erfolgreich!",
            "en": "Bump done!",
            "fr": "Bump effectué !",
            "he": "באמפ בוצע!",
            "hi": "बम्प हो गया!",
            "id": "Bump berhasil! 👍",
            "ja": "表示順をアップしたよ :thumbsup:",
            "ko": "서버 갱신 완료!",
            "pl": "Podbito serwer!",
            "pt": "Bump feito!",
            "ro": "Bump gata!",
            "tr": "Öne çıkarma başarılı!",
            "vi": "Đã bump!",
            "zh-CN": "服务器已顶！",
        }

    def validate_success(self, message: discord.Message) -> Optional[discord.Embed]:
        if not message.embeds:
            return None
        embed: discord.Embed = message.embeds[0]
        if ":thumbsup:" in embed.description:  # type: ignore
            return embed
        for language in self._languages:
            if message.webhook_id and self._success_messages[language] in embed.description:  # type: ignore
                return embed
        return None
