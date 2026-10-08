from rag.chains import sequential_rag


question = "اهم معلم سياحي في مصر?"

result = sequential_rag(question)

print("\n" + "=" * 60)
print("ORIGINAL QUESTION")
print("=" * 60)

print(result["original_question"])


print("\n" + "=" * 60)
print("REWRITTEN QUESTION")
print("=" * 60)

print(result["rewritten_question"])


print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)

print(result["answer"])


print("\n" + "=" * 60)
print("SOURCE PAGES")
print("=" * 60)

print(result["sources"])