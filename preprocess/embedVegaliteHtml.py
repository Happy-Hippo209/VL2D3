import os
import json
import argparse
import glob
from tqdm import tqdm
import logging
from datetime import datetime

def setup_logging(log_dir):
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名（包含时间戳）
    log_filename = os.path.join(log_dir, f'embed_html_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            # logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    return logging.getLogger(__name__)

def embed_vegalite_to_html(input_dir, output_dir, log_dir, pattern="*.vl.json"):
    # 设置日志记录器
    logger = setup_logging(log_dir)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # HTML模板
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
        <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
        <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    </head>
    <body>
        <div id="vis" style="width: 800px; height: 600px;"></div>
        <script>
            var vlSpec = {chart_spec};
            // Add default size if not specified
            if (!vlSpec.width) vlSpec.width = 800;
            if (!vlSpec.height) vlSpec.height = 600;
            
            vegaEmbed('#vis', vlSpec, {renderer: 'svg'}).then((result) => {{
                const view = result.view;
                // 获取完整的场景图
                const scenegraph = view.scenegraph();
                console.log('SCENEGRAPH_START' + JSON.stringify(scenegraph) + 'SCENEGRAPH_END');
            }}).catch(console.error);
        </script>
    </body>
    </html>
    """

    # 获取所有vega-lite json文件
    chart_files = glob.glob(os.path.join(input_dir, pattern))
    
    if not chart_files:
        logger.warning(f"No files matching pattern '{pattern}' found in {input_dir}")
        return

    # 使用tqdm创建进度条
    for file_path in tqdm(chart_files, desc="Embed HTML", unit="file"):
        try:
            # 读取Vega-Lite JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                vl_spec = json.load(f)

            # 将JSON嵌入HTML模板
            html_content = html_template.replace("{chart_spec}", json.dumps(vl_spec))

            # 确定输出文件名
            file_name = os.path.splitext(os.path.basename(file_path))[0] + ".html"
            output_path = os.path.join(output_dir, file_name)

            # 写入HTML内容到输出文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Generated: {output_path}")
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Convert Vega-Lite JSON files to HTML')
    parser.add_argument('input_dir', help='Directory containing Vega-Lite JSON files')
    parser.add_argument('output_dir', help='Directory for output HTML files')
    parser.add_argument('--log-dir', default='logs', help='Directory for log files')
    parser.add_argument('--pattern', default='*.vl.json', 
                        help='File pattern to match (default: *.vl.json)')

    args = parser.parse_args()

    embed_vegalite_to_html(args.input_dir, args.output_dir, args.log_dir, args.pattern)

if __name__ == "__main__":
    main()