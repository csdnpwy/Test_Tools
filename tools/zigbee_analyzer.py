import os
import re
import shutil

from handlers.log_handler import get_log


def zigbee_payload_analyzer(args, log_path):
    """
    zigbee报文分析器
    :param args: 前端参数
    :param log_path: 日志存储路径
    """
    file_path = args.文件
    filter = args.过滤正则
    output_dir = args.Path
    output_file = f"{output_dir}/zigbee_mes.txt"
    with open(file_path) as file:
        text = file.read()
    matches = re.findall(filter, text)

    if os.path.isfile(output_file):
        # 文件存在，备份删除文件
        backup_filename = output_file + '.bak'
        shutil.copy(output_file, backup_filename)
        get_log(log_path).info(f"备份原过滤报文文件: {backup_filename}")
        os.remove(output_file)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for match in matches:
            outfile.write(f"{match}\n")
        get_log(log_path).info(f"过滤报文存储路径: {output_file}")
