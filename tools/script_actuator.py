import sys
import subprocess

def execute_script(args, log_path):
    """
    执行指定路径的 Python 脚本。
    :param args: 前端参数
    :param log_path: 日志路径
    """
    script_path = args.Path
    try:
        # 获取当前虚拟环境的 Python 解释器路径
        python_executable = sys.executable

        # 构造命令，剔除与 Gooey 相关的参数
        command = [python_executable, script_path]

        # 使用 subprocess.Popen 进行实时输出
        with subprocess.Popen(
                command,
                stdout=sys.stdout,  # 将子进程的标准输出重定向到主进程
                stderr=sys.stderr,  # 将子进程的标准错误重定向到主进程
                text=True  # 以文本模式处理输出
        ) as process:
            process.wait()  # 等待脚本执行完成

    except Exception as e:
        print(f"执行脚本时发生错误：{e}")
