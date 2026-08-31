import streamlit as st
from io import BytesIO
from rag_poc.config import create_storage_folder
from rag_poc.loaders import load_files
from rag_poc.chunking import create_chunks
from rag_poc.vectorstore import VectorStore
from rag_poc.rag import answer_question

st.set_page_config(page_title="RAG Demo", layout="wide")

create_storage_folder()

if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "index_ready" not in st.session_state:
    st.session_state.index_ready = False

if "error_message" not in st.session_state:
    st.session_state.error_message = None

store = st.session_state.vector_store

if not st.session_state.index_ready:
    if store.load_index():
        st.session_state.index_ready = True

st.title("RAG Demo - Ask Your Documents")

with st.sidebar:
    st.header("Upload Files")

    excel_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    word_file = st.file_uploader("Upload Word file", type=["docx"])

    if st.button("Build Index"):
        if not excel_file and not word_file:
            st.error("Please upload at least one file")
        else:
            try:
                excel_data = None
                word_data = None

                if excel_file:
                    excel_bytes = BytesIO(excel_file.getvalue())
                    excel_data = excel_bytes

                if word_file:
                    word_bytes = BytesIO(word_file.getvalue())
                    word_data = word_bytes

                documents = load_files(excel_data, word_data)

                chunks = create_chunks(documents)

                new_store = VectorStore()
                new_store.build_index(chunks)

                st.session_state.vector_store = new_store
                st.session_state.index_ready = True
                st.session_state.chat_messages = []
                st.session_state.error_message = None

                st.success(f"Index built! {len(chunks)} chunks created")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.session_state.index_ready:
        chunk_count = len(st.session_state.vector_store.metadata)
        st.info(f"✓ Index ready with {chunk_count} chunks")
    else:
        st.warning("Index not ready - upload files and build index")

if st.session_state.error_message:
    st.error(st.session_state.error_message)

if not st.session_state.index_ready:
    st.info("Upload files in the sidebar and click 'Build Index' to start")
else:
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["text"])
        else:
            with st.chat_message("assistant"):
                st.write(message["text"])
                if message.get("sources"):
                    with st.expander("Sources"):
                        for source in message["sources"]:
                            st.write(f"**{source['file']}** - {source['location']}")
                            st.write(f"Score: {source['score']:.3f}")
                            st.write(source["text"][:200] + "...")

    user_input = st.chat_input("Ask a question about your documents")

    if user_input:
        st.session_state.chat_messages.append({"role": "user", "text": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching and answering..."):
                result = answer_question(
                    user_input,
                    st.session_state.vector_store,
                    chat_history=st.session_state.chat_messages[:-1]
                )

            st.write(result["answer"])

            with st.expander("Sources"):
                for source in result["sources"]:
                    st.write(f"**{source['file']}** - {source['location']}")
                    st.write(f"Score: {source['score']:.3f}")
                    st.write(source["text"][:200] + "...")

            st.session_state.chat_messages.append({
                "role": "assistant",
                "text": result["answer"],
                "sources": result["sources"]
            })
