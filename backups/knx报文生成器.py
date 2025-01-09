from handlers.crc_handler import calculate_crc
import itertools

def parse_rule(rule):
    """解析输入规则，生成可能的值列表"""
    parts = rule.split()  # 按空格分隔规则
    combinations = []

    for part in parts:
        if part.startswith("[") and part.endswith("]"):
            content = part[1:-1]
            if "-" in content:  # 范围 [00-FF]
                start, end = content.split("-")
                try:
                    combinations.append([f"{i:02X}" for i in range(int(start, 16), int(end, 16) + 1)])
                except ValueError:
                    raise ValueError(f"无效的范围定义：{part}")
            elif ":" in content:  # 多选项 [01:02:03]
                combinations.append(content.split(":"))
            else:
                raise ValueError(f"无效的范围或选项定义：{part}")
        else:  # 固定字符
            combinations.append([part])

    return combinations

def generate_combinations(rule):
    """根据规则生成所有可能的组合"""
    combinations = parse_rule(rule)
    return itertools.product(*combinations)  # 笛卡尔积生成所有组合

def show_rule_help():
    """显示规则的输入格式说明"""
    print("-" * 65)
    print("功能：")
    print("自定义16进制字符串规则，输出所有组合序列并计算其CRC值；\n")
    print("规则输入说明：")
    print("1. 固定字符：直接输入，例如 '56'")
    print("2. 范围值：用 [00-FF] 表示，例如 '[00-FF]' 生成从 00 到 FF 的所有值")
    print("3. 多选值：用 [01:02:03] 表示，例如 '[01:02:03]' 生成 01、02 和 03")
    print("4. 使用空格分隔不同部分，例如 '56 [00-FF] [01:02:03] 01'")
    print("5. 支持CRC8、CRC16、CRC32数据校验")
    print("6. 输入 'exit' 退出程序")
    print("-" * 65)

def get_crc_type():
    """获取用户选择的 CRC 类型"""
    print("请选择 CRC 计算方式（回车选择默认值）：")
    print("1. CRC8")
    print("2. CRC16（默认）")
    print("3. CRC32")
    while True:
        choice = input("请输入选项（1、2 或 3）：").strip()
        if not choice:  # 回车默认选 CRC16
            return "crc16-modbus"
        elif choice == "1":
            return "crc8-rohc"
        elif choice == "2":
            return "crc16-modbus"
        elif choice == "3":
            return "crc32"
        else:
            print("无效选项，请输入 1、2 或 3，或直接回车。")


if __name__ == '__main__':
    show_rule_help()

    while True:
        mes_rule = input("\n请输入报文规则（输入 'exit' 退出）：").strip()
        if not mes_rule:  # 处理空输入
            print("输入为空，请重新输入！")
            continue

        if mes_rule.lower() == 'exit':  # 检查用户是否输入 exit 以退出
            print("程序结束！")
            break

        try:
            crc_type = get_crc_type()  # 获取用户选择的 CRC 类型
            print(f"\n*********报文组合如下*********")
            all_combinations = generate_combinations(mes_rule)

            # 打印所有组合及其 CRC 值
            for combination in all_combinations:
                combination_str = "".join(combination)  # 合并为无空格的字符串
                crc_value = calculate_crc(combination_str, crc_type=crc_type)  # 根据选择计算 CRC
                res = combination_str + crc_value
                print(" ".join([res[j:j + 2] for j in range(0, len(res), 2)]))

        except ValueError as e:
            print(f"输入规则错误：{e}")
        except Exception as e:
            print(f"发生错误：{e}")
