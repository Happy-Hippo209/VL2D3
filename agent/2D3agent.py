import os
import time
import logging
import tiktoken
from openai import OpenAI
from tqdm import tqdm
from pathlib import Path
from enum import Enum, auto
from typing import Tuple, Optional

class PromptFilterReason(Enum):
    """过滤原因枚举"""
    TOKEN_LIMIT_EXCEEDED = auto()
    EMPTY_CONTENT = auto()
    INVALID_FORMAT = auto()
    # 可以继续添加其他过滤原因

class PromptFilter:
    """Prompt过滤器类"""
    def __init__(self, max_tokens: int = 5000, model: str = "gpt-4o"):
        self.max_tokens = max_tokens
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def check_prompt(self, content: str) -> Tuple[bool, Optional[PromptFilterReason]]:
        """
        检查prompt是否满足发送条件

        Parameters:
        -----------
        content : str
            prompt内容

        Returns:
        --------
        Tuple[bool, Optional[PromptFilterReason]]
            (是否通过检查, 未通过原因)
        """
        # 检查是否为空
        if not content.strip():
            return False, PromptFilterReason.EMPTY_CONTENT

        # 检查token数量
        token_count = len(self.encoding.encode(content))
        if token_count > self.max_tokens:
            return False, PromptFilterReason.TOKEN_LIMIT_EXCEEDED

        # 通过所有检查
        return True, None

def setup_logging(log_dir):
    log_file = os.path.join(log_dir, f'response_processing_{time.strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.getLogger().handlers[1].setLevel(logging.ERROR)
    
    return logging.getLogger()

def setup_client():
    return OpenAI(
        api_key="sk-NidOuYrSQtUpc5NyFb771dE82aCe422bA1E94aA02c56C886",
        base_url="https://api-zjuvag.truth-ai.com.cn/v1"
    )

def process_single_prompt(client, prompt_path, output_path, logger, prompt_filter):
    try:
        # 读取prompt文件
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()

        # 使用过滤器检查prompt
        is_valid, filter_reason = prompt_filter.check_prompt(prompt_content)
        
        if not is_valid:
            reason_msg = {
                PromptFilterReason.TOKEN_LIMIT_EXCEEDED: 
                    f"Token count exceeds limit of {prompt_filter.max_tokens}",
                PromptFilterReason.EMPTY_CONTENT: 
                    "Prompt content is empty",
                PromptFilterReason.INVALID_FORMAT: 
                    "Invalid prompt format"
            }.get(filter_reason, "Unknown reason")
            
            logger.warning(f"Skipped {prompt_path}: {reason_msg}")
            return False

        # 调用API
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content":( 
                    "You are an expert in data visualization, specializing in converting "
                    "Vega-Lite specifications to D3.js v7 code. Follow these guidelines:\n"
                    "- Generate complete, self-contained HTML files\n"
                    "- Use modern D3.js v7 syntax and best practices\n"
                    "- Ensure responsive design principles\n"
                    "- Maintain visualization accuracy and aesthetics\n"
                    "- Include clear code comments\n"
                    "- Focus on performance and cross-browser compatibility"
                )},
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
    os.makedirs(response_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    logger = setup_logging(log_dir)
    client = setup_client()
    prompt_filter = PromptFilter(max_tokens=5000)  # 创建过滤器实例
    
    prompt_files = list(Path(prompt_dir).glob('*.prompt.txt'))
    logger.info(f"Found {len(prompt_files)} prompt files to process")
    
    successful_count = 0
    failed_count = 0
    skipped_count = 0
    
    for prompt_file in tqdm(prompt_files, desc="Processing prompts", leave=True):
        relative_path = prompt_file.stem.replace('.prompt', '')
        output_path = os.path.join(response_dir, f"{relative_path}.response.html")
        
        result = process_single_prompt(client, str(prompt_file), output_path, logger, prompt_filter)
        
        if result:
            successful_count += 1
        else:
            if "Skipped" in logger.handlers[0].baseFilename:  # 检查是否是被过滤掉的
                skipped_count += 1
            else:
                failed_count += 1
    
    logger.info(f"Processing completed:")
    logger.info(f"  Successfully processed: {successful_count}")
    logger.info(f"  Failed: {failed_count}")
    logger.info(f"  Skipped: {skipped_count}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python script.py prompt_dir response_dir log_dir")
        sys.exit(1)
    
    prompt_dir = sys.argv[1]
    response_dir = sys.argv[2]
    log_dir = sys.argv[3]
    
    main(prompt_dir, response_dir, log_dir)