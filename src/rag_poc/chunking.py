from rag_poc.config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text, max_size, overlap):
    if len(text) <= max_size:
        return [text]

    chunks = []
    position = 0

    while position < len(text):
        chunk_end = min(position + max_size, len(text))
        chunk = text[position:chunk_end]
        chunks.append(chunk)

        if chunk_end == len(text):
            break

        position = chunk_end - overlap

    return chunks

def create_chunks(documents):
    all_chunks = []
    current_buffer = ""
    buffer_file = ""
    buffer_location = ""

    for doc in documents:
        new_text = doc["text"]
        new_file = doc["file"]
        new_location = doc["location"]

        if current_buffer:
            combined = current_buffer + "\n" + new_text
        else:
            combined = new_text

        same_source = (buffer_file == new_file and buffer_location == new_location)

        if len(combined) <= CHUNK_SIZE and (not current_buffer or same_source):
            current_buffer = combined
            buffer_file = new_file
            buffer_location = new_location
        else:
            if current_buffer:
                text_pieces = chunk_text(current_buffer, CHUNK_SIZE, CHUNK_OVERLAP)
                for piece in text_pieces:
                    chunk_dict = {
                        "text": piece,
                        "file": buffer_file,
                        "location": buffer_location
                    }
                    all_chunks.append(chunk_dict)

            current_buffer = new_text
            buffer_file = new_file
            buffer_location = new_location

    if current_buffer:
        text_pieces = chunk_text(current_buffer, CHUNK_SIZE, CHUNK_OVERLAP)
        for piece in text_pieces:
            chunk_dict = {
                "text": piece,
                "file": buffer_file,
                "location": buffer_location
            }
            all_chunks.append(chunk_dict)

    return all_chunks
