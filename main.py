from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from typing import List

from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import asyncio
import os
import tempfile
import warnings

# 忽略警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 加载环境变量
load_dotenv()

app = FastAPI()

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

# 智谱向量模型
embeddings = ZhipuAIEmbeddings(
    api_key=os.getenv("ZHIPU_API_KEY"),
    model="embedding-2",
)

# 向量库
vectordb = Chroma(persist_directory="./db", embedding_function=embeddings)

# ------------------------------
# 上传 PDF 接口（没问题）
# ------------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 解析PDF
    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    os.unlink(tmp_path)

    # 切片入库
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(pages)
    vectordb.add_documents(chunks)

    return {"message": f"已导入 {len(chunks)} 个片段"}

# ------------------------------
# 流式 RAG 问答（已修复）
# ------------------------------
class Question(BaseModel):
    content: str

@app.post("/rag")
async def rag(q: Question):
    results = vectordb.similarity_search(q.content, k=2)
    context = "\n".join([doc.page_content for doc in results])

    prompt = f"""你是企业内部助手，只根据以下资料回答，不要编造。

资料：
{context}

问题：{q.content}
"""

    # 同步转异步 🔥 修复卡顿
    async def stream():
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        sources = [doc.page_content for doc in results]
        yield f'data: {{"event":"sources","data":{sources}}}\n\n'

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f'data: {{"event":"answer","data":"{content}"}}\n\n'
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")

# ------------------------------
# 流式回答工具函数
# ------------------------------
def generate_answer(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": m.role, "content": m.content} for m in messages],
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# ------------------------------
# 单轮对话 /ask（已修复）
# ------------------------------
@app.post("/ask")
async def ask(q: Question):
    messages = [{"role": "user", "content": q.content}]
    return StreamingResponse(generate_answer(messages), media_type="text/plain")

# ------------------------------
# 多轮对话 /chat（正常）
# ------------------------------
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.post("/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(generate_answer(req.messages), media_type="text/plain")
