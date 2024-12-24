import subprocess

# 参数
input_path = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart"
output_path = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart_html"
log_dir = "./logs"

# 执行命令
subprocess.run([
    "python", 
    "./preprocess/embedVegaliteHtml.py", 
    input_path, 
    output_path, 
    "--log-dir", log_dir
], check=True)

# 参数
input_dir = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart_html"
sg_output_dir = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart_SG"
svg_output_dir = r"D:\files\study2024\VL2D3_20241224\datasets\VLchart_SVG"
log_dir = r"./logs"
driver_path = r"D:\files\study2024\chromedriver-win64\chromedriver.exe"

# 执行命令
subprocess.run([
    "python", 
    "./preprocess/getSGandSVG.py",  
    "--input_dir", input_dir,
    "--sg_output_dir", sg_output_dir,
    "--svg_output_dir", svg_output_dir,
    "--log_dir", log_dir,
    "--driver_path", driver_path
], check=True)