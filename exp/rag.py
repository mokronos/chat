import bs4
from langchain import hub
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
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

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

### Statefully manage chat history ###
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

res = conversational_rag_chain.invoke(
    {"input": "What is written in the document?"},
    config={
        "configurable": {"session_id": "abc123"}
    },  # constructs a key "abc123" in `store`.
)["answer"]

print(res)

res = conversational_rag_chain.invoke(
    {"input": "How could it be improved?"},
    config={"configurable": {"session_id": "abc123"}},
)["answer"]

print(res)

# prompt = hub.pull("rlm/rag-prompt")

# p = """Use the following pieces of context to answer the question at the end.
# If you don't know the answer, please think rationally about an answer from your own knowledge base.
# If the question is unrelated to the context, don't mention the context in your answer.

# Context:
# {context}

# Question:
# {question}
# """

# prompt.messages[0].prompt.template = p


# rag_chain = (
#         {"context": retriever, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
# )

# q = "How do lions communicate?"

# # result = rag_chain.invoke({"question": "Was steht in Abs. III Punkt 3?"})
# result = rag_chain.invoke({"question": q})
# print(result)
