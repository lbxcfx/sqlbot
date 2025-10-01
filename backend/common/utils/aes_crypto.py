from typing import Optional
from common.core.config import settings
import base64
import hashlib

# 开源版本：优雅降级处理企业版 AES 加密
try:
    from sqlbot_xpack.aes_utils import SecureEncryption
    XPACK_AVAILABLE = True
except ImportError:
    XPACK_AVAILABLE = False
    # 使用 pycryptodome 实现开源版 AES 加密
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad

    class SecureEncryption:
        @staticmethod
        def encrypt_to_single_string(text: str, key: str) -> str:
            """AES-256-CBC 加密"""
            try:
                # 使用 key 的 SHA256 作为加密密钥（32 字节）
                cipher_key = hashlib.sha256(key.encode()).digest()
                # 使用 key 的 MD5 作为 IV（16 字节）
                iv = hashlib.md5(key.encode()).digest()

                cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
                padded_data = pad(text.encode('utf-8'), AES.block_size)
                encrypted = cipher.encrypt(padded_data)

                # Base64 编码返回
                return base64.b64encode(encrypted).decode('utf-8')
            except Exception:
                # 加密失败返回原文
                return text

        @staticmethod
        def decrypt_from_single_string(text: str, key: str) -> str:
            """AES-256-CBC 解密"""
            try:
                # 使用 key 的 SHA256 作为解密密钥（32 字节）
                cipher_key = hashlib.sha256(key.encode()).digest()
                # 使用 key 的 MD5 作为 IV（16 字节）
                iv = hashlib.md5(key.encode()).digest()

                encrypted = base64.b64decode(text)
                cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
                decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)

                return decrypted.decode('utf-8')
            except Exception:
                # 解密失败返回原文
                return text

        @staticmethod
        def simple_aes_encrypt(text: str, key: str, ivtext: str) -> str:
            """简单 AES 加密（兼容方法）"""
            try:
                # 确保 key 是 32 字节
                cipher_key = (key + '0' * 32)[:32].encode('utf-8')
                # 确保 IV 是 16 字节
                iv = (ivtext + '0' * 16)[:16].encode('utf-8')

                cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
                padded_data = pad(text.encode('utf-8'), AES.block_size)
                encrypted = cipher.encrypt(padded_data)

                return base64.b64encode(encrypted).decode('utf-8')
            except Exception:
                return text

        @staticmethod
        def simple_aes_decrypt(text: str, key: str, ivtext: str) -> str:
            """简单 AES 解密（兼容方法）"""
            try:
                # 确保 key 是 32 字节
                cipher_key = (key + '0' * 32)[:32].encode('utf-8')
                # 确保 IV 是 16 字节
                iv = (ivtext + '0' * 16)[:16].encode('utf-8')

                encrypted = base64.b64decode(text)
                cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
                decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)

                return decrypted.decode('utf-8')
            except Exception:
                return text

simple_aes_iv_text = 'sqlbot_em_aes_iv'

def sqlbot_aes_encrypt(text: str, key: Optional[str] = None) -> str:
    return SecureEncryption.encrypt_to_single_string(text, key or settings.SECRET_KEY)

def sqlbot_aes_decrypt(text: str, key: Optional[str] = None) -> str:
    return SecureEncryption.decrypt_from_single_string(text, key or settings.SECRET_KEY)

def simple_aes_encrypt(text: str, key: Optional[str] = None, ivtext: Optional[str] = None) -> str:
    return SecureEncryption.simple_aes_encrypt(text, key or settings.SECRET_KEY[:32], ivtext or simple_aes_iv_text)

def simple_aes_decrypt(text: str, key: Optional[str] = None, ivtext: Optional[str] = None) -> str:
    return SecureEncryption.simple_aes_decrypt(text, key or settings.SECRET_KEY[:32], ivtext or simple_aes_iv_text)