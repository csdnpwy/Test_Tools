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


def custom_pad(in_data, block_size):
    """
    数据填充-适配网关局域网通信中AES加密数据填充
    :param in_data: 源数据
    :param block_size: 块大小
    :return:
    """
    padding = block_size - (len(in_data) % block_size)
    return in_data + b'\x00' * padding


def ch_to_hex(value):
    """
    单个字符转为十六进制
    :param value: 单字符
    :return: 转换后十六进制
    """
    if '0' <= value <= '9':
        return ord(value) - ord('0')
    elif 'A' <= value <= 'Z':
        return ord(value) - ord('A') + 10
    elif 'a' <= value <= 'z':
        return ord(value) - ord('a') + 10
    else:
        return -1


def str_to_hex(buf):
    """
    将字符串转为十六进制数组
    :param buf: 字符串
    :return: 转换字节串
    """
    hex_array = bytearray()
    for i in range(0, len(buf), 2):
        if i + 1 < len(buf):
            high_nibble = ch_to_hex(buf[i])
            low_nibble = ch_to_hex(buf[i + 1])
            if high_nibble != -1 and low_nibble != -1:
                hex_byte = (high_nibble << 4) | low_nibble
                hex_array.append(hex_byte)
            else:
                return None
        else:
            return None
    return hex_array


def aes_encrypt(data, password):
    """
    网关局域网通信AES加密
    :param data: 待加密数据
    :param password: 初始密码
    :return: 加密后数据
    """
    # print(f"预加密Payload：{data}")
    AES_BLOCK_SIZE = 16
    AES_IV = 'nwALi4=fjXM4nk#N'.encode()
    # 创建 AES 加密器
    aes_key = str_to_hex(password)
    cipher = AES.new(aes_key, AES.MODE_CBC, AES_IV)
    # 自定义填充
    padded_data = custom_pad(data.encode(), AES_BLOCK_SIZE)
    # 加密数据
    enc_payload = cipher.encrypt(padded_data)
    # print(f"加密Payload长度：{len(enc_payload)}")
    return enc_payload.hex()


def aes_decrypt(encrypted_data, password):
    """
    网关局域网通信AES解密
    :param encrypted_data: 待解密数据的十六进制表示
    :param password: 初始密码
    :return: 解密后的数据
    """
    AES_IV = 'nwALi4=fjXM4nk#N'.encode()
    aes_key = str_to_hex(password)
    cipher = AES.new(aes_key, AES.MODE_CBC, AES_IV)
    encrypted_data = bytes.fromhex(encrypted_data)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data.rstrip(b'\x00').decode('utf-8')

