import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.llms import Ollama

model = "tinyllama"

llm = Ollama(model=model)
emb = OllamaEmbeddings(model=model)

# Load the document
loader = WebBaseLoader(
        web_paths = ("https://lilianweng.github.io/posts/2023-06-23-agent/)",),
        bs_kwargs = dict(
        parse_only = bs4.SoupStrainer(
        class_ = ("post-content", "post-title", "post-header")
        )
    ),
)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=emb)
