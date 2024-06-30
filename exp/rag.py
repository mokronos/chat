import bs4
from langchain import hub
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

model = "llama3:8b"

llm = Ollama(model=model)
emb = OllamaEmbeddings(model=model)

# Load the document
loader = PyPDFLoader("data/doc.pdf")

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs_splitted = text_splitter.split_documents(docs)
for i, doc in enumerate(docs_splitted):
    doc.metadata["test"] = [str(i) for i in range(10)]
vectorstore = Qdrant.from_documents(
    docs_splitted,
    emb,
    force_recreate=True,
    url="http://localhost:6333",
    collection_name="doc",
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 2, "filter": {"test": ["1", "2"]}})
prompt = hub.pull("rlm/rag-prompt")

p = "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise. Answer in the language of the question.\nQuestion: {question}\nContext: {context}\nAnswer:"
prompt.messages[0].prompt.template = p


rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

q = "Was steht in Abs. III Punkt 3?"

# result = rag_chain.invoke({"question": "Was steht in Abs. III Punkt 3?"})
result = rag_chain.invoke({"question": q})
print(result)
