from rag.pdf_to_markdown import pdf_to_markdown

pdf_path = "data/documents/Horizon_Tours_Complete_Knowledge_Base_2025.pdf"

markdown_path = pdf_to_markdown(pdf_path)

print("Markdown created:")
print(markdown_path)