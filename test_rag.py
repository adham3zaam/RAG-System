
from rag.chains import sequential_rag


question = " what the pdf summary ?"

result = sequential_rag(question)

print("\n==============================")
print("Original Question:")
print(result["original_question"])

print("\n==============================")
print("Rewritten Question:")
print(result["rewritten_question"])

print("\n==============================")
print("Answer:")
print(result["answer"])

print("\n==============================")
print("Sources:")
print(result["sources"])