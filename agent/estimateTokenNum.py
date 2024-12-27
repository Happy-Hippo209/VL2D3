import tiktoken
import os
from pathlib import Path

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    计算给定文本的tokens数量

    Parameters:
    -----------
    text : str
        需要计算tokens的文本
    model : str
        使用的模型名称，默认为'gpt-4'

    Returns:
    --------
    int
        tokens数量
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        print(f"Warning: model {model} not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

def analyze_prompt_file(file_path: str, model: str = "gpt-4") -> dict:
    """
    分析prompt文件的tokens信息

    Parameters:
    -----------
    file_path : str
        prompt文件的路径
    model : str
        使用的模型名称

    Returns:
    --------
    dict
        包含tokens统计信息的字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tokens_count = count_tokens(content, model)
        file_size = os.path.getsize(file_path)
        
        return {
            'file_name': os.path.basename(file_path),
            'tokens_count': tokens_count,
            'file_size_bytes': file_size,
            'file_size_kb': round(file_size / 1024, 2)
        }
    except Exception as e:
        return {
            'file_name': os.path.basename(file_path),
            'error': str(e)
        }

# 使用示例
if __name__ == "__main__":
    prompt_file = r"D:\files\study2024\VL2D3_20241224\datasets\VLprompt\vl_0002.prompt.txt"
    
    # 分析单个文件
    result = analyze_prompt_file(prompt_file)
    
    if 'error' in result:
        print(f"Error analyzing {result['file_name']}: {result['error']}")
    else:
        print(f"File: {result['file_name']}")
        print(f"Tokens count: {result['tokens_count']}")
        print(f"File size: {result['file_size_kb']} KB")
        
    # # 如果您想批量分析某个目录下的所有prompt文件：
    # prompt_dir = Path(r"D:\files\study2024\VL2D3_20241224\datasets\VLprompt")
    # all_results = []
    
    # for prompt_file in prompt_dir.glob("*.prompt.txt"):
    #     result = analyze_prompt_file(str(prompt_file))
    #     all_results.append(result)
        
    # # 打印汇总信息
    # total_tokens = sum(r['tokens_count'] for r in all_results if 'tokens_count' in r)
    # print(f"\nTotal files analyzed: {len(all_results)}")
    # print(f"Total tokens: {total_tokens}")