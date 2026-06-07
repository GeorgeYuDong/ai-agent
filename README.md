# 企业文档问答系统

基于 RAG（检索增强生成）架构，支持上传 PDF 文档，用自然语言提问。

## 技术栈

- FastAPI — 后端服务
- DeepSeek API — 大语言模型 + ZhiPuAIEmbeddings API
- Chroma — 向量数据库
- LangChain — 文档解析与检索

## 核心功能

- 上传 PDF 文档，自动解析并存入向量数据库
- 自然语言提问，检索最相关片段后由大模型回答
- 返回答案的同时返回原文来源，保证可信度
- 文档中没有的信息明确告知，不胡乱编造

## 快速启动

安装依赖：
pip install -r requirements.txt

配置环境变量：
touch .env
设置下面三个环境变量
- DEEPSEEK_API_KEY
- DEEPSEEK_BASE_URL
- ZHIPU_API_KEY

启动服务：
uvicorn main:app --reload

访问接口文档：
http://localhost:8000/docs

## 接口说明

POST /upload — 上传 PDF 文档
POST /rag    — 针对文档内容提问

## 设计思路

传统做法是把所有文档塞给大模型，但有 token 限制且成本高。
RAG 的做法是先用向量检索找到最相关的片段，只把片段交给模型，
既节省成本，又能处理任意大小的文档库。
