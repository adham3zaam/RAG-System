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

Rules:
- Keep the exact meaning of the original question.
- Do not answer the question.
- Do not add information.
- Return only the rewritten question.

User question:
{question}
""")

rewrite_chain = rewrite_prompt | llm | StrOutputParser()


# ==============================
# Answer Chain
# ==============================

answer_prompt = ChatPromptTemplate.from_template("""
You are a document question-answering assistant.

Your job is to answer the user's question using ONLY
the information inside the CONTEXT below.

IMPORTANT RULES:

1. The CONTEXT is the source of truth.
2. If the answer exists anywhere in the CONTEXT, you MUST answer it.
3. Do NOT say that you don't have enough information if the answer
   is present in the CONTEXT.
4. Do NOT use outside knowledge.
5. Do NOT invent information.
6. Answer in the same language as the user's question.
7. Give a clear and concise answer.
8. When possible, mention the page number shown in the context.

CONTEXT:
==============================
{context}
==============================

USER QUESTION:
{question}

Now answer the user's question using the CONTEXT.
""")


answer_chain = answer_prompt | llm | StrOutputParser()


# ==============================
# Format Retrieved Documents
# ==============================

def format_docs(docs):

    formatted = []

    for doc in docs:

        page = doc.metadata.get("page", 0) + 1

        content = doc.page_content.strip()

        formatted.append(
            f"[Page {page}]\n{content}"
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

    # ==========================================
    # 1. Original Question
    # ==========================================

    original_question = question.strip()

    print("\n==============================")
    print("ORIGINAL QUESTION")
    print("==============================")
    print(original_question)

    # ==========================================
    # 2. Rewrite Question
    # ==========================================

    rewritten_question = rewrite_chain.invoke({
        "question": original_question
    }).strip()

    print("\n==============================")
    print("REWRITTEN QUESTION")
    print("==============================")
    print(rewritten_question)

    # ==========================================
    # 3. Retrieve using ORIGINAL question
    # ==========================================
    #
    # IMPORTANT:
    # We use the original question for retrieval
    # because our previous test showed that it
    # retrieves the correct tourism chunk.
    #

    docs = retriever.invoke(original_question)

    print("\n==============================")
    print("RETRIEVED DOCUMENTS")
    print("==============================")
    print("Number of documents:", len(docs))

    for i, doc in enumerate(docs, start=1):

        print(f"\n--- DOCUMENT {i} ---")

        page = doc.metadata.get("page")

        if page is not None:
            print("Page:", page + 1)
        else:
            print("Page: Unknown")

        print(
            "Source:",
            doc.metadata.get("source", "unknown")
        )

        print("Content:")
        print(doc.page_content[:1500])

    # ==========================================
    # 4. Format context
    # ==========================================

    context = format_docs(docs)

    print("\n==============================")
    print("RETRIEVED CONTEXT")
    print("==============================")
    print(context)
    print("==============================")

    # ==========================================
    # 5. Generate Answer
    # ==========================================

    answer = answer_chain.invoke({
        "context": context,
        "question": original_question
    })

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")
    print(answer)

    # ==========================================
    # 6. Sources
    # ==========================================

    sources = get_sources(docs)

    print("\n==============================")
    print("SOURCES")
    print("==============================")
    print(sources)

    # ==========================================
    # 7. Return result
    # ==========================================

    return {
        "original_question": original_question,
        "rewritten_question": rewritten_question,
        "answer": answer,
        "sources": sources
    }