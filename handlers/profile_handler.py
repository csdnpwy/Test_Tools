# -*- coding: utf-8 -*-
import os
import shutil

from handlers.log_handler import get_log


def replace_and_save(input_file, output_dir, replacements, log_path):
    try:
        os.chmod(input_file, 0o777)
        with open(input_file, 'r', encoding='utf-8') as infile:
            content = infile.read()

        for old_text, new_text in replacements.items():
            content = content.replace(old_text, new_text)

        output_file = f"{output_dir}/配置及页面元素.txt"
        if os.path.isfile(output_file):
            # 文件存在，备份删除文件
            backup_filename = output_file + '.bak'
            shutil.copy(output_file, backup_filename)
            get_log(log_path).info(f"备份原配置文件: {backup_filename}")
            os.remove(output_file)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(content)
            get_log(log_path).info(f"生成配置文件: {output_file}")
    except FileNotFoundError:
        get_log(log_path).error(f"File '{input_file}' not found.")
    except Exception as e:
        get_log(log_path).error(f"An error occurred: {e}")
