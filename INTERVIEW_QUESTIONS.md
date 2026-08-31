# RAG POC - Interview Preparation Questions

## TECHNICAL QUESTIONS

### 1. Why did you choose FAISS over other vector databases?
**What:** Selecting FAISS (Facebook AI Similarity Search) as the vector store
**Why:** 
- Lightweight & open-source (no external service needed)
- Excellent for small-to-medium datasets (~10K-1M vectors)
- Fast similarity search with IndexFlatIP (inner product/cosine)
- Easy to persist and reload from disk
**How:** FAISS normalizes vectors and computes similarity scores in O(n) time, which is acceptable for POCs
**Related Questions:**
- What are the limitations of FAISS at scale (>1M vectors)?
- When would you migrate from FAISS to Pinecone/Weaviate?
- How does IndexFlatIP differ from IndexIVFFlat?

---

### 2. How does your chunking strategy (800 chars with 150 char overlap) impact retrieval quality?
**What:** Text splitting with fixed window size and overlap
**Why:**
- 800 chars ≈ 200-250 words (fits most LLM context windows efficiently)
- 150 char overlap = ~37 words (maintains semantic continuity)
- Prevents losing information at chunk boundaries
**How:** If a sentence spans chunk boundary, overlap ensures both chunks have it
**Related Questions:**
- How would you adapt chunk size for different document types?
- What's the trade-off between overlap and storage/cost?
- Should chunk size be adaptive (e.g., paragraph-aware)?

---

### 3. Why normalize embeddings for cosine similarity?
**What:** Converting vectors to unit length before storing in FAISS
**Why:**
- Cosine similarity measures angle, not magnitude
- Normalized vectors make distance/similarity calculations consistent
- Prevents high-magnitude vectors from dominating results
**How:** `normalized_vector = vector / ||vector||` ensures magnitude = 1
**Related Questions:**
- When would L2 distance be better than cosine similarity?
- How does normalization affect retrieval ranking?
- What happens if you don't normalize?

---

### 4. How does your RAG handle false negatives (relevant docs not retrieved)?
**What:** Documents that should match user query but aren't in top-K results
**Why:**
- Semantic gap: query phrasing vs document wording
- Ambiguous questions with multiple valid interpretations
- Limited context in documents
**How:**
- Use query expansion (rephrase before embedding)
- Increase K (retrieve more results, then re-rank)
- Add metadata filters (file type, date, category)
- Implement hybrid search (BM25 + semantic)
**Related Questions:**
- What's the difference between top-4 and top-10 retrieval?
- How would you measure recall in your system?
- Should you implement query rewriting before embedding?

---

### 5. Why separate embedding provider from chat model?
**What:** Using Gemini for both embeddings and chat, but allowing OpenAI embeddings
**Why:**
- Embedding & chat models optimize for different tasks
- Flexibility to swap providers independently
- Cost optimization (cheaper embedding models exist)
- API redundancy (if one service down, can switch)
**How:** 
```python
if EMBEDDING_PROVIDER == "openai":
    embedding = OpenAIEmbedding()
else:
    embedding = GeminiEmbedding()
```
**Related Questions:**
- Why not use the same model for both?
- What's the performance difference between OpenAI and Gemini embeddings?
- How do you handle model drift when switching providers?

---

### 6. How do you handle casual inputs differently from document queries?
**What:** Detecting greetings ("Hi", "Thanks") vs actual questions
**Why:**
- Avoid wasting API calls on non-queries
- Provide faster, rule-based responses
- Better user experience (feels more natural)
**How:** 
```python
if is_casual_input(text):  # Check against predefined list
    return get_casual_response(text)  # No embedding/retrieval needed
else:
    return rag_pipeline(text)  # Full pipeline
```
**Related Questions:**
- Should casual detection be ML-based or rule-based?
- What edge cases does your casual detection miss?
- How would you expand casual detection (off-topic questions)?

---

### 7. What's the purpose of conversation history in your prompts?
**What:** Including last 3 messages in RAG context
**Why:**
- Enables follow-up questions ("Tell me more about that")
- Provides context for pronouns and references
- Makes system feel more conversational
**How:**
```python
context = "Previous conversation:\n"
for msg in chat_history[-3:]:
    context += f"{role}: {msg['text']}\n"
```
**Related Questions:**
- Why limit to last 3 messages instead of all?
- How does conversation history affect prompt length/cost?
- What if conversation becomes contradictory?

---

### 8. How would you debug a poor answer?
**What:** Tracing why system gave wrong/irrelevant answer
**Why:**
- Need to identify failure point (retrieval vs generation)
- Improve system iteratively
**How:**
1. Check retrieved sources (were they relevant?)
2. Check relevance scores (was confidence low?)
3. Check original embedding (was query misunderstood?)
4. Check prompt (was context clear to LLM?)
**Related Questions:**
- How would you log retrieval vs generation quality separately?
- Should you show low-confidence answers differently to users?
- How would you implement a feedback loop?

---

## BUSINESS QUESTIONS

### 9. What are the main use cases for this system?
**What:** Real-world applications where RAG adds value
**Why:**
- Justifies development cost/effort
- Guides feature prioritization
**Examples:**
- Internal knowledge base search
- Customer support automation
- Policy/procedure lookup
- Legal document discovery
- Product documentation Q&A
**Related Questions:**
- Which use case would generate most revenue?
- How does RAG beat traditional search?
- What industry would benefit most?

---

### 10. How would you price this as a SaaS product?
**What:** Monetization strategy
**Why:**
- Need to cover API costs (Gemini embeddings/chat)
- Sustain business
**Models:**
- Per-query pricing ($0.01-0.05 per query)
- Per-document pricing (storage/indexing)
- Monthly subscription (unlimited queries)
- Freemium (100 free queries/month)
**Related Questions:**
- What's your cost per query (API + infrastructure)?
- How does usage scale with pricing model?
- Should you have tiered plans (basic/pro/enterprise)?

---

### 11. What's the competitive advantage vs Google Search / ChatGPT?
**What:** Why would customers choose your system?
**Why:**
- Differentiate in market
- Justify higher costs
**Advantages:**
- Works on proprietary/internal documents
- Real-time answers without hallucination
- Control over data (privacy)
- Customizable to domain
- Lower latency (no web search)
**Related Questions:**
- How do you beat ChatGPT with internet access?
- What about competitors like Perplexity?
- How important is data privacy to your target market?

---

### 12. What's the time-to-value for a customer?
**What:** How quickly can customer get ROI?
**Why:**
- Affects sales pitch and adoption
**Timeline:**
- Day 1: Upload documents, build index (10 min)
- Day 1: Start asking questions (immediately)
- Week 1: Measure quality, adjust chunk size
- Month 1: Train team, integrate into workflow
**Related Questions:**
- What's the minimum viable dataset size?
- How long to train support team?
- When do customers see 10x productivity gains?

---

### 13. How would you handle enterprise customers wanting integration?
**What:** Connecting RAG to enterprise systems (Salesforce, SharePoint, etc.)
**Why:**
- Enterprise deals are high-value
- But require more engineering
**Approach:**
- API endpoints (REST/GraphQL)
- Webhooks for document updates
- SSO integration (OAuth/SAML)
- Custom data connectors
**Related Questions:**
- Should integration support be premium feature?
- How do you maintain security with third-party integrations?
- What SLAs would you offer?

---

## SITUATIONAL QUESTIONS

### 14. "Our RAG is giving hallucinated answers. What do you do?"
**What:** System inventing facts not in documents
**Why:** Gemini might add "plausible-sounding" details
**Root causes:**
- Prompt not constraining LLM enough ("Only use context provided")
- Retrieval failed (irrelevant sources)
- Query too ambiguous
**Solutions:**
- Tighten prompt ("Say 'I don't know' if answer not in context")
- Lower temperature (0.1-0.3 instead of 0.7)
- Add confidence threshold (only answer if score > 0.7)
- Implement fact-checking against sources
**Related Questions:**
- How would you measure hallucination rate?
- Should you filter LLM output against source text?
- When is some hallucination acceptable?

---

### 15. "Users uploaded a 1000-page PDF but chunking produced 10K chunks. System now slow."
**What:** Performance degradation from large dataset
**Why:**
- More chunks = more embeddings to search
- Embedding API calls expensive
**Solutions:**
- Implement batch processing (embed in parallel)
- Use hierarchical chunking (summarize sections first)
- Filter low-quality chunks before embedding
- Implement caching for repeated queries
**Related Questions:**
- Should you warn users before indexing large files?
- How would you implement incremental indexing?
- What's the maximum chunk count you'd handle?

---

### 16. "A competitor just launched with 10 languages but we only support English."
**What:** Language expansion requirement
**Why:**
- Market pressure
- Customer demand
**Approach:**
- Multilingual embeddings (e.g., Multilingual E5)
- Language detection on input
- Separate FAISS indexes per language (or single multilingual)
- Test cross-language retrieval (Spanish query on English docs)
**Related Questions:**
- Should you support code-switching (mixing languages)?
- How do you handle document translation?
- What's cost of multilingual vs English-only?

---

### 17. "A customer's confidential document was leaked. What went wrong?"
**What:** Security/privacy incident
**Why:**
- Reputational damage
- Regulatory fines (GDPR/HIPAA)
**Investigation:**
- Were documents encrypted at rest?
- Was access logged?
- Did user share index file?
- Were API keys exposed in logs?
**Prevention:**
- Implement encryption (AES-256)
- Remove sensitive data from logs
- Add document-level access control
- Implement audit trails
**Related Questions:**
- Should you encrypt embeddings?
- How long should you retain query logs?
- What compliance certifications do you need (SOC2/ISO)?

---

### 18. "User says 'Your answer was wrong' but retrieved sources seem relevant. What happened?"
**What:** Quality issue diagnosis
**Why:**
- Need root cause analysis
- Improves system
**Possible causes:**
1. **Retrieval** - Right topic, wrong info (low recall)
2. **Generation** - Misunderstood/over-simplified answer
3. **User expectation** - Unrealistic demand
4. **Context** - Documents contradict each other
**Diagnosis approach:**
- Show user actual sources
- Ask: "Were the sources relevant?"
- Check: "Did we extract the right passages?"
- Compare: LLM answer vs actual source text
**Related Questions:**
- Should you implement user feedback loop?
- How do you weight negative feedback?
- Should users rate each answer?

---

## ARCHITECTURAL QUESTIONS

### 19. "How would you handle real-time document updates?"
**What:** Customer updates document; system should reflect changes immediately
**Why:**
- Documents evolve (new policies, pricing changes)
- Current system loads index once at startup
**Solutions:**
- Implement change detection (file modification time)
- Rebuild only changed documents
- Implement streaming index updates
- Use document versioning
**Related Questions:**
- Should you rebuild entire index or just update chunks?
- How do you handle deleted documents?
- What's acceptable lag (seconds/minutes)?

---

### 20. "How would you scale from 100 documents to 1M documents?"
**What:** Scalability roadmap
**Why:**
- POC doesn't think about scale
- Enterprise customers need it
**Bottlenecks & solutions:**
| Bottleneck | POC (100 docs) | Scale (1M docs) |
|---|---|---|
| Storage | Local disk | S3/Cloud storage |
| Embedding | Batch via API | Distributed workers |
| Vector search | FAISS in-memory | Pinecone/Weaviate |
| API calls | Direct | Rate limiting/queuing |
| Metadata | In-memory dict | Database (PostgreSQL) |

**Related Questions:**
- When would you migrate from FAISS?
- Should you shard data (one index per customer)?
- How do you handle search across shards?

---

### 21. "How would you handle multi-tenancy (multiple customers)?"
**What:** Each customer has own documents, can't see others
**Why:**
- SaaS model requires this
- POC assumes single user
**Architecture:**
- Separate vector index per customer (isolation)
- Separate database records per customer
- Row-level security in metadata
- Query filtering by customer_id
**Related Questions:**
- Should indexes be in separate servers or same?
- How do you handle cross-tenant data leaks?
- What's overhead of per-customer indexes?

---

## OPERATIONAL QUESTIONS

### 22. "How would you monitor system health in production?"
**What:** Observability/alerting
**Why:**
- Catch issues before customers complain
**Key metrics:**
- Query latency (embedding + retrieval + generation)
- API error rates (Gemini failures)
- Index staleness (when last updated)
- User satisfaction (feedback ratings)
- Cost per query
**Tools:** Datadog, New Relic, CloudWatch
**Related Questions:**
- What's acceptable latency SLA?
- Should you alert on cost spikes?
- How would you detect model degradation?

---

### 23. "How would you handle API quota limits?"
**What:** Google Gemini has rate limits
**Why:**
- Unexpected usage spikes
- Cost control
**Solutions:**
- Implement request queuing
- Cache embeddings for identical queries
- Rate-limit users (per API key)
- Use cheaper models for non-critical paths
**Related Questions:**
- Should you batch embed multiple queries?
- What's your fallback if Gemini is down?
- How do you communicate rate limits to users?

---

## IMPROVEMENT & ROADMAP QUESTIONS

### 24. "What's your product roadmap for next 6 months?"
**What:** Strategic priorities
**Why:**
- Shows thinking about product/market fit
**Potential priorities:**
1. **Phase 1:** PDF support (most requested)
2. **Phase 2:** Hybrid search (BM25 + semantic)
3. **Phase 3:** Multi-language support
4. **Phase 4:** Real-time indexing
5. **Phase 5:** Analytics dashboard
**Related Questions:**
- Which feature would generate most revenue?
- What's blocking each phase?
- How would you validate each feature with customers?

---

### 25. "How would you improve answer quality by 50%?"
**What:** Measurable quality improvements
**Why:**
- Demonstrates thinking about optimization
**Approaches (in priority order):**
1. Implement re-ranking (retrieve 50, re-rank to top 4)
2. Add query expansion (rephrase query 3 ways)
3. Implement fact-checking (verify answer against sources)
4. Use better embedding model (shift to BGE/E5)
5. Add domain fine-tuning (RAG on industry-specific data)
**Related Questions:**
- How would you measure 50% improvement?
- What's cost vs benefit of each approach?
- Should you combine multiple approaches?

---

## EDGE CASES & LIMITATIONS

### 26. "What happens with empty documents or tables with no text?"
**What:** Malformed input handling
**Why:**
- Real-world files often have garbage
- System should fail gracefully
**Current behavior:** Likely creates empty chunks (wasted space)
**Improvements:**
- Skip empty chunks
- Log warning to user
- Provide feedback (e.g., "3 of 10 sheets had no data")
**Related Questions:**
- Should you validate files before indexing?
- How do you handle images in documents?
- What about encrypted PDFs?

---

### 27. "What if user asks about something not in documents?"
**What:** Out-of-domain queries
**Why:**
- System should handle gracefully
- Current behavior: Still tries to answer from unrelated chunks
**Current solution:** Prompt says "Say 'I don't know'"
**Better solution:**
- Set similarity threshold (only answer if score > 0.7)
- Return "Not found in documents" vs hallucination
- Log these queries (user expectations mismatch)
**Related Questions:**
- Should you answer general knowledge Qs?
- How confident must you be to answer?
- Should you suggest related documents?

---

### 28. "What if documents contradict each other?"
**What:** Document A says X, document B says opposite
**Why:**
- Common in evolving policies
- System might average answers (wrong)
**Handling:**
- Show both sources (let user decide)
- Flag contradictions to user
- Ask user which is authoritative
- Implement document weighting/trust scores
**Related Questions:**
- Should you warn user about conflicts?
- How do you weight newer documents?
- Should you require document dating?

---

## SUMMARY TABLE

| Category | Key Questions |
|----------|---|
| **Technical** | Why FAISS? Chunking strategy? Normalization? False negatives? |
| **Business** | Use cases? Pricing? Competitive advantage? Time-to-value? |
| **Architecture** | Real-time updates? Scaling? Multi-tenancy? |
| **Operations** | Monitoring? Rate limiting? Incident response? |
| **Product** | Roadmap? Quality improvements? Edge cases? |

---

## Interview Tips

✅ **Prepare stories** about each major decision
✅ **Think trade-offs** (speed vs accuracy, cost vs quality)
✅ **Discuss metrics** (how you'd measure success)
✅ **Mention limitations** (shows realistic thinking)
✅ **Propose improvements** (not just defensive)
✅ **Ask clarifying questions** (don't assume requirements)
