import subprocess
import os
import sys

def main():
    # 参数
    vl_path = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart"
    sg_path = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart_SG"  
    output_path = r"D:\files\study2024\VL2D3_20241224\datasets\VLprompt"
    log_dir = r"D:\files\study2024\VL2D3_20241224\logs"

    # 检查路径是否存在
    paths = [vl_path, sg_path]
    for path in paths:
        if not os.path.exists(path):
            print(f"Error: Path does not exist: {path}")
            sys.exit(1)

    # 创建输出和日志目录
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # 构建完整的脚本路径
    script_path = os.path.join(os.path.dirname(__file__), "agent", "prompt.py")
    
    try:
        # 执行命令
        subprocess.run([
            sys.executable,  # 使用当前Python解释器
            script_path,
            vl_path,
            sg_path, 
            output_path,
            "--log-dir",
            log_dir
        ], check=True)
        print("Processing completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()