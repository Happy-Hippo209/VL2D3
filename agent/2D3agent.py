import os
import time
import logging
from openai import OpenAI
from tqdm import tqdm
from pathlib import Path

def setup_logging(log_dir):
    # 创建日志文件名，包含时间戳
    log_file = os.path.join(log_dir, f'response_processing_{time.strftime("%Y%m%d_%H%M%S")}.log')
    
    # 配置logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 这个handler会被设置为只显示进度条
        ]
    )
    
    # 禁用控制台输出，只保留文件输出
    logging.getLogger().handlers[1].setLevel(logging.ERROR)
    
    return logging.getLogger()

def setup_client():
    return OpenAI(
        api_key="sk-NidOuYrSQtUpc5NyFb771dE82aCe422bA1E94aA02c56C886",
        base_url="https://api-zjuvag.truth-ai.com.cn/v1"
    )

def process_single_prompt(client, prompt_path, output_path, logger):
    try:
        # 读取prompt文件
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()

        # 调用API
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_content}
            ]
        )
        
        response = completion.choices[0].message.content
        
        # 保存响应
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response)
            
        logger.info(f"Successfully processed: {prompt_path}")
        return True
    except Exception as e:
        logger.error(f"Error processing {prompt_path}: {str(e)}")
        return False

def main(prompt_dir, response_dir, log_dir):
    # 创建输出目录
    os.makedirs(response_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志
    logger = setup_logging(log_dir)
    
    # 设置OpenAI客户端
    client = setup_client()
    
    # 获取所有prompt文件
    prompt_files = list(Path(prompt_dir).glob('*.prompt.txt'))
    logger.info(f"Found {len(prompt_files)} prompt files to process")
    
    # 处理每个prompt文件
    successful_count = 0
    failed_count = 0
    
    for prompt_file in tqdm(prompt_files, desc="Processing prompts", leave=True):
        # 创建对应的输出路径
        relative_path = prompt_file.stem.replace('.prompt', '')
        output_path = os.path.join(response_dir, f"{relative_path}.response.txt")
        
        # 处理prompt
        if process_single_prompt(client, str(prompt_file), output_path, logger):
            successful_count += 1
        else:
            failed_count += 1
    
    # 记录总结信息
    logger.info(f"Processing completed. Successfully processed: {successful_count}, Failed: {failed_count}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python script.py prompt_dir response_dir log_dir")
        sys.exit(1)
    
    prompt_dir = sys.argv[1]
    response_dir = sys.argv[2]
    log_dir = sys.argv[3]
    
    main(prompt_dir, response_dir, log_dir)