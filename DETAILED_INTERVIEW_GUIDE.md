# RAG POC - Detailed Interview Preparation Guide
## With Libraries, Tools, Models, and Answered Questions

---

# SECTION 1: LIBRARIES & DEPENDENCIES

## 1.1 FAISS (faiss-cpu >= 1.15.0)

### What is FAISS?
Facebook AI Similarity Search - A library for efficient similarity search and clustering of dense vectors. In your POC, it stores embeddings (vector representations) and quickly retrieves the most similar chunks for a given query.

### Why did you choose FAISS?
- **Lightweight & CPU-only**: Doesn't require GPU (faiss-cpu); perfect for POCs and small deployments
- **No external service needed**: Unlike Pinecone, everything runs locally - full data control
- **Fast similarity search**: IndexFlatIP computes inner product (cosine similarity) in milliseconds
- **Persistence**: Easy to save/load index from disk (one file = index.faiss)
- **Cost-effective**: Zero infrastructure costs, no API bills for storage
- **Proven**: Used at scale by Meta; battle-tested algorithm

### How does it solve your problem?
```python
# Your use case: User asks "What products are available?"
# System needs to find matching document chunks from thousands

self.index = faiss.IndexFlatIP(dimension)  # dimension=768 (embedding size)
self.index.add(embeddings)                  # Add all document embeddings

# Later when user asks:
scores, indices = self.index.search(query_embedding, k=4)
# Returns: Top-4 most similar chunks (score: 0.0-1.0 similarity)
```

### Implementation Details in Your Code:
- **Location**: `src/rag_poc/vectorstore.py`
- **Index type**: `IndexFlatIP` (Inner Product = Cosine Similarity for normalized vectors)
- **Storage**: Saves to `storage/index.faiss` + metadata in JSON
- **Search complexity**: O(n) - linear search through all vectors (acceptable for <100K docs)

### Related Questions & Answers:

**Q1: What are FAISS limitations at scale (>1M vectors)?**
**A:** 
- **Memory usage**: IndexFlatIP stores all vectors in RAM. 1M vectors × 768 dims × 4 bytes = ~3GB RAM
- **Search speed**: Linear scan becomes slow (milliseconds → seconds) for very large scales
- **No distributed**: All on single machine (no sharding across servers)
- **Solution for scale**: Migrate to Pinecone/Weaviate (cloud-managed), or use IndexIVFFlat (approximation, faster)

**Q2: When would you migrate from FAISS to Pinecone/Weaviate?**
**A:**
- **Pinecone when**: >10M vectors, need hybrid search, serverless operations, managed backups
- **Weaviate when**: Need GraphQL interface, more control, multi-tenancy, complex filters
- **Trigger**: Query latency > 500ms OR RAM costs exceed Pinecone/Weaviate costs
- **Timeline in your project**: After proving POC works, before production (Month 3-6)

**Q3: IndexFlatIP vs IndexIVFFlat differences?**
**A:**
| Feature | IndexFlatIP | IndexIVFFlat |
|---------|---|---|
| Accuracy | 100% (exact) | 98-99% (approximate) |
| Speed | O(n) slow | O(log n) fast |
| Memory | Full storage | Reduced (~80%) |
| Use case | <100K vectors | >1M vectors |
| Your POC | ✓ Using this | Not needed yet |

---

## 1.2 Google Generative AI (google-generativeai >= 0.8.6)

### What is it?
Official Python SDK for Google Gemini API. Provides easy access to:
- Embedding models (convert text → vectors)
- Chat models (generate answers from context)

### Why choose Google Generative AI?
- **Free tier**: 60 requests/minute without billing for POC development
- **Unified access**: Single library for embeddings + chat (no juggling multiple SDKs)
- **Latest models**: Access to Gemini models (better quality than older alternatives)
- **Simple integration**: One-liner to call: `genai.embed_content()`, `model.generate_content()`
- **No infrastructure**: No need to host/manage models locally

### How it's used in your code:

**For embeddings:**
```python
# src/rag_poc/embeddings.py
result = genai.embed_content(
    model="models/gemini-embedding-001",
    content=text_list,
    task_type="retrieval_document"  # Optimized for document embedding
)
```

**For chat:**
```python
# src/rag_poc/rag.py
model = genai.GenerativeModel(CHAT_MODEL)  # "models/gemini-3.6-flash"
response = model.generate_content(prompt)
```

### Related Questions & Answers:

**Q: Why not use OpenAI embeddings instead?**
**A:**
| Factor | OpenAI | Google Gemini |
|--------|--------|---|
| Embedding cost | $0.02 per 1M tokens | Free (up to limits) |
| Embedding quality | text-embedding-3-small (1536 dims) | gemini-embedding-001 (768 dims) |
| Chat cost | $0.50/$1.50 per 1M tokens | Free tier available |
| Latency | Low (~200ms) | Similar (~200ms) |
| Your choice | No (cost for POC) | ✓ Yes (free tier) |

**Q: What if Gemini API goes down?**
**A:**
- **Risk**: System completely stops (no fallback in current code)
- **Solution for production**: Implement circuit breaker pattern
```python
def get_embedding_with_fallback(text):
    try:
        return gemini_embed(text)  # Primary
    except Exception:
        return openai_embed(text)  # Fallback (requires key)
```

---

## 1.3 NumPy (numpy >= 2.5.2)

### What is it?
Numerical Python library for array/matrix operations. Used for mathematical calculations on embeddings.

### Why include it?
FAISS and embeddings return numpy arrays; you need NumPy for:
- Vector normalization (divide by magnitude)
- Array reshaping
- Distance calculations

### How it's used:
```python
# src/rag_poc/embeddings.py
embeddings_array = np.array(embeddings, dtype=np.float32)

# Normalize vectors for cosine similarity
norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
normalized = embeddings_array / norms  # Element-wise division
```

---

## 1.4 Streamlit (streamlit >= 1.62.0)

### What is it?
Python framework for building interactive web apps with minimal frontend code.

### Why Streamlit for RAG?
- **Rapid prototyping**: Go from code → web UI in <10 lines
- **Built-in components**: `st.chat_message()`, `st.file_uploader()`, `st.expander()` (all you need for RAG)
- **Hot reload**: Code changes = instant UI update (great for iteration)
- **No frontend skills needed**: Pure Python, not JavaScript
- **Deploy easily**: Streamlit Cloud, Docker, or local server

### How it's used:
```python
# src/rag_poc/app.py
st.title("RAG Demo - Ask Your Documents")

with st.sidebar:
    excel_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if st.button("Build Index"):
        # ... indexing logic

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.write(message["text"])

user_input = st.chat_input("Ask a question about your documents")
```

### Trade-offs:
| Pros | Cons |
|------|------|
| Fast to build | Limited customization (can't build complex UIs) |
| Easy to deploy | Reloads entire script on interaction (not efficient) |
| Great for demos | Not suitable for high-load production |

### Related Questions & Answers:

**Q: Why not use React/Vue for the frontend?**
**A:** For a POC:
- React = 100+ lines of code minimum; requires Node.js, build tools, API endpoints
- Streamlit = 30 lines, everything in one file, instant prototype
- **When to switch to React**: If you need custom styling, real-time collaboration, mobile app

---

## 1.5 OpenPyXL (openpyxl >= 3.1.5)

### What is it?
Library for reading/writing Excel (.xlsx) files in Python.

### Why needed?
Your system supports Excel file uploads. OpenPyXL extracts text from:
- Cell values
- Formulas
- Sheet names

### How it's used:
```python
# src/rag_poc/loaders.py
from openpyxl import load_workbook

wb = load_workbook(excel_file)
for ws in wb.worksheets:
    for row in ws.iter_rows(values_only=True):
        # Extract cell values
        text += str(cell_value)
```

---

## 1.6 Python-docx (python-docx >= 1.2.0)

### What is it?
Library for reading/writing Word documents (.docx).

### Why needed?
Your system supports Word file uploads. python-docx extracts:
- Paragraph text
- Table content
- Headings
- Lists

### How it's used:
```python
# src/rag_poc/loaders.py
from docx import Document

doc = Document(word_file)
for para in doc.paragraphs:
    text += para.text
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            text += cell.text
```

---

## 1.7 Python-dotenv (python-dotenv >= 1.2.3)

### What is it?
Loads environment variables from `.env` file into Python.

### Why needed?
Your system needs API keys (GEMINI_API_KEY) but shouldn't hardcode them.

### How it's used:
```python
# src/rag_poc/config.py
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

### Security benefit:
- `.env` file in `.gitignore` → keys never committed to GitHub
- Different keys for dev/prod environments

---

# SECTION 2: TOOLS USED

## 2.1 FAISS (Already Covered Above - Also a Tool)

## 2.2 Streamlit (Already Covered Above - Also a Tool)

## 2.3 Google Gemini API (Tool Interface)

### What does the Gemini tool solve?
- **Embedding problem**: Convert text → vector (semantic meaning)
- **Chat problem**: Answer questions grounded in documents

### How you access it:
- **Not a local tool**: Cloud-based API call
- **Your code**: Uses google-generativeai SDK as intermediary

### Gemini capabilities you're using:
```
1. Embeddings (gemini-embedding-001)
   - Input: Text string or list of texts
   - Output: Vector [768 dimensions]
   
2. Chat (gemini-3.6-flash)
   - Input: Prompt with context + question
   - Output: Answer text
```

### Cost consideration:
- **Embedding**: Free tier = 60 req/min, ~$0.0001 per 1K tokens
- **Chat**: Free tier available, then ~$0.075 per 1M input tokens

---

## 2.4 UV Package Manager

### What is UV?
Modern Python package manager (alternative to pip/pipenv). Extremely fast.

### Why used?
- **Speed**: 10x faster than pip (you probably notice `uv sync` is instant)
- **Lock file**: `uv.lock` = reproducible installs across machines
- **Simplicity**: Single command: `uv sync`, `uv run`

### How you use it:
```bash
uv sync              # Install dependencies from pyproject.toml
uv run streamlit run src/rag_poc/app.py  # Run Python with deps
```

---

# SECTION 3: MODELS USED

## 3.1 Gemini Embedding 001

### What is it?
Google's embedding model. Converts text into 768-dimensional vectors.

### Why this model?
- **Free tier**: No cost for POC development
- **Quality**: Performs well on document retrieval tasks
- **Speed**: <200ms per request
- **Dimension**: 768 dims = good balance (not too big like OpenAI's 1536)

### How embeddings work in your system:
```
User document: "The return policy is 30 days."
         ↓ (gemini-embedding-001)
Vector: [0.12, -0.45, 0.67, ..., 0.23]  (768 numbers)
         ↓ (stored in FAISS)
Later when user asks: "Can I return items?"
         ↓ (gemini-embedding-001)
Vector: [0.11, -0.44, 0.65, ..., 0.24]  (similar vector)
         ↓ (FAISS finds closest match)
Retrieved: "The return policy is 30 days."
```

### Key feature you're using:
```python
task_type="retrieval_document"  # Tells model to optimize for document embedding
task_type="retrieval_query"     # Tells model to optimize for query embedding
```

This is important! Query embeddings have different tuning than document embeddings.

### Related Questions & Answers:

**Q: Why 768 dimensions instead of OpenAI's 1536?**
**A:**
- **Storage**: 768 dims = ~3KB per vector vs 1536 = ~6KB (half the memory)
- **Speed**: Faster similarity search with smaller vectors
- **Quality trade-off**: Slightly lower quality (~2-3% worse), but good enough for document retrieval
- **Cost**: Smaller size = faster processing

**Q: What if you need better embedding quality?**
**A:**
Options in priority order:
1. **Switch to E5-Large** (~1024 dims, open-source, free): Better quality, small vector
2. **Switch to OpenAI text-embedding-3-large** (3072 dims): Best quality, more expensive
3. **Fine-tune embedding model** on your domain data: Best for specialized use case

---

## 3.2 Gemini 3.6 Flash (Chat Model)

### What is it?
Google's lightweight chat model. Generates answers to user questions.

### Why this model?
- **Fast**: "Flash" = optimized for speed (milliseconds response)
- **Cheap**: Free tier available + lowest cost among capable models
- **Quality**: Good enough for document Q&A (not as good as Opus, but sufficient)
- **New**: Latest Gemini model (3.6 version)

### How you use it:
```python
model = genai.GenerativeModel("models/gemini-3.6-flash")
response = model.generate_content("""
Answer using ONLY the context below.
If you don't know, say "I don't know".

Context:
[Retrieved document chunks here]

Question: What is the return policy?

Answer:
""")
```

### Why constrain the prompt?
Your system adds:
- **"Answer using ONLY the context"** → Prevents hallucination
- **"If you don't know, say I don't know"** → Handles out-of-domain questions
- **Append context + question** → Grounds answer in documents

### Related Questions & Answers:

**Q: Why not use Gemini Pro or Opus?**
**A:**
| Model | Speed | Quality | Cost | Your choice |
|-------|-------|---------|------|---|
| Nano | Fastest | Lowest | Free | No (too basic) |
| Flash | Fast | Good | Free | ✓ Yes (perfect balance) |
| Pro | Medium | Better | $1.50/M tokens | No (overkill for POC) |
| Opus | Slow | Best | $15/M tokens | No (expensive) |

**Q: How would you reduce API costs?**
**A:**
1. **Caching**: Store answers for identical questions (don't call API twice)
   ```python
   cache = {"What products...": "Laptops, keyboards..."}
   if question in cache:
       return cache[question]  # Instant, $0 cost
   ```
2. **Batch processing**: Embed 10 documents together instead of 1-by-1 (bulk discount)
3. **Switch models**: Use smaller model (Nano) for simple Q&A
4. **Rate limiting**: Limit user queries per minute to prevent runaway costs

---

# SECTION 4: ARCHITECTURE DECISIONS

## 4.1 Why Separate Embedding Provider (Potential)

### Current setup in your code:
```python
# config.py - Currently ONLY uses Gemini
EMBEDDING_MODEL = "models/gemini-embedding-001"
CHAT_MODEL = "models/gemini-3.6-flash"
```

### But README mentions flexibility:
```text
To use Gemini for embeddings instead, set EMBEDDING_PROVIDER=gemini.
(Implies OpenAI is default)
```

### Why separate them?
**Reason**: Different models excel at different tasks:
- **Embedding model**: Optimized for semantic similarity
- **Chat model**: Optimized for generation/creativity

### You could switch:
```python
if EMBEDDING_PROVIDER == "openai":
    embeddings = openai.Embedding.create(...)  # Better embeddings
else:
    embeddings = gemini.embed_content(...)     # Faster/cheaper

# Always use best chat model
answer = gemini.chat(context + question)  # Best answer generation
```

---

## 4.2 Chunking Strategy Deep Dive

### Your configuration:
```python
CHUNK_SIZE = 800           # Characters per chunk
CHUNK_OVERLAP = 150        # Character overlap between chunks
```

### Why these specific numbers?

**800 characters:**
- ≈ 150-200 words
- ≈ 250-300 tokens (Gemini embedding limit is higher, but 768 dims optimal around this size)
- Fits nicely in a chat message without overwhelming LLM

**150 character overlap:**
- ≈ 25-30 words
- Ensures sentences spanning chunk boundary aren't lost
- Acceptable redundancy (~19% extra storage)

### Visual example:
```
Document: "The product warranty is 1 year. All defects covered. 
            Return within 30 days. No questions asked. Free return 
            shipping on defects."

Chunk 1 (0-800):
"The product warranty is 1 year. All defects covered. 
 Return within 30 days. No questions asked. Free return 
 shipping on defects. [continues to 800 chars]"
      
Chunk 2 (650-1450):  [overlaps with chunk 1 by 150 chars]
"[...shipping on defects. ...continues for 800 chars]"
```

### Related Questions & Answers:

**Q: Should chunk size be adaptive (paragraph-aware)?**
**A:**
| Approach | Pros | Cons | Your POC |
|----------|------|------|---------|
| Fixed size (800 chars) | Simple, consistent | May split paragraphs | ✓ Using |
| Paragraph-aware | Preserves semantics | Variable chunk quality | Future work |
| Hierarchical | Chunks + summaries | Complex code | Production only |

**Your answer**: "For POC, fixed size works well. For production, I'd implement paragraph detection: if paragraph < 800 chars, include full paragraph; if > 800, then split."

---

## 4.3 Conversation History Implementation

### Your code:
```python
def build_conversation_context(chat_history):
    context = "Previous conversation:\n"
    for msg in chat_history[-3:]:  # Last 3 messages only
        role = "USER" if msg["role"] == "user" else "ASSISTANT"
        context += f"{role}: {msg['text']}\n"
    return context
```

### Why last 3 messages?

| Num messages | Prompt size | Quality | Cost |
|---|---|---|---|
| 0 (none) | Small | No context | Low |
| 3 | Medium | Good context | Medium |
| 10 | Large | Better context | High |

**3 is optimal** because:
- Captures immediate context (last user question + 1-2 prior exchanges)
- Doesn't blow up prompt size
- Keeps API costs manageable

### Example use case where it helps:
```
User 1: "What products do you have?"
Assistant: "Laptops, keyboards, mice..."

User 2: "Tell me more about them"  ← "them" = ambiguous without history
Without history: "I don't know what you mean"
With history: "Here are details about laptops, keyboards, mice..."
```

---

# SECTION 5: IMPLEMENTATION DEEP DIVE

## 5.1 Full Pipeline Explained

### Step 1: Document Upload
```python
# app.py
excel_file = st.file_uploader("Upload Excel file", type=["xlsx"])
word_file = st.file_uploader("Upload Word file", type=["docx"])
```
**What**: User uploads files via browser
**Output**: BytesIO objects (files in memory)

### Step 2: Text Extraction
```python
# loaders.py - extract_text_from_excel(), extract_text_from_word()
documents = load_files(excel_data, word_data)
```
**What**: Parse Excel/Word → extract raw text
**Output**: List of strings ["Product: Laptop...", "Warranty: 1 year..."]
**Example**: 100KB file → 50,000 characters of text

### Step 3: Chunking
```python
# chunking.py - create_chunks()
chunks = create_chunks(documents)  # Size 800, overlap 150
```
**What**: Split text into overlapping pieces
**Output**: 
```python
[
    {"text": "...[800 chars]...", "file": "products.xlsx", "location": "Sheet 1, Row 5"},
    {"text": "...[800 chars]...", "file": "products.xlsx", "location": "Sheet 1, Row 7"},
    ...  # ~50 chunks for average document
]
```

### Step 4: Embedding
```python
# vectorstore.py - build_index()
embeddings = get_text_embeddings(text_list)
```
**What**: Convert each chunk to vector using Gemini
**API calls**: 50 chunks = 50 API calls (or batch as 1 call)
**Output**: 
```python
[
    [0.12, -0.45, 0.67, ..., 0.23],  # 768 dimensions
    [0.11, -0.44, 0.65, ..., 0.24],
    ...
]  # Shape: (50, 768)
```

### Step 5: Index Building
```python
# vectorstore.py
self.index = faiss.IndexFlatIP(768)
self.index.add(embeddings)  # Add all 50 normalized vectors
```
**What**: Create searchable index from vectors
**Storage**: ~50 vectors × 768 dims × 4 bytes = 150 KB

### Step 6: Save to Disk
```python
# vectorstore.py
faiss.write_index(self.index, "storage/index.faiss")  # Save FAISS index
metadata_json.write_text(json.dumps(metadata))        # Save metadata
```

### Step 7: User Query
```python
# app.py
user_input = st.chat_input("Ask a question...")
```
**Input**: "What products do you have?"

### Step 8: Query Embedding
```python
# embeddings.py - get_query_embedding()
query_embedding = genai.embed_content(
    model="models/gemini-embedding-001",
    content="What products do you have?",
    task_type="retrieval_query"  # Note: "query" not "document"
)
```
**Output**: [0.13, -0.43, 0.68, ..., 0.22]  # Same 768 dimensions

### Step 9: Vector Search
```python
# vectorstore.py - search()
scores, indices = self.index.search(query_embedding.reshape(1, -1), k=4)
# scores: [0.89, 0.76, 0.65, 0.54]
# indices: [5, 12, 23, 45]  (which chunks matched)
```
**What**: Find top-4 most similar chunks
**Output**: 4 chunks + relevance scores

### Step 10: Context Building
```python
# rag.py - ask_question()
context = ""
for i, result in enumerate(search_results, start=1):
    context += f"[{i}] From {result['file']} ({result['location']}):\n"
    context += result["text"]
    context += "\n\n"
```
**Output**:
```
[1] From products.xlsx (Sheet 1, Row 5):
We offer laptops, keyboards, mice...

[2] From policies.docx (Paragraph 2):
Products come with 1-year warranty...

[3] ...
[4] ...
```

### Step 11: Prompt Construction
```python
# rag.py
prompt = f"""{conversation_context}Answer the question using ONLY the context below.
If you don't know the answer, say "I don't know".

Context:
{context}

Question: What products do you have?

Answer:"""
```

### Step 12: LLM Response
```python
# rag.py
model = genai.GenerativeModel(CHAT_MODEL)
response = model.generate_content(prompt)
answer = response.text
```
**Output**: "Based on the provided context, we offer laptops, keyboards, and mice..."

### Step 13: Display Results
```python
# app.py
st.write(result["answer"])
with st.expander("Sources"):
    for source in result["sources"]:
        st.write(f"**{source['file']}** - {source['location']}")
        st.write(f"Score: {source['score']:.3f}")
        st.write(source["text"][:200] + "...")
```

---

# SECTION 6: PERFORMANCE CHARACTERISTICS

## 6.1 Latency Breakdown

For a typical query "What products do you have?":

```
Component                    Time        Notes
───────────────────────────────────────────────────────────
Query embedding              ~200ms      Gemini API call
FAISS search (50 chunks)     ~1ms        O(n) linear scan
LLM response generation      ~500ms      Gemini chat API
─────────────────────────────────────────────────────────
TOTAL                        ~700ms      User perceives 0.7 sec
```

## 6.2 Cost Breakdown

For 1000 queries on 50 documents:

```
Operation              Calls    Cost (approx)    Notes
──────────────────────────────────────────────────────────
Initial embedding      50       $0              Free tier
Query embeddings       1000     $0              Free tier
LLM responses          1000     ~$0.075         ~$0.075 total
──────────────────────────────────────────────────────────
TOTAL                                $0.075   Extremely cheap!
```

---

# SECTION 7: POTENTIAL INTERVIEW SCENARIOS

## Scenario 1: Scale Problem
**Interviewer**: "We need to handle 1 million documents. Current system takes 30 seconds per query."

**Your analysis**:
- Current: FAISS Linear search on 50K vectors = O(n) = fast
- At scale: 1M vectors = still O(n) but 20x slower
- Bottleneck: FAISS, not embeddings/LLM
- Solution: Switch FAISS to IndexIVFFlat (approximate, 100x faster) OR migrate to Pinecone

**Your proposal**:
1. Phase 1: Add caching (identical queries return instant)
2. Phase 2: Implement batch embeddings (embed 100 at once)
3. Phase 3: Migrate to Pinecone for production load

---

## Scenario 2: Hallucination Problem
**Interviewer**: "User asked about product 'XYZ' but product doesn't exist. System made up details."

**Your analysis**:
- Gemini is too creative (temperature too high)
- Retrieved sources irrelevant (low similarity score threshold)
- Prompt doesn't constrain well

**Your fix**:
```python
# Option 1: Stricter prompt
prompt = f"""You must answer using ONLY the exact text from context.
Do NOT add any information not in the provided text.
If information is not provided, respond: "I don't have this information in my documents."

Context:
{context}

Question: {question}
Answer:"""

# Option 2: Filter by confidence
def answer_question(...):
    results = vector_store.search(question)
    if results[0]['score'] < 0.7:  # Low confidence
        return {"answer": "Not found in documents", "sources": []}
    # ... continue with high-confidence results
```

---

## Scenario 3: Cost Explosion
**Interviewer**: "Suddenly our monthly API bill is $5,000 (was $50). What happened?"

**Your investigation checklist**:
1. ✓ Check logs: Which API was called most? (embedding vs chat)
2. ✓ Check metrics: Queries per second (was 10/sec, now 1000/sec)
3. ✓ Check code: Is caching working? Any infinite loops?
4. ✓ Check users: Did a new power-user start using extensively?

**Your fixes**:
```python
# 1. Add request logging
import logging
logging.info(f"Embedding API call: {len(texts)} texts")

# 2. Add rate limiting per user
from collections import defaultdict
user_calls = defaultdict(lambda: deque(maxlen=60))  # Last 60 seconds

def rate_limit_check(user_id):
    now = time.time()
    user_calls[user_id].append(now)
    if len(user_calls[user_id]) > 60:  # 60 calls per minute max
        return False
    return True

# 3. Add caching
@cache
def get_embedding(text):
    return gemini_api_call(text)
```

---

# SECTION 8: INTERVIEW CHEAT SHEET

## Quick Answers to Common Questions:

**"Why FAISS?"**
> Lightweight, no external service, fast enough for POCs (<100K docs), easy persistence.

**"Why Gemini?"**
> Free tier, unified API for both embeddings and chat, latest model quality.

**"Why Streamlit?"**
> Rapid prototyping in Python, no frontend skills needed, quick to demo.

**"Why 800 chars chunks?"**
> ~200 words, fits LLM context window efficiently, ~19% overlap prevents information loss.

**"How does it scale?"**
> FAISS works to ~100K docs. Beyond that, need Pinecone/Weaviate + distributed architecture.

**"How do you prevent hallucination?"**
> Strict prompt ("ONLY use context"), confidence thresholding (score > 0.7), fact-checking against sources.

**"What's your main limitation?"**
> Single-user/single-machine, no real-time updates, fixed chunk size, limited file formats.

**"How would you productionize this?"**
> Add authentication, implement caching, migrate to Pinecone, setup monitoring/alerts, add user feedback loop.

---

# SECTION 9: BEFORE YOUR INTERVIEW

**24 hours before:**
- [ ] Re-read this guide (focus on your project's actual choices)
- [ ] Run your app locally, ask yourself questions
- [ ] Prepare 2-3 "war stories" about debugging/improvements

**Day of interview:**
- [ ] Mention specific numbers (768 dims, 800 chars, top-4 results, $0.075 for 1000 queries)
- [ ] Reference your actual code files (shows you know it well)
- [ ] Give trade-off answers (not just "this is good")
- [ ] Ask clarifying questions (don't assume requirements)

**Example answer structure:**
> "We chose [X] because [specific reason]. For our POC with [constraints], it works great. If we scale to [larger scale], we'd need [different solution] because [technical reason]. We measure success with [metric]."

Good luck! 🚀
