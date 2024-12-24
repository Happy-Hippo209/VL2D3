import subprocess
import os
import sys

def main():
    # 参数
    prompt_dir = r"D:\files\study2024\VL2D3_20241224\datasets\VLprompt"
    response_dir = r"D:\files\study2024\VL2D3_20241224\datasets\VLresponse"
    log_dir = r"D:\files\study2024\VL2D3_20241224\logs"

    # 创建输出和日志目录
    os.makedirs(response_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # 执行命令
    subprocess.run([
        sys.executable,
        "./agent/2D3agent.py",
        prompt_dir,
        response_dir,
        log_dir
    ], check=True)

if __name__ == "__main__":
    main()