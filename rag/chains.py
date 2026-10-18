
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.llm import get_llm
from rag.retriever import get_retriever


# ==========================================
# LLM
# ==========================================

llm = get_llm()
output_parser = StrOutputParser()


# ==========================================
# Question Rewrite Chain
# ==========================================

rewrite_prompt = ChatPromptTemplate.from_template("""
You are a question rewriting assistant.

Rewrite the user's question to make it clearer
and more suitable for semantic search in a PDF document.

Rules:
- Preserve the exact meaning of the original question.
- Do not answer the question.
- Do not add information.
- Return only the rewritten question.

User question:
{question}
""")

rewrite_chain = rewrite_prompt | llm | output_parser


# ==========================================
# Answer Chain - Existing RAG
# ==========================================

answer_prompt = ChatPromptTemplate.from_template("""
You are an academic document question-answering assistant.

Answer the user's question using ONLY the information
inside the CONTEXT below.

Rules:
1. The context is the source of truth.
2. If the answer exists in the context, answer it clearly.
3. Do not use outside knowledge.
4. Do not invent information.
5. Answer in the same language as the user's question.
6. Explain academic concepts when the context supports it.
7. Use examples from the document when relevant.
8. Mention page numbers when available.
9. If the answer is not supported by the context, clearly
   say that the document does not provide enough information.
10. Focus on the lecture content, not unrelated details.

CONTEXT:
==============================
{context}
==============================

USER QUESTION:
{question}

Answer using the context only.
""")

answer_chain = answer_prompt | llm | output_parser


# ==========================================
# Summary Chain
# ==========================================

summary_prompt = ChatPromptTemplate.from_template("""
You are an expert academic study assistant.

Create a clear and useful study summary based ONLY on
the document content provided below.

Requirements:
- Write in the same language as the document.
- Preserve important concepts, definitions, facts, dates,
  formulas, steps, and examples.
- Organize the summary using clear headings and bullet points.
- Explain difficult ideas in simple language.
- Explain relationships between concepts when supported.
- Do not add facts that are not in the document.
- Avoid unnecessary repetition.
- Focus on academic content.
- Exclude cover-page information and instructor names unless
  they are academically relevant to the lecture.
- Do not claim that the summary covers content that was
  not included in the provided section.

DOCUMENT SECTION:
{content}

Write the study summary for this section.
""")

summary_chain = summary_prompt | llm | output_parser


# ==========================================
# Questions Chain
# ==========================================

questions_prompt = ChatPromptTemplate.from_template("""
You are an expert university exam-preparation assistant.

Your task is to create useful exam questions that test the
student's understanding of the actual academic content.

LECTURE CONTENT:
{content}

IMPORTANT RULES:

1. Focus ONLY on educational and academic content.
2. Ignore cover-page information, instructor names, professor
   names, university names, student names, and administrative
   details.
3. Do not ask who prepared or presented the lecture.
4. Focus on the important concepts, definitions, explanations,
   methods, steps, formulas, examples, comparisons, advantages,
   disadvantages, and relationships discussed in the lecture.
5. Generate 5 to 8 meaningful questions for this section
   when the content supports that number.
6. Include a useful mixture of:
   - Definition questions.
   - Explain and understand questions.
   - Compare and contrast questions.
   - How and why questions.
   - Application questions based on lecture examples.
   - Multiple-choice questions with four options (A, B, C, D).
   - Questions about steps, methods, or processes.
7. Include the correct answer for every question.
8. For multiple-choice questions, identify the correct option
   and explain the answer when the content supports it.
9. Use the same language as the lecture content.
10. Every question must test a meaningful learning objective.
11. Avoid duplicate questions and irrelevant minor details.
12. Never invent facts, concepts, options, or answers.
13. If a section contains little academic content, generate
    only questions that are supported by that section.
14. Return multiple questions when the content supports them.
    Do not return just one example.
15. Do not create questions merely to reach a target number.

OUTPUT FORMAT:

Question 1: [Question]
Answer: [Correct answer]

Question 2: [Question]
Answer: [Correct answer]

For multiple-choice questions:

Question: [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
Correct answer: [Letter and answer]
Explanation: [Explanation supported by the lecture]

Generate the questions now.
""")

questions_chain = questions_prompt | llm | output_parser


# ==========================================
# Format Retrieved Documents
# ==========================================

def format_docs(docs):
    formatted = []

    for doc in docs:
        page_value = doc.metadata.get("page")
        page = (
            page_value + 1
            if isinstance(page_value, int)
            else "Unknown"
        )

        content = doc.page_content.strip()

        formatted.append(f"[Page {page}]\n{content}")

    return "\n\n".join(formatted)


# ==========================================
# Get Sources
# ==========================================

def get_sources(docs):
    sources = []

    for doc in docs:
        page_value = doc.metadata.get("page")

        page = (
            page_value + 1
            if isinstance(page_value, int)
            else None
        )

        item = {
            "page": page,
            "source": doc.metadata.get("source", "unknown")
        }

        if item not in sources:
            sources.append(item)

    return sources


# ==========================================
# Existing RAG Question Answering
# ==========================================

def sequential_rag(question):
    retriever = get_retriever()
    original_question = question.strip()

    print("\n==============================")
    print("ORIGINAL QUESTION")
    print("==============================")
    print(original_question)

    rewritten_question = rewrite_chain.invoke({
        "question": original_question
    }).strip()

    print("\nREWRITTEN QUESTION:")
    print(rewritten_question)

    # Preserve the existing retrieval behavior.
    docs = retriever.invoke(original_question)

    print("\nRETRIEVED DOCUMENTS:", len(docs))

    context = format_docs(docs)

    answer = answer_chain.invoke({
        "context": context,
        "question": original_question
    })

    sources = get_sources(docs)

    return {
        "original_question": original_question,
        "rewritten_question": rewritten_question,
        "answer": answer,
        "sources": sources
    }


# ==========================================
# Read Full Document
# ==========================================

def read_document_content(markdown_path):
    """
    Read the complete converted Markdown document.
    Used for document-wide summaries and questions.
    """

    with open(markdown_path, "r", encoding="utf-8") as file:
        content = file.read().strip()

    if not content:
        raise ValueError("The document is empty.")

    return content


# ==========================================
# Split Long Documents
# ==========================================

def split_document_content(
    content,
    chunk_size=12000,
    chunk_overlap=500
):
    """
    Split the full document into manageable sections
    for processing by the language model.
    """

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    return splitter.split_text(content)


# ==========================================
# Generate Summary
# ==========================================

def generate_summary(markdown_path):
    """
    Summarize each section of the document and combine
    the summaries into one coherent study summary.
    """

    content = read_document_content(markdown_path)
    sections = split_document_content(content)

    section_summaries = []

    for index, section in enumerate(sections, start=1):
        print(
            f"Generating summary for section "
            f"{index}/{len(sections)}"
        )

        section_summary = summary_chain.invoke({
            "content": section
        })

        section_summaries.append(
            f"Section {index} Summary:\n{section_summary}"
        )

    combined_summaries = "\n\n".join(section_summaries)

    final_summary_prompt = ChatPromptTemplate.from_template("""
You are an expert academic editor.

Combine the following section summaries into one coherent
study summary for the original document.

Rules:
- Preserve important concepts and details.
- Remove repeated information.
- Organize the output with headings and bullet points.
- Use the same language as the summaries.
- Do not introduce facts that are not present in the summaries.
- Focus on academic content.
- Keep important definitions, steps, formulas, and examples.

SECTION SUMMARIES:
{summaries}

Write the final study summary.
""")

    final_summary_chain = (
        final_summary_prompt | llm | output_parser
    )

    return final_summary_chain.invoke({
        "summaries": combined_summaries
    })


# ==========================================
# Generate Important Questions
# ==========================================

def generate_questions(markdown_path, summary=None):
    """
    Generate academic questions from the entire document.
    Process sections separately, then combine and deduplicate
    the questions while preserving their answers.
    """

    content = read_document_content(markdown_path)
    sections = split_document_content(content)

    question_sets = []

    for index, section in enumerate(sections, start=1):
        print(
            f"Generating questions for section "
            f"{index}/{len(sections)}"
        )

        section_questions = questions_chain.invoke({
            "content": section
        })

        question_sets.append(
            f"Section {index} Questions:\n{section_questions}"
        )

    combined_questions = "\n\n".join(question_sets)

    final_questions_prompt = ChatPromptTemplate.from_template("""
You are an academic exam-question organizer.

Organize and deduplicate candidate questions generated
from different sections of the SAME lecture.

CANDIDATE QUESTIONS:
{questions}

RULES:

1. Keep questions about actual academic content.
2. Remove questions about instructor names, professor names,
   university names, cover pages, and administrative details.
3. Remove duplicate and near-duplicate questions only.
4. Preserve questions that test different concepts.
5. Preserve answers, MCQ options, correct answers,
   and explanations.
6. Do not invent questions, facts, options, or answers.
7. Aim for 15 to 20 distinct questions for a sufficiently
   long lecture when the candidate questions support this.
8. If fewer questions are supported, return fewer.
9. Organize questions by topic when possible.
10. Number all questions sequentially from 1.
11. Keep the same language as the lecture.
12. Return the complete final question set, not just a sample.
13. Do not discard useful questions simply to shorten the output.
14. Include answers for every question.

FINAL QUESTIONS WITH ANSWERS:
""")

    final_questions_chain = (
        final_questions_prompt | llm | output_parser
    )

    final_questions = final_questions_chain.invoke({
        "questions": combined_questions
    })

    return final_questions
