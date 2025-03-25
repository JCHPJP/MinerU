# Copyright (c) Opendatalab. All rights reserved.
import os  # 操作系统接口模块，用于处理文件路径和目录操作

# 从自定义模块导入必要的组件
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod  # 枚举类型，定义支持的PDF解析方法

# ####################################################
# 参数配置区域（实际使用时需替换具体路径）
# ####################################################
pdf_file_name = "pdf/demo1.pdf"  # 输入PDF文件名（需替换为实际路径）
name_without_suffix = os.path.splitext(pdf_file_name)[0]  # 提取无后缀的文件名（如demo1）

# ####################################################
# 路径准备
# ####################################################
# 定义输出目录
local_image_dir = "output/images"  # 图片输出目录
local_md_dir = "output"           # 文本类数据输出目录
image_dir_name = os.path.basename(local_image_dir)  # 提取图片目录名（用于Markdown中的相对路径）

# 确保输出目录存在
os.makedirs(local_image_dir, exist_ok=True)  # 递归创建目录，存在时不报错

# ####################################################
# 初始化数据读写器
# ####################################################
# 图片写入器（负责保存提取的图片）
image_writer = FileBasedDataWriter(local_image_dir)
# Markdown等文本数据写入器（负责保存结构化数据）
md_writer = FileBasedDataWriter(local_md_dir)

# ####################################################
# 读取PDF原始内容
# ####################################################
# 初始化文件读取器（空路径表示使用当前工作目录）
reader = FileBasedDataReader("")
# 读取PDF文件的二进制内容
pdf_bytes = reader.read(pdf_file_name)

# ####################################################
# PDF处理主流程
# ####################################################
# 创建PDF数据集实例（封装PDF解析逻辑）
pdf_dataset = PymuDocDataset(pdf_bytes)

# 判断PDF类型（OCR模式或直接文本提取模式）
if pdf_dataset.classify() == SupportedPdfParseMethod.OCR:
    # 对扫描件/图片型PDF进行OCR解析
    print("检测到需要OCR处理的PDF类型")
    # 应用解析模型（启用OCR模式）
    analyze_result = pdf_dataset.apply(doc_analyze, ocr=True)
    # 执行OCR模式处理管道（提取文本、图片等）
    processed_result = analyze_result.pipe_ocr_mode(image_writer)
else:
    # 对可提取文本的数字PDF进行处理
    print("检测到可直接提取文本的PDF类型")
    # 应用解析模型（禁用OCR模式）
    analyze_result = pdf_dataset.apply(doc_analyze, ocr=False)
    # 执行文本模式处理管道
    processed_result = analyze_result.pipe_txt_mode(image_writer)

# ####################################################
# 可视化输出
# ####################################################
# 绘制模型解析结果（用边界框标注页面元素）
model_visual_path = os.path.join(local_md_dir, f"{name_without_suffix}_model.pdf")
analyze_result.draw_model(model_visual_path)
print(f"已生成模型解析可视化文件：{model_visual_path}")

# 绘制页面布局分析结果
layout_visual_path = os.path.join(local_md_dir, f"{name_without_suffix}_layout.pdf")
processed_result.draw_layout(layout_visual_path)
print(f"已生成布局分析可视化文件：{layout_visual_path}")

# 绘制文本块分布结果
span_visual_path = os.path.join(local_md_dir, f"{name_without_suffix}_spans.pdf")
processed_result.draw_span(span_visual_path)
print(f"已生成文本块分布可视化文件：{span_visual_path}")

# ####################################################
# 结构化数据输出
# ####################################################
# 生成Markdown内容（包含图片相对路径）
md_content = processed_result.get_markdown(image_dir_name)
# 写入Markdown文件
md_output_path = os.path.join(local_md_dir, f"{name_without_suffix}.md")
processed_result.dump_md(md_writer, md_output_path, image_dir_name)
print(f"已生成Markdown文件：{md_output_path}")

# 生成结构化内容列表（JSON格式）
content_list = processed_result.get_content_list(image_dir_name)
# 写入内容列表文件
content_list_path = os.path.join(local_md_dir, f"{name_without_suffix}_content_list.json")
processed_result.dump_content_list(md_writer, content_list_path, image_dir_name)
print(f"已生成内容列表文件：{content_list_path}")

# 获取中间处理数据（完整解析结果）
middle_json = processed_result.get_middle_json()
# 写入中间数据文件
middle_json_path = os.path.join(local_md_dir, f"{name_without_suffix}_middle.json")
processed_result.dump_middle_json(md_writer, middle_json_path)
print(f"已生成中间数据文件：{middle_json_path}")

# ####################################################
# 注意事项说明
# ####################################################
"""
1. 依赖环境：需要安装 magic_pdf 及其依赖项
2. 输入文件：需确保对PDF文件有读取权限
3. 输出目录：程序需要写入权限
4. OCR支持：如需处理扫描件，需配置Tesseract等OCR引擎
5. 异常处理：本示例未包含完整错误处理逻辑，实际使用时需增强
"""