import google.generativeai as genai
from rag_poc.config import GEMINI_API_KEY, CHAT_MODEL

genai.configure(api_key=GEMINI_API_KEY)

def ask_question(question, search_results):
    context = ""

    for i, result in enumerate(search_results, start=1):
        context += f"[{i}] From {result['file']} ({result['location']}):\n"
        context += result["text"]
        context += "\n\n"

    prompt = f"""Answer the question using ONLY the context below.
If you don't know the answer, say "I don't know".

Context:
{context}

Question: {question}

Answer:"""

    model = genai.GenerativeModel(CHAT_MODEL)
    response = model.generate_content(prompt)

    answer = response.text if response.text else "No answer"

    return answer

def answer_question(question, vector_store):
    if not question.strip():
        raise ValueError("Question is empty")

    search_results = vector_store.search(question)

    if not search_results:
        return "No relevant documents found"

    answer = ask_question(question, search_results)

    return {
        "answer": answer,
        "sources": search_results
    }
