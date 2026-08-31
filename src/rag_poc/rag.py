import google.generativeai as genai
from rag_poc.config import GEMINI_API_KEY, CHAT_MODEL

genai.configure(api_key=GEMINI_API_KEY)

def is_casual_input(text):
    """Check if input is casual greeting/thanks"""
    casual_words = ["hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye", "ok", "okay"]
    text_lower = text.lower().strip()
    return any(word in text_lower for word in casual_words)

def get_casual_response(text):
    """Return casual response for casual inputs"""
    text_lower = text.lower().strip()

    if any(word in text_lower for word in ["hi", "hello", "hey"]):
        return "Hi! I'm here to help. Ask me about your documents."
    if any(word in text_lower for word in ["thanks", "thank you"]):
        return "You're welcome! Feel free to ask more questions."
    if any(word in text_lower for word in ["bye", "goodbye"]):
        return "Goodbye! Have a great day!"
    if any(word in text_lower for word in ["ok", "okay"]):
        return "Understood! What else would you like to know?"

    return None

def build_conversation_context(chat_history):
    """Build context from recent conversation history"""
    if not chat_history:
        return ""

    context = "Previous conversation:\n"
    # Use last 3 messages to keep prompt concise
    for msg in chat_history[-3:]:
        role = "USER" if msg["role"] == "user" else "ASSISTANT"
        context += f"{role}: {msg['text']}\n"

    return context + "\n"

def ask_question(question, search_results, chat_history=None):
    context = ""

    for i, result in enumerate(search_results, start=1):
        context += f"[{i}] From {result['file']} ({result['location']}):\n"
        context += result["text"]
        context += "\n\n"

    # Add conversation history if available
    conversation_context = build_conversation_context(chat_history)

    prompt = f"""{conversation_context}Answer the question using ONLY the context below.
If you don't know the answer, say "I don't know".

Context:
{context}

Question: {question}

Answer:"""

    model = genai.GenerativeModel(CHAT_MODEL)
    response = model.generate_content(prompt)

    answer = response.text if response.text else "No answer"

    return answer

def answer_question(question, vector_store, chat_history=None):
    if not question.strip():
        raise ValueError("Question is empty")

    # Check if it's a casual input first
    if is_casual_input(question):
        casual_response = get_casual_response(question)
        if casual_response:
            return {
                "answer": casual_response,
                "sources": []
            }

    search_results = vector_store.search(question)

    if not search_results:
        return {
            "answer": "No relevant documents found",
            "sources": []
        }

    answer = ask_question(question, search_results, chat_history)

    return {
        "answer": answer,
        "sources": search_results
    }
