from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import os
import time
import json
import re
import argparse
from tqdm import tqdm
import logging

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process HTML files to extract scene graphs and save as SVG')
    parser.add_argument('--input_dir', required=True, help='Input directory containing HTML files')
    parser.add_argument('--sg_output_dir', required=True, help='Output directory for scene graph JSON files')
    parser.add_argument('--svg_output_dir', required=True, help='Output directory for SVG files')
    parser.add_argument('--log_dir', required=True, help='Directory for log files')
    parser.add_argument('--driver_path', required=True, help='Path to Chrome driver')
    return parser.parse_args()

def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'processing_{time.strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
        ]
    )
    return logging.getLogger()

def clean_json_string(json_str):
    json_str = re.sub(r'^.*?"SCENEGRAPH_START', '', json_str)
    json_str = re.sub(r'SCENEGRAPH_END".*$', '', json_str)
    json_str = json_str.replace('\\"', '"')
    json_str = json_str.replace('\\\\', '')
    if json_str.startswith('"') and json_str.endswith('"'):
        json_str = json_str[1:-1]
    return json_str

def process_html_file(html_file, driver, args, logger):
    try:
        file_url = "file://" + os.path.abspath(html_file).replace(os.sep, "/")
        driver.get(file_url)
        time.sleep(2)

        logs = driver.get_log("browser")
        
        # 保存SVG
        try:
            svg_element = driver.find_element(By.TAG_NAME, "svg")
            svg_content = svg_element.get_attribute("outerHTML")
            
            base_name = os.path.basename(html_file)
            svg_output_file = os.path.join(args.svg_output_dir, f"{os.path.splitext(base_name)[0]}.svg")
            
            with open(svg_output_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            logger.info(f"SVG已保存: {svg_output_file}")
        except Exception as e:
            logger.error(f"保存SVG时出错 {html_file}: {e}")
        
        # 处理场景图
        scenegraph_json = None
        for log in logs:
            if "SCENEGRAPH_START" in log["message"]:
                try:
                    cleaned_json_str = clean_json_string(log["message"])
                    scenegraph_json = json.loads(cleaned_json_str)
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误 {html_file}: {e}")
                except Exception as e:
                    logger.error(f"其他错误 {html_file}: {e}")

        if scenegraph_json:
            base_name = os.path.basename(html_file)
            output_filename = base_name.replace('.vl.html', '.sg.json')
            output_path = os.path.join(args.sg_output_dir, output_filename)
            
            with open(output_path, "w", encoding="utf-8") as json_file:
                json.dump(scenegraph_json, json_file, indent=2)
            logger.info(f"场景图已保存: {output_path}")
        else:
            logger.warning(f"未找到场景图数据: {html_file}")

    except Exception as e:
        logger.error(f"处理文件出错 {html_file}: {e}")

def main():
    args = parse_arguments()
    logger = setup_logging(args.log_dir)
    
    # 创建输出目录
    os.makedirs(args.sg_output_dir, exist_ok=True)
    os.makedirs(args.svg_output_dir, exist_ok=True)

    # 设置 WebDriver
    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"browser": "ALL"}

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    service = Service(args.driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        html_files = [f for f in os.listdir(args.input_dir) if f.endswith('.vl.html')]
        
        # 使用tqdm创建进度条
        for filename in tqdm(html_files, desc="Processing files"):
            html_file = os.path.join(args.input_dir, filename)
            process_html_file(html_file, driver, args, logger)
            
    finally:
        driver.quit()

    logger.info("所有文件处理完成")

if __name__ == "__main__":
    main()