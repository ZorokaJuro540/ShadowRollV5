"""
Text styling system for Shadow Roll Bot
Anime-inspired font effects and text formatting
"""

class AnimeTextStyles:
    """Collection of anime-inspired text styling functions"""
    
    @staticmethod
    def vaporwave(text: str) -> str:
        """Convert text to vaporwave style (full-width characters)"""
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        vaporwave = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９"
        
        result = ""
        for char in text:
            if char in normal:
                result += vaporwave[normal.index(char)]
            else:
                result += char
        return result
    
    @staticmethod
    def small_caps(text: str) -> str:
        """Convert text to small caps style"""
        normal = "abcdefghijklmnopqrstuvwxyz"
        small_caps = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
        
        result = ""
        for char in text.lower():
            if char in normal:
                result += small_caps[normal.index(char)]
            else:
                result += char
        return result
    
    @staticmethod
    def bold_italic(text: str) -> str:
        """Convert text to bold italic Unicode style"""
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        bold_italic = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"
        
        result = ""
        for char in text:
            if char in normal:
                result += bold_italic[normal.index(char)]
            else:
                result += char
        return result
    
    @staticmethod
    def serif_bold(text: str) -> str:
        """Convert text to serif bold style"""
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        serif_bold = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
        
        result = ""
        for char in text:
            if char in normal:
                result += serif_bold[normal.index(char)]
            else:
                result += char
        return result
    
    @staticmethod
    def double_struck(text: str) -> str:
        """Convert text to double-struck style"""
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        double_struck = "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕠𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"
        
        result = ""
        for char in text:
            if char in normal:
                result += double_struck[normal.index(char)]
            else:
                result += char
        return result
    
    @staticmethod
    def sans_serif_bold(text: str) -> str:
        """Convert text to sans-serif bold style"""
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        sans_bold = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
        
        result = ""
        for char in text:
            if char in normal:
                result += sans_bold[normal.index(char)]
            else:
                result += char
        return result
    
    @staticmethod
    def monospace(text: str) -> str:
        """Convert text to monospace style"""
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        monospace = "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
        
        result = ""
        for char in text:
            if char in normal:
                result += monospace[normal.index(char)]
            else:
                result += char
        return result

class ShadowRollTextFormatter:
    """Shadow Roll specific text formatting with anime aesthetics"""
    
    @staticmethod
    def format_title(text: str, style: str = "vaporwave") -> str:
        """Format titles with anime-inspired styling"""
        if style == "vaporwave":
            return AnimeTextStyles.vaporwave(text)
        elif style == "bold":
            return AnimeTextStyles.serif_bold(text)
        elif style == "small_caps":
            return AnimeTextStyles.small_caps(text)
        elif style == "double_struck":
            return AnimeTextStyles.double_struck(text)
        elif style == "sans_bold":
            return AnimeTextStyles.sans_serif_bold(text)
        elif style == "monospace":
            return AnimeTextStyles.monospace(text)
        else:
            return text
    
    @staticmethod
    def format_main_title() -> str:
        """Format the main Shadow Roll title with special styling"""
        # Using vaporwave for the main title
        shadow = AnimeTextStyles.vaporwave("SHADOW")
        roll = AnimeTextStyles.vaporwave("ROLL")
        return f"🌌 ═══════〔 {shadow}   {roll} 〕═══════ 🌌"
    
    @staticmethod
    def format_section_title(title: str, emoji: str = "🌑") -> str:
        """Format section titles with consistent styling"""
        styled_title = AnimeTextStyles.sans_serif_bold(title.upper())
        return f"{emoji} ═══〔 {styled_title} 〕═══ {emoji}"
    
    @staticmethod
    def format_character_name(name: str) -> str:
        """Format character names with special styling"""
        return AnimeTextStyles.serif_bold(name)
    
    @staticmethod
    def format_rarity_text(rarity: str) -> str:
        """Format rarity text with emphasis"""
        return AnimeTextStyles.sans_serif_bold(rarity.upper())
    
    @staticmethod
    def format_anime_title(anime: str) -> str:
        """Format anime titles with italic styling"""
        return AnimeTextStyles.bold_italic(anime)
    
    @staticmethod
    def format_username(username: str) -> str:
        """Format usernames with small caps"""
        return AnimeTextStyles.small_caps(username)

# Convenience functions for quick access
def style_title(text: str, style: str = "vaporwave") -> str:
    """Quick access to title styling"""
    return ShadowRollTextFormatter.format_title(text, style)

def style_main_title() -> str:
    """Quick access to main title formatting"""
    return ShadowRollTextFormatter.format_main_title()

def style_section(title: str, emoji: str = "🌑") -> str:
    """Quick access to section title formatting"""
    return ShadowRollTextFormatter.format_section_title(title, emoji)

def style_character(name: str) -> str:
    """Quick access to character name formatting"""
    return ShadowRollTextFormatter.format_character_name(name)

def style_rarity(rarity: str) -> str:
    """Quick access to rarity text formatting with color codes"""
    # Map rarity to ANSI color codes
    rarity_colors = {
        'Common': '\u001b[0;37m',      # Gris/White
        'Rare': '\u001b[1;34m',        # Bleu/Blue
        'Epic': '\u001b[1;35m',        # Violet/Magenta
        'Legendary': '\u001b[1;33m',   # Jaune/Yellow
        'Mythic': '\u001b[1;31m',      # Rouge/Red
        'Titan': '\u001b[1;37m',       # Blanc/Bright White
        'Fusion': '\u001b[1;95m',      # Rose/Bright Magenta
        'Secret': '\u001b[1;30m',      # Noir/Black
        'Evolve': '\u001b[1;32m'       # Vert/Green
    }
    
    color_code = rarity_colors.get(rarity, '\u001b[0;37m')  # Default to white
    reset_code = '\u001b[0m'
    
    # Format with color and styling
    styled_rarity = ShadowRollTextFormatter.format_rarity_text(rarity)
    return f"{color_code}{styled_rarity}{reset_code}"

def style_anime(anime: str) -> str:
    """Quick access to anime title formatting"""
    return ShadowRollTextFormatter.format_anime_title(anime)

def style_username(username: str) -> str:
    """Quick access to username formatting"""
    return ShadowRollTextFormatter.format_username(username)