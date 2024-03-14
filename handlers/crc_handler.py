from crcmod import mkCrcFun
from binascii import unhexlify


def calculate_crc(data, crc_type='crc8'):
    crc_func_map = {
        'crc8-rohc': (0x107, True, 0xFF, 0x00),
        'crc16-modbus': (0x18005, True, 0xFFFF, 0x0000),
        'crc32': (0x104C11DB7, True, 0xFFFFFFFF, 0xFFFFFFFF)
    }

    if crc_type not in crc_func_map:
        raise ValueError("calculate_crc: Unsupported CRC type.")

    poly, rev, initCrc, xorOut = crc_func_map[crc_type]
    crc_func = mkCrcFun(poly, rev=rev, initCrc=initCrc, xorOut=xorOut)

    crc_value = crc_func(unhexlify(data))

    if 'crc8' in crc_type:
        crc_hex = format(crc_value, '02X')
    elif 'crc16' in crc_type:
        crc_hex = format(crc_value, '04X')
    else:
        crc_hex = format(crc_value, '08X')

    return crc_hex


if __name__ == '__main__':
    # 测试
    data = '0102030405'
    crc_type = 'crc16-modbus'
    crc = calculate_crc(data, crc_type)
    print(f"CRC-{crc_type.upper()} 校验值（十六进制）：", crc)
