import binascii
import hashlib
import hmac

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class AESCipher:
    def __init__(self, key, mode=AES.MODE_CBC, iv=None):
        """  
        初始化AES加密器  
        :param key: 密钥，可以是16, 24, 或 32字节长，对应AES-128, AES-192, AES-256  
        :param mode: 加密模式，如AES.MODE_CBC, AES.MODE_CFB等  
        :param iv: 初始化向量，对于某些模式（如CBC）是必需的，对于ECB模式则忽略  
        """
        if len(key) not in [16, 24, 32]:
            raise ValueError("AESCipher: Key must be 16, 24, or 32 bytes long")
        self.key = key
        self.mode = mode
        self.iv = iv if iv is not None else get_random_bytes(AES.block_size)  # 如果未提供IV，则生成一个随机IV
        if self.mode == AES.MODE_CBC:
            self.cipher = AES.new(self.key, self.mode, self.iv)
        else:
            self.cipher = AES.new(self.key, self.mode)

    def encrypt(self, plaintext):
        """  
        加密明文  
        :param plaintext: 要加密的明文  
        :return: 加密后的密文（十六进制表示）  
        """
        padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = self.cipher.encrypt(padded_plaintext)
        return ciphertext.hex()

    def decrypt(self, ciphertext_hex):
        """  
        解密密文  
        :param ciphertext_hex: 要解密的密文（十六进制表示）  
        :return: 解密后的明文  
        """
        ciphertext = bytes.fromhex(ciphertext_hex)
        decrypted_text = self.cipher.decrypt(ciphertext)
        unpadded_text = unpad(decrypted_text, AES.block_size)
        return unpadded_text.decode('utf-8')


# 总加和取低8位
def hex_checksum(data):
    # 将16进制字符串转换为整数
    nums = [int(data[i:i + 2], 16) for i in range(0, len(data), 2)]
    # 计算总和
    total_sum = sum(nums)
    # 取低8位
    checksum = total_sum & 0xFF
    return format(checksum, '02X')


def hmac_encode(algo, key, input_data):
    """
        HMAC（Hash-based Message Authentication Code）是一种基于哈希函数的消息认证码
        :param algo: 哈希函数（如MD5、SHA-1、SHA-256等）
        :param key: 秘钥key
        :param input_data: 消息
        :return: 返回加密后的十六进制字符串
     """
    if algo == "md5":
        hash_func = hashlib.md5
    elif algo == "sha1":
        hash_func = hashlib.sha1
    elif algo == "sha256":
        hash_func = hashlib.sha256
    elif algo == "sha512":
        hash_func = hashlib.sha512
    else:
        raise ValueError("Unsupported algorithm")

    hmac_result = hmac.new(key.encode(), input_data.encode(), hash_func)
    # Convert HMAC-MD5 result to hex string
    result = binascii.hexlify(hmac_result.digest()).decode()
    return result


if __name__ == '__main__':
    key = b"your_key_here123"  # 密钥必须是16、24或32字节长
    iv = b'0123456789123456'
    aes = AESCipher(key, mode=AES.MODE_ECB, iv=iv)
    # 加密数据
    plaintext = "Hello, AES!"
    encrypted_text = aes.encrypt(plaintext)
    print("加密后的密文:", encrypted_text)
    # # 重新初始化AES实例
    # aes = AESCipher(key, mode=AES.MODE_ECB, iv=iv)
    # 解密数据
    decrypted_text = aes.decrypt(encrypted_text)
    print("解密后的明文:", decrypted_text)

    # # hmac_encode示例
    # # Constants
    # HMACMD5_KEY = "@9jHaGa]"
    # random = "FZNrADXQTSVIZgua"
    # groupId = "1045263038358777856"
    # # Concatenate key and random
    # key_random = HMACMD5_KEY + random
    # # Calculate HMAC-MD5
    # password = hmac_encode("md5", key_random, groupId)
    # print("Password:", password)
