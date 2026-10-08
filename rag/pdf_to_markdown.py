import pymupdf
import os


def pdf_to_markdown(pdf_path):
    """
    Convert a PDF file into a Markdown file.
    """

    # Open PDF
    pdf = pymupdf.open(pdf_path)

    markdown_content = []

    # Read every page
    for page_number, page in enumerate(pdf, start=1):

        text = page.get_text("text").strip()

        if text:
            markdown_content.append(f"## Page {page_number}\n")
            markdown_content.append(text)
            markdown_content.append("\n")

    pdf.close()

    # Create Markdown path
    markdown_path = os.path.splitext(pdf_path)[0] + ".md"

    # Save Markdown
    with open(markdown_path, "w", encoding="utf-8") as file:
        file.write("\n".join(markdown_content))

    return markdown_path