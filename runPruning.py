import subprocess
import os
import sys

def main():
    # 参数
    input_dir = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart_SG"
    output_dir = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart_SG_pruned"
    log_dir = r"D:\files\study2024\VL2D3_20241224\logs"

    # 创建输出和日志目录
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # 执行命令
    subprocess.run([
        sys.executable,
        "./agent/simplifySG.py",
        "--input_dir", input_dir,
        "--output_dir", output_dir,
        "--log_dir", log_dir,
        "--max_files", "30",
        "--suffix", ".pruned.json"
    ], check=True)

if __name__ == "__main__":
    main()