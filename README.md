# Vega-Lite2D3图表分析流水线


## 项目结构

```
.
├── agent/
│ ├── 2D3agent.py # LLM交互代理
│ └── prompt.py # Prompt生成逻辑
│
├── datasets/
│ ├── VLchart/ # 原始Vega-Lite JSON文件
│ ├── VLchart_html/ # 嵌入HTML的JSON
│ ├── VLchart_SG/ # 场景图
│ ├── VLchart_SVG/ # Vegalite在浏览器渲染的SVG文件
│ ├── VLprompt/ # 生成的prompts
│ └── VLresponse/ # LLM响应
│
├── logs/ # 日志文件
│
├── preprocess/
│ ├── embedVegaliteHtml.py # JSON转HTML转换器
│ └── getSGandSVG.py # 基于浏览器截取SVG与scenegraph
│
├── genPrompt.py # Prompt生成脚本
├── getResponse.py # LLM响应收集脚本
└── preprocess.py # 数据预处理脚本
```

## 处理流程

1. **预处理** (`preprocess.py`)
   - 读取`datasets/VLchart`中的原始Vega-Lite JSON文件
   - 使用`embedVegaliteHtml.py`将JSON转换为HTML
   - 使用`getSGandSVG.py`捕获场景图和SVG
   - 输出到`VLchart_html`、`VLchart_SG`和`VLchart_SVG`目录

2. **Prompt生成** (`genPrompt.py`)
   - 执行`agent/prompt.py`
   - 将场景图与源代码组合
   - 生成可自定义的prompts
   - 将结果保存在`datasets/VLprompt`

3. **响应收集** (`getResponse.py`)
   - 使用`agent/2D3agent.py`
   - 与LLM接口交互
   - 将响应存储在`datasets/VLresponse`

## 依赖项
Python 3.9

其他见requirement.txt
