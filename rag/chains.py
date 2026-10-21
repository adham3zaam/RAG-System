# rag/chains.py

import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.llm import get_llm
from rag.retriever import get_retriever


# =========================================================
# 1. INITIALIZE LLM AND OUTPUT PARSER
# =========================================================

llm = get_llm()
output_parser = StrOutputParser()


# =========================================================
# 2. QUESTION REWRITING PROMPT
# =========================================================

rewrite_prompt = ChatPromptTemplate.from_template(
    """
You are a question-rewriting assistant for a university lecture
document question-answering system.

Rewrite the student's question into a clear, specific search query
that will help retrieve the most relevant information from the lecture.

Rules:
- Preserve the student's original meaning.
- Keep important technical terms.
- Use the conversation question as the main source of intent.
- Do not answer the question.
- Do not add facts that are not provided.
- Return only the rewritten search query.

Student question:
{question}
"""
)

rewrite_chain = rewrite_prompt | llm | output_parser


# =========================================================
# 3. ANSWER PROMPT
# =========================================================

answer_prompt = ChatPromptTemplate.from_template(
    """
You are DocuMind AI, a helpful university study assistant.

Answer the student's question using the lecture context provided below.

LECTURE CONTEXT:
{context}

STUDENT QUESTION:
{question}

Instructions:
1. Answer the actual question directly.
2. Explain the relevant concepts clearly and in sufficient detail.
3. Use examples when they are supported by the lecture.
4. Preserve important definitions, technical terms, formulas, and steps.
5. Organize long answers using headings or bullet points when useful.
6. Do not invent information or claim that the lecture says something
   that is not supported by the context.
7. If the context does not contain enough information, clearly explain
   that the answer cannot be determined from the available lecture.
8. Do not answer unrelated questions using outside assumptions.

Write a clear, educational answer.
"""
)

answer_chain = answer_prompt | llm | output_parser


# =========================================================
# 4. DETAILED SUMMARY PROMPT
# =========================================================

summary_prompt = ChatPromptTemplate.from_template(
    """
You are an expert university teaching assistant.

Your task is to create detailed study notes from ONE SECTION of a
university lecture. The section may be part of a longer document.

LECTURE SECTION:
{context}

Write a comprehensive, accurate summary of the provided section.

REQUIREMENTS:

1. Cover the important information throughout the entire section,
   not just its opening paragraphs.
2. Explain the main ideas and concepts in clear language.
3. Include important definitions, terminology, classifications,
   properties, comparisons, and explanations.
4. Preserve formulas, equations, algorithms, examples, and procedures
   when they appear in the section.
5. Explain relationships between concepts when the text supports them.
6. Include important details that a student may need for an exam.
7. Use descriptive headings and subheadings.
8. Use bullet points for lists and numbered steps for procedures.
9. Explain technical concepts rather than simply listing keywords.
10. Do not add facts that are absent from the provided section.
11. Do not summarize only the introduction or the first few paragraphs.
12. Do not include unrelated information about the lecturer, document
    administration, or file metadata unless academically relevant.
13. If the section is short, summarize all its meaningful content.
14. Return the actual summary, not an introduction about what you will do.
15. Never return an empty response or a placeholder.

Produce detailed notes that help a student understand and revise
the material without needing to reread every sentence.
"""
)

summary_chain = summary_prompt | llm | output_parser


# =========================================================
# 5. IMPORTANT QUESTIONS PROMPT
# =========================================================

questions_prompt = ChatPromptTemplate.from_template(
    """
You are an expert university instructor preparing exam revision
questions from a lecture section.

LECTURE SECTION:
{context}

Generate IMPORTANT STUDY QUESTIONS based on the academic content
of this section.

COVERAGE REQUIREMENTS:

1. Examine the entire section, including its beginning, middle,
   and end.
2. Focus on concepts, definitions, explanations, mechanisms,
   classifications, comparisons, examples, formulas, and procedures.
3. Do not focus on the lecturer's name, document title, course
   administration, or other unimportant personal details.
4. Avoid asking multiple questions that test exactly the same idea.
5. Do not ask questions whose answers are unrelated to the lecture.
6. Make the questions useful for understanding and exam preparation.
7. Generate approximately 8-12 questions for a substantial section.
   For a short section, generate fewer questions if appropriate.
8. Include a mixture of:
   - Definition and concept questions
   - Explanation and understanding questions
   - Comparison questions, when applicable
   - Application or problem-solving questions, when supported
   - Questions about important steps, properties, or relationships
9. Do not invent concepts that do not appear in the section.
10. Every question must be based on the actual lecture content.
11. Include a concise, accurate answer below each question.
12. If the section contains formulas, procedures, or examples,
    include questions about them where relevant.

Use this format:

## Question 1: [Question]

**Answer:** [Answer based on the lecture]

## Question 2: [Question]

**Answer:** [Answer based on the lecture]

Continue numbering the questions.

Return only the questions and their answers.
Do not return a generic introduction or a conclusion.
"""
)

questions_chain = questions_prompt | llm | output_parser


# =========================================================
# 6. DOCUMENT HELPER FUNCTIONS
# =========================================================

def format_docs(docs):
    """
    Convert retrieved LangChain documents into one context string.
    Include page information when available.
    """
    formatted_docs = []

    for doc in docs:
        content = doc.page_content.strip()

        if not content:
            continue

        page = doc.metadata.get("page")

        if page is not None:
            try:
                page_label = int(page) + 1
            except (TypeError, ValueError):
                page_label = page

            formatted_docs.append(
                f"[Page {page_label}]\n{content}"
            )
        else:
            formatted_docs.append(content)

    return "\n\n---\n\n".join(formatted_docs)


def get_sources(docs):
    """
    Return unique source/page references for the frontend.
    """
    sources = []
    seen = set()

    for doc in docs:
        source = doc.metadata.get("source", "Lecture document")
        page = doc.metadata.get("page")

        if page is not None:
            try:
                page_label = int(page) + 1
            except (TypeError, ValueError):
                page_label = page

            source_label = f"{os.path.basename(str(source))} - Page {page_label}"
        else:
            source_label = os.path.basename(str(source))

        if source_label not in seen:
            seen.add(source_label)
            sources.append(source_label)

    return sources


# =========================================================
# 7. FOLLOW-UP QUESTION: RETRIEVAL-AUGMENTED GENERATION
# =========================================================

def sequential_rag(question):
    """
    Answer a student's follow-up question using relevant lecture chunks.

    Returns:
        original_question
        rewritten_question
        answer
        sources
    """
    original_question = (question or "").strip()

    if not original_question:
        raise ValueError("Please enter a question.")

    print("\n" + "=" * 50)
    print("DOCUMIND AI: PROCESSING STUDENT QUESTION")
    print("=" * 50)

    # Step 1: Rewrite the question for better retrieval.
    rewritten_question = rewrite_chain.invoke(
        {"question": original_question}
    ).strip()

    if not rewritten_question:
        rewritten_question = original_question

    print("Original question:", original_question)
    print("Search query:", rewritten_question)

    # Step 2: Retrieve relevant lecture chunks.
    retriever = get_retriever()
    docs = retriever.invoke(rewritten_question)

    if not docs:
        return {
            "original_question": original_question,
            "rewritten_question": rewritten_question,
            "answer": (
                "I could not find relevant information in the uploaded "
                "lecture. Please try rephrasing your question."
            ),
            "sources": [],
        }

    # Step 3: Format the retrieved context.
    context = format_docs(docs)

    if not context:
        raise ValueError(
            "The retrieved lecture sections contain no readable text."
        )

    # Step 4: Generate an answer grounded in the lecture.
    answer = answer_chain.invoke(
        {
            "context": context,
            "question": original_question,
        }
    ).strip()

    # Step 5: Return the answer and source references.
    result = {
        "original_question": original_question,
        "rewritten_question": rewritten_question,
        "answer": answer,
        "sources": get_sources(docs),
    }

    print("Retrieved chunks:", len(docs))
    print("Answer length:", len(answer))
    print("=" * 50)

    return result


# =========================================================
# 8. READ THE COMPLETE MARKDOWN DOCUMENT
# =========================================================

def read_document_content(markdown_path):
    """
    Read the Markdown file created from the uploaded PDF.
    """
    if not markdown_path:
        raise ValueError("The Markdown file path was not provided.")

    if not os.path.isfile(markdown_path):
        raise FileNotFoundError(
            f"Lecture Markdown file was not found: {markdown_path}"
        )

    with open(markdown_path, "r", encoding="utf-8") as file:
        content = file.read().strip()

    if not content:
        raise ValueError(
            "The converted lecture is empty. Please upload a readable PDF."
        )

    print("\n" + "=" * 50)
    print("READING LECTURE DOCUMENT")
    print("File:", markdown_path)
    print("Characters:", len(content))
    print("=" * 50)

    return content


# =========================================================
# 9. SPLIT THE DOCUMENT INTO MANAGEABLE SECTIONS
# =========================================================

def split_document_content(
    content,
    chunk_size=6000,
    chunk_overlap=400,
):
    """
    Split the complete lecture into overlapping sections.

    Overlap helps preserve context between adjacent sections.
    """
    if not content or not content.strip():
        raise ValueError("Cannot split an empty lecture document.")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            " ",
            "",
        ],
        length_function=len,
    )

    sections = splitter.split_text(content)

    sections = [
        section.strip()
        for section in sections
        if section and section.strip()
    ]

    if not sections:
        raise ValueError(
            "No readable sections could be created from the lecture."
        )

    print("Total document sections:", len(sections))

    for index, section in enumerate(sections, start=1):
        print(
            f"Section {index}: {len(section)} characters"
        )

    return sections


# =========================================================
# 10. GENERATE A SUMMARY FOR THE WHOLE LECTURE
# =========================================================

def generate_summary(markdown_path):
    """
    Generate detailed notes for every section of the lecture.

    Each section is processed separately, then the results are combined.
    """
    content = read_document_content(markdown_path)
    sections = split_document_content(content)

    summaries = []

    print("\n" + "=" * 50)
    print("GENERATING FULL LECTURE SUMMARY")
    print("=" * 50)

    for index, section in enumerate(sections, start=1):
        print(
            f"\nSummarizing section {index}/{len(sections)}..."
        )

        try:
            section_summary = summary_chain.invoke(
                {"context": section}
            ).strip()

            print(
                f"Section {index} summary length: "
                f"{len(section_summary)} characters"
            )

            if not section_summary:
                raise ValueError(
                    f"The model returned an empty summary for section {index}."
                )

            summaries.append(
                f"## Part {index}\n\n{section_summary}"
            )

        except Exception as exc:
            print(
                f"SUMMARY ERROR in section {index}: {exc}"
            )
            raise

    final_summary = "\n\n".join(summaries).strip()

    if len(final_summary) < 50:
        raise ValueError(
            "The generated summary is unexpectedly short. "
            "Please check the LLM response and configuration."
        )

    print("\n" + "=" * 50)
    print("SUMMARY GENERATION COMPLETED")
    print("Sections processed:", len(sections))
    print("Final summary length:", len(final_summary))
    print("=" * 50)

    return final_summary


# =========================================================
# 11. GENERATE STUDY QUESTIONS FOR THE WHOLE LECTURE
# =========================================================

def generate_questions(markdown_path, summary=None):
    """
    Generate questions and answers from every section of the lecture.

    The optional summary argument is retained for compatibility with
    any existing code that might pass it.
    """
    content = read_document_content(markdown_path)
    sections = split_document_content(content)

    all_questions = []

    print("\n" + "=" * 50)
    print("GENERATING QUESTIONS FOR THE FULL LECTURE")
    print("=" * 50)

    for index, section in enumerate(sections, start=1):
        print(
            f"\nGenerating questions for section "
            f"{index}/{len(sections)}..."
        )

        try:
            section_questions = questions_chain.invoke(
                {"context": section}
            ).strip()

            print(
                f"Section {index} questions length: "
                f"{len(section_questions)} characters"
            )

            if not section_questions:
                raise ValueError(
                    f"The model returned no questions for section {index}."
                )

            all_questions.append(
                f"# Questions from Part {index}\n\n{section_questions}"
            )

        except Exception as exc:
            print(
                f"QUESTIONS ERROR in section {index}: {exc}"
            )
            raise

    final_questions = "\n\n".join(all_questions).strip()

    if not final_questions:
        raise ValueError(
            "No study questions were generated from the lecture."
        )

    print("\n" + "=" * 50)
    print("QUESTION GENERATION COMPLETED")
    print("Sections processed:", len(sections))
    print("Final questions length:", len(final_questions))
    print("=" * 50)

    return final_questions
