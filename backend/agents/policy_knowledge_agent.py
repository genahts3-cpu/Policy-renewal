import logging
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from services.llm_service import get_llm
from rag.rag_engine import retrieve_context

logger = logging.getLogger(__name__)

KNOWLEDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert insurance policy advisor. Use the provided policy documents context to answer customer questions accurately.
If the context does not contain enough information, say so honestly and provide general guidance.
Be concise, clear, and helpful.

Policy Context:
{context}

Customer Profile:
{customer_context}"""),
    ("human", "{question}"),
])


async def policy_knowledge_agent(question: str, customer_context: str = "") -> tuple[str, List[str]]:
    docs: List[Document] = retrieve_context(question, k=4)
    context = "\n\n---\n\n".join(d.page_content for d in docs) if docs else "No specific policy documents available in the knowledge base."
    sources = list({d.metadata.get("source", "Policy Document") for d in docs})

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
