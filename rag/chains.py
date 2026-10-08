from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from rag.llm import get_llm
from rag.retriever import get_retriever


# ==============================
# LLM
# ==============================

llm = get_llm()


# ==============================
# Question Rewrite Chain
# ==============================

rewrite_prompt = ChatPromptTemplate.from_template("""
You are a question rewriting assistant.

Rewrite the user's question to make it clearer
and more suitable for semantic search in a PDF document.

Do not answer the question.

Only return the rewritten question.

User question:
{question}
""")


rewrite_chain = rewrite_prompt | llm | StrOutputParser()


# ==============================
# Answer Chain
# ==============================

answer_prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant answering questions based only
on the provided context from a PDF document.

Rules:

- Use only the provided context.
- Do not invent or guess information.
- If the answer is not available in the context, say:
  "I don't have enough information in the document."
- Answer clearly and concisely.
- Mention the page number when possible.

Context:

{context}

Question:

{question}

Answer:
""")


answer_chain = answer_prompt | llm | StrOutputParser()


# ==============================
# Format Retrieved Documents
# ==============================

def format_docs(docs):

    formatted = []

    for doc in docs:

        page = doc.metadata.get("page", 0) + 1

        formatted.append(
            f"[Page {page}]\n{doc.page_content}"
        )

    return "\n\n".join(formatted)


# ==============================
# Get Sources
# ==============================

def get_sources(docs):

    sources = []

    for doc in docs:

        page = doc.metadata.get("page", 0) + 1

        source = doc.metadata.get(
            "source",
            "unknown"
        )

        item = {
            "page": page,
            "source": source
        }

        if item not in sources:
            sources.append(item)

    return sources


# ==============================
# Sequential RAG
# ==============================

def sequential_rag(question):

    retriever = get_retriever()

    rewritten_question = rewrite_chain.invoke({
        "question": question
    })

    docs = retriever.invoke(
        rewritten_question
    )

    context = format_docs(docs)

    answer = answer_chain.invoke({
        "context": context,
        "question": question
    })

    sources = get_sources(docs)

    return {
        "original_question": question,
        "rewritten_question": rewritten_question,
        "answer": answer,
        "sources": sources
    }


    # Step 6:
    # Return everything

    return {

        "original_question": question,

        "rewritten_question": rewritten_question,

        "answer": answer,

        "sources": sources
    }