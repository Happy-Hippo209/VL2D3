import json
import os
import time
import logging
from typing import Dict, List, Any
from pathlib import Path
from tqdm import tqdm
import argparse

class ScenegraphPruner:
    def __init__(self):
        # 定义需要保留的关键属性
        self.essential_attributes = {
            'marktype',              # 图形类型
            'name',  
            'role',  
            'description',  
            'ariaRoleDescription',
            'x', 'y',           # 位置信息
            'width', 'height',  # 基本尺寸
            'fill', 'stroke',   # 基本样式
            'shape',            # 图形形状
            'text',             # 文本内容
            'items',            # 子元素
        }
        
        # 定义需要特殊处理的属性
        self.special_attributes = {
            'todo1': self._prune_todo1,
            'todo2': self._prune_todo2
        }

    def _prune_todo1(self, encode_obj: Dict) -> Dict:
        pass

    def _prune_todo2(self, transform_obj: List) -> List:
        pass

    def prune_node(self, node: Dict) -> Dict:
        """递归处理节点"""
        if not isinstance(node, dict):
            return node

        pruned_node = {}
        
        # 处理当前节点的属性
        for key, value in node.items():
            # 如果是关键属性，保留
            if key in self.essential_attributes:
                # 特殊处理items数组，因为它们可能包含叶子节点
                if key in ['items'] and isinstance(value, list):
                    # 找出叶子节点
                    leaf_nodes = [item for item in value if isinstance(item, dict) 
                                and 'items' not in item]
                    non_leaf_nodes = [item for item in value if isinstance(item, dict)
                                    and ('items' in item)]
                    
                    # 如果叶子节点超过3个，只保留前3个
                    if len(leaf_nodes) > 3:
                        leaf_nodes = leaf_nodes[:3]
                    
                    # 合并处理后的叶子节点和非叶子节点
                    processed_value = leaf_nodes + non_leaf_nodes
                    # 对所有节点进行递归处理
                    pruned_node[key] = [self.prune_node(item) if isinstance(item, dict) else item 
                                    for item in processed_value]
                
                # 处理其他字典类型的值
                elif isinstance(value, dict):
                    pruned_node[key] = self.prune_node(value)
                # 处理其他列表类型的值
                elif isinstance(value, list):
                    pruned_node[key] = [self.prune_node(item) if isinstance(item, dict) else item 
                                    for item in value]
                # 处理基本类型的值
                else:
                    pruned_node[key] = value
                    
            # 如果是需要特殊处理的属性
            elif key in self.special_attributes:
                processed_value = self.special_attributes[key](value)
                if processed_value is not None:
                    pruned_node[key] = processed_value

        return pruned_node

    def prune(self, scenegraph: Dict) -> Dict:
        """主处理函数"""
        return self.prune_node(scenegraph)
    
def setup_logger(log_dir: str) -> logging.Logger:
    """设置日志记录器"""
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名
    log_file = os.path.join(log_dir, f'scenegraph_pruning_{time.strftime("%Y%m%d_%H%M%S")}.log')
    
    # 配置日志记录器
    logger = logging.getLogger('ScenegraphPruner')
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    
    return logger

def process_scenegraph_files(args):
    """
    批量处理场景图文件
    
    Args:
        input_dir: 输入文件夹路径
        output_dir: 输出文件夹路径
        log_dir: 日志文件夹路径
        suffix: 新文件的后缀名
    """
    # 设置日志记录器
    logger = setup_logger(args.log_dir)
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 创建剪枝器实例
    pruner = ScenegraphPruner()
    
    # 获取所有需要处理的文件
    files = list(Path(args.input_dir).glob("*.sg.json"))
    total_files = min(len(files), args.max_files)  # 限制处理文件数量为10个
    
    # 统计信息
    total_reduction = 0
    
    # 使用tqdm创建进度条
    with tqdm(total=total_files, desc="Processing files") as pbar:
        for i, file in enumerate(files):
            if i >= total_files:
                break
                
            try:
                # 读取输入文件
                with open(file, 'r', encoding='utf-8') as f:
                    scenegraph = json.load(f)
                
                # 获取原始大小
                original_size = len(json.dumps(scenegraph))
                
                # 进行剪枝
                pruned_scenegraph = pruner.prune(scenegraph)
                
                # 获取剪枝后大小
                pruned_size = len(json.dumps(pruned_scenegraph))
                
                # 计算减少百分比
                reduction = 100 * (1 - pruned_size/original_size)
                total_reduction += reduction
                
                # 构建输出文件名
                output_filename = file.stem.replace('.sg', '') + args.suffix
                output_path = Path(args.output_dir) / output_filename
                
                # 保存剪枝后的文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(pruned_scenegraph, f, indent=2)
                
                # 记录日志
                logger.info(f"Processed {file.name}:")
                logger.info(f"  Original size: {original_size:,} characters")
                logger.info(f"  Pruned size: {pruned_size:,} characters")
                logger.info(f"  Reduction: {reduction:.2f}%")
                logger.info(f"  Saved to: {output_path}\n")
                
            except Exception as e:
                logger.error(f"Error processing {file.name}: {str(e)}\n")
            
            # 更新进度条
            pbar.update(1)
    
    # 记录总体统计信息
    logger.info("\nProcessing complete:")
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Average reduction: {total_reduction/total_files:.2f}%")
    
def parse_args():
    parser = argparse.ArgumentParser(description='Prune scenegraph files')
    parser.add_argument('--input_dir', type=str, required=True,
                      help='Input directory containing scenegraph files')
    parser.add_argument('--output_dir', type=str, required=True,
                      help='Output directory for pruned files')
    parser.add_argument('--log_dir', type=str, required=True,
                      help='Directory for log files')
    parser.add_argument('--max_files', type=int, default=10,
                      help='Maximum number of files to process')
    parser.add_argument('--suffix', type=str, default='.pruned.json',
                      help='Suffix for output files')
    return parser.parse_args()
        
if __name__ == "__main__":
    args = parse_args()
    process_scenegraph_files(args)