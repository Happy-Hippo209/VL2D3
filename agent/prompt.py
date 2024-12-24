import os
import json
import argparse
import logging
import time
from tqdm import tqdm

class VLtoD3PromptGenerator:
    def __init__(self, vl_path, sg_path, output_path, log_dir):
        """
        初始化类

        Parameters:
        vl_path (str): Vega-Lite源代码文件夹路径。
        sg_path (str): 场景图文件夹路径。
        output_path (str): 保存Prompt的文件夹路径。
        log_dir (str): 日志文件夹路径。
        """
        self.vl_path = vl_path
        self.sg_path = sg_path
        self.output_path = output_path

        # 创建输出文件夹和日志文件夹，如果不存在
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        # 使用时间戳创建日志文件名
        log_file = os.path.join(log_dir, f'prompt_processing_{time.strftime("%Y%m%d_%H%M%S")}.log')

        # 配置日志
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_json(self, file_path):
        """加载JSON文件。"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_prompt(self, prompt, file_name):
        """将生成的Prompt保存到文件。"""
        output_file = os.path.join(self.output_path, file_name)
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(prompt)

    def generate_prompt(self, vl_content, sg_content):
        """
        生成Prompt。

        Parameters:
        vl_content (dict): Vega-Lite源代码内容。
        sg_content (dict): 场景图内容。

        Returns:
        str: 用于大语言模型的Prompt。
        """
        return (
            "Convert the following Vega-Lite specification to D3.js code.\n\n"
            "Vega-Lite Specification:\n"
            f"{json.dumps(vl_content, indent=2)}\n\n"
            "Scene Graph Representation:\n"
            f"{json.dumps(sg_content, indent=2)}\n\n"
            "D3.js Code:"  # 语言模型将在这里生成对应的D3.js代码。
        )

    def process_files(self):
        """
        批量处理文件并生成Prompt。
        """
        vl_files = [f for f in os.listdir(self.vl_path) if f.endswith('.json')]

        for vl_file in tqdm(vl_files, desc="Processing files"):
            vl_file_path = os.path.join(self.vl_path, vl_file)
            sg_file_path = os.path.join(self.sg_path, vl_file.replace('.vl.json', '.sg.json'))

            # 确保场景图文件存在
            if not os.path.exists(sg_file_path):
                logging.warning(f"Scene graph file not found for {vl_file}. Skipping.")
                continue

            # 加载Vega-Lite和场景图内容
            try:
                vl_content = self.load_json(vl_file_path)
                sg_content = self.load_json(sg_file_path)
            except Exception as e:
                logging.error(f"Error loading files for {vl_file}: {e}")
                continue

            # 生成Prompt
            try:
                prompt = self.generate_prompt(vl_content, sg_content)

                # 保存Prompt
                prompt_file_name = vl_file.replace('.vl.json', '.prompt.txt')
                self.save_prompt(prompt, prompt_file_name)
                logging.info(f"Processed and saved prompt for {vl_file}.")
            except Exception as e:
                logging.error(f"Error generating/saving prompt for {vl_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate prompts from Vega-Lite and Scene Graph files.")
    parser.add_argument("vl_path", type=str, help="Path to the directory containing Vega-Lite files.")
    parser.add_argument("sg_path", type=str, help="Path to the directory containing Scene Graph files.")
    parser.add_argument("output_path", type=str, help="Path to the directory to save generated prompts.")
    parser.add_argument("--log-dir", type=str, default="./logs", help="Directory for log files.")

    args = parser.parse_args()

    generator = VLtoD3PromptGenerator(args.vl_path, args.sg_path, args.output_path, args.log_dir)
    generator.process_files()