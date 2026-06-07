import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_community.embeddings import ZhipuAIEmbeddings
from openai import OpenAI
import os

load_dotenv()

# 模拟几段文档内容
docs = [
    "公司年假政策：工作满1年享有5天年假，满3年10天，满5年15天。",
    "报销流程：先填写报销单，附上发票，提交给直属上级审批，财务3个工作日内到账。",
    "请假流程：提前一天在系统中申请，直属上级审批后生效。病假需提供医院证明。",
]

# 切割文本
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
chunks = splitter.create_documents(docs)

# ==========正确初始化ZhiPu Embedding（关键）==========
embeddings = ZhipuAIEmbeddings(
    api_key=os.getenv("ZHIPU_API_KEY"),
    model="embedding-2",  # 最稳定
)

#存入向量库
vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./db"
)

print("文档已存入，共", len(chunks), "个片段")

client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = os.getenv("DEEPSEEK_BASE_URL"),
)

def rag_answer(query: str):
    # 检索片段
    results = vectordb.similarity_search(query, k=2) 
    context = "\n".join([doc.page_content for doc in results])

    # 拼装prompt
    prompt = f"""你是一个企业内部助手，只根据以下资料回答问题，不要编造
    资料:
    {context}
    问题：{query}
    """ 
    # 让模型回答
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = [{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 测试检索示例
print(rag_answer("我工作了五年，有几天年假"))
print("---")
print(rag_answer("报销要几天到账"))
print("---")
print(rag_answer("公司有健身房吗"))

'''
query = "我工作了两年，有几天年假"
res = vectordb.similarity_search(query, k=1)
print("\n检索结果：")

for i, doc in enumerate(res):
    print(f"片段{i+1}：{doc.page_content}")

'''
#print(res[0].page_content)
