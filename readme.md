目录结构是这样的：
-agent/
--2D3agent.py
--prompt.py

-datasets/
--VLchart/
--VLchart_html/
--VLchart_SG/
--VLchart_SVG/
--VLprompt/
--VLresponse/

-log/

-preprocess/
--embedVegaliteHtml.py
--getSGandSVG.py

-genPrompt.py
-getResponse.py
-preprocess.py

preprocess.py脚本负责处理原始vegalite的json文件（保存在datasets/VLchart），调用两个子脚本,通过preprocess/embedVegaliteHtml.py将json格式嵌入html（保存在datasets/VLchart_html），之后通过preprocess/getSGandSVG.py在浏览器中截取场景图与渲染的SVG（保存在datasets/VLchart_SG与datasets/VLchart_SVG）

genPrompt.py脚本负责执行agent/prompt.py，将场景图与源码批量转化为prompt（保存在datasets/VLprompt），可以自定义

getResponse.py脚本，调用agent/2D3agent.py,得到LLM的回复（保存在datasets/VLresponse）
