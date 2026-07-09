import logging
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from services.llm_service import get_llm
from rag.rag_engine import retrieve_context
from services.chroma_service import get_all_documents

logger = logging.getLogger(__name__)

KNOWLEDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an Insurance Policy Assistant.

Use ONLY the provided context below to answer the customer's question.
Never make assumptions or generate information not present in the context.
If the information is not available in the context, respond exactly:
"I could not find this information in the uploaded policy documents."

Never hallucinate. Never generate policy information not present in context.
NEVER use markdown formatting. No bold (**), no bullet points, no numbered lists, no headers. Respond in plain text only.
ALWAYS display monetary amounts in Indian Rupees (INR, ₹) using exchange rate 1 USD = 83 INR.

Policy Context:
{context}

Customer Profile:
{customer_context}"""),
    ("human", "{question}"),
])


async def policy_knowledge_agent(question: str, customer_context: str = "") -> tuple[str, List[str]]:
    # Search RAG vectorstore (policy_knowledge collection)
    docs: List[Document] = retrieve_context(question, k=4)
    rag_context = "\n\n---\n\n".join(d.page_content for d in docs) if docs else ""
    sources = list({d.metadata.get("source", "Policy Document") for d in docs})

    # Also search uploaded documents from chroma_service collections
    uploaded_docs = get_all_documents(search=question)
    uploaded_context = "\n\n---\n\n".join(
        d["content"] for d in uploaded_docs[:6] if d.get("content")
    ) if uploaded_docs else ""

    context = "\n\n---\n\n".join(filter(None, [rag_context, uploaded_context])) or "No specific policy documents available in the knowledge base."
    if uploaded_docs:
        sources += list({d["source_file"] for d in uploaded_docs[:6] if d.get("source_file")})

    try:
        llm = get_llm(temperature=0.2)
        chain = KNOWLEDGE_PROMPT | llm
        result = await chain.ainvoke({
            "context": context,
            "customer_context": customer_context,
            "question": question,
        })
        return result.content, sources
    except Exception as e:
        logger.error(f"Policy knowledge agent failed: {e}")
        return "I'm unable to retrieve policy information at the moment. Please contact support.", []
