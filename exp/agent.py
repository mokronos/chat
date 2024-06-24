from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.documents import Document
from langchain.chains import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage

# model = 'tinyllama'
model = 'llama3:8b'

llm = Ollama(model=model)
embeddings = OllamaEmbeddings(model=model)

prompt = ChatPromptTemplate.from_template("""Anwer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

chatprompt = ChatPromptTemplate.from_messages([
                                              MessagesPlaceholder(variable_name="chat_history"),
                                              ("user", "{input}"),
                                              ("user", "Given the above conversation, generate a search query to look up to get information relevant to the conversation")
])

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's questions based on the below context:\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])

document_chain = create_stuff_documents_chain(llm, prompt)

loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()

# retrieval_chain = create_retrieval_chain(retriever, document_chain)
# resp = retrieval_chain.invoke({"input": "how can langsmith help with testing?"})
# print(resp["answer"])


chat_history = [HumanMessage(content="Can LangSmith help test my LLM applications?"), AIMessage(content="Yes!")]

retriever_chain = create_history_aware_retriever(llm, retriever, chatprompt)
retriever_chain = create_retrieval_chain(retriever_chain, document_chain)

resp = retriever_chain.invoke({
    "chat_history": chat_history,
    "input": "Tell me how"
})
print(resp["answer"])
