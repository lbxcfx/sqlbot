import base64
import re

try:
    from sqlbot_xpack.core import sqlbot_decrypt as xpack_sqlbot_decrypt, sqlbot_encrypt as xpack_sqlbot_encrypt
    XPACK_AVAILABLE = True
except (ImportError, AttributeError):
    XPACK_AVAILABLE = False

def _is_base64_encoded(text: str) -> bool:
    """
    判断字符串是否为 base64 编码
    """
    if not text:
        return False
    # Base64 字符串只包含 A-Z, a-z, 0-9, +, /, =
    # 长度必须是 4 的倍数（考虑 padding）
    base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
    if not base64_pattern.match(text):
        return False
    if len(text) % 4 != 0:
        return False
    try:
        # 尝试 base64 解码
        base64.b64decode(text, validate=True)
        return True
    except Exception:
        return False

async def sqlbot_decrypt(text: str) -> str:
    """
    解密文本。开源版本：如果 XPack 不可用或解密失败，直接返回原文
    """
    if not text:
        return text

    # 如果不是 base64 编码，直接返回（明文）
    if not _is_base64_encoded(text):
        return text

    if not XPACK_AVAILABLE:
        return text

    try:
        return await xpack_sqlbot_decrypt(text)
    except Exception:
        # 如果解密失败，直接返回原文
        return text

async def sqlbot_encrypt(text: str) -> str:
    """
    加密文本。开源版本：如果 XPack 不可用，直接返回原文
    """
    if not XPACK_AVAILABLE:
        return text
    try:
        return await xpack_sqlbot_encrypt(text)
    except Exception:
        return text