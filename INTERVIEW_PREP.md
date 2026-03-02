# RAG System Interview Preparation
## 30-Second Elevator Pitch

"I built an end-to-end RAG system for internal knowledge management. It ingests company documents, chunks and embeds them into a FAISS vector store, and retrieves relevant context for each query. The system uses grounded prompting to constrain the LLM to retrieved facts, applies confidence thresholds to trigger 'I don't know' responses, and validates outputs against source material. I understand that hallucinations come from three places—model knowledge leakage, poor retrieval, and over-extrapolation—and I've implemented specific techniques to address each."

---

## Key Concepts You Must Know

### What is RAG ?

RAG = Retrieval-Augmented Generation

Instead of asking an LLM to answer from memory (which causes hallucinations), we:
1. Search a knowledge base for relevant information
2. Give that information to the LLM as context
3. Ask the LLM to answer ONLY from that context

**Analogy**: It's like an open-book exam instead of a closed-book exam.

### Why RAG Over Fine-Tuning?

| RAG                                        | Fine-Tuning |
|-----                                       |-------------|
| Knowledge is updateable without retraining | Requires retraining to update |
| Source attribution possible                | No source tracking |
| Works with any base model                  | Model-specific |
| Lower cost to update                       | Expensive to retrain |
| Better for frequently changing data        | Better for stable domain knowledge |

**Say this**: "RAG keeps knowledge updatable without retraining. In a consulting environment where clients add documents frequently, RAG handles this elegantly."

---

## Where Do Hallucinations Come From?

### Source 1: Model Knowledge Leakage
The LLM "knows" things from training that aren't in your documents. It might answer using that knowledge instead of your context.

**Fix**: Grounded prompting - explicitly tell it to ignore training knowledge.

### Source 2: Poor Retrieval
If you retrieve irrelevant chunks, the LLM gets bad context and makes up answers to fill gaps.

**Fix**: Similarity threshold filtering. If nothing relevant is found, say "I don't know."

### Source 3: Over-Extrapolation
Even with good context, the LLM might infer things that aren't explicitly stated.

**Fix**: Low temperature (0.1), citation requirements, post-generation guardrails.

---

## The Five Hallucination Reduction Techniques I Implemented

### 1. Retrieval Threshold (Technique: Prevention)
```
If similarity_score < 0.3:
    return "I don't know"
```
Don't generate from irrelevant context.

### 2. Grounded Prompting (Technique: Constraint)
System prompt says:
- "Only answer from the provided context"
- "If context doesn't contain the answer, say so"
- "Cite your sources"

### 3. Low Temperature (Technique: Reduction)
Temperature = 0.1 makes the model deterministic and factual, not creative.

### 4. Source Citation (Technique: Verification)
Requiring citations forces the model to point to specific text. Harder to fake.

### 5. Post-Generation Guardrails (Technique: Detection)
After generation, check:
- Does the response hedge too much? ("probably", "I think")
- Are numbers in the response actually from the context?
- Did it cite sources?

---

## Common Interview Questions

### "Walk me through how your RAG system works."

"When a user asks a question:

1. I embed the question into a vector using sentence-transformers
2. I search FAISS for the most similar document chunks
3. I filter out any chunks below my similarity threshold
4. If no chunks pass, I return 'I don't have enough information'
5. Otherwise, I construct a prompt with the context and strict instructions
6. The LLM generates an answer constrained to that context
7. I run guardrails to check for hallucination signals
8. I return the answer with sources and confidence score

The key insight is that I have multiple layers of defense—retrieval filtering, prompt engineering, and post-generation validation."

### "How would you evaluate this system in production?"

"I'd track several metrics:

**Retrieval quality**: Average similarity scores, retrieval success rate
**Answer quality**: Grounding rate, user feedback ratings
**System health**: Latency percentiles, error rates

I'd also maintain a golden test set—questions with known answers—and run regression tests on every change. For continuous improvement, I'd implement a feedback loop where users can rate answers, and periodically review low-rated responses."

### "How would you scale this?"

"Several changes for production scale:

1. Replace FAISS with a managed vector DB like Pinecone or Weaviate for horizontal scaling
2. Add async document ingestion with a queue (Celery/RabbitMQ)
3. Cache repeated queries in Redis
4. Add observability—structured logging, metrics dashboards
5. Implement rate limiting and authentication
6. Consider chunking improvements like semantic chunking or recursive chunking"

### "What's the tradeoff between chunk size and retrieval quality?"

"Smaller chunks give more precise retrieval but less context per chunk. Larger chunks give more context but might include irrelevant information.

512 characters is a reasonable default. But the right size depends on your documents. For dense technical docs, smaller is better. For narrative content, larger preserves meaning.

The overlap is important too—it prevents losing information at chunk boundaries."

### "Why not just use a longer context window?"

"Modern LLMs have large context windows, but:

1. Cost scales with input tokens
2. 'Lost in the middle' problem—LLMs pay less attention to middle context
3. Retrieval focuses attention on relevant content
4. Source attribution is clearer with retrieved chunks

RAG is still valuable even with 100K+ context windows."

---

## Technical Details to Mention

### Embedding Model
"I use `all-MiniLM-L6-v2` from sentence-transformers. It produces 384-dimensional vectors, runs on CPU, and is good for general text. In production, I'd evaluate domain-specific models."

### Vector Search
"FAISS IndexFlatIP for exact search with inner product. Since embeddings are normalized, inner product equals cosine similarity. For millions of vectors, I'd use IVF or HNSW indexes for approximate but faster search."

### Why Ollama
"Local inference means no API costs, works offline, and keeps data on-premises—important for enterprise/consulting environments with data sensitivity."

---

## Red Flags to Avoid

- Don't say "RAG eliminates hallucinations" — it reduces them
- Don't claim 100% accuracy — acknowledge limitations
- Don't ignore evaluation — measuring quality is critical
- Don't skip source attribution — traceability matters

---

## Quick Reference: System Flow Diagram

```
User Question: "How many PTO days do I get?"
        │
        ▼
┌───────────────────┐
│  Embed Question   │  ← sentence-transformers
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  FAISS Search     │  ← Find similar chunks
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Filter by Score  │  ← Remove low-relevance chunks
└───────────────────┘
        │
        ├── Score < 0.3 ──► "I don't know"
        │
        ▼
┌───────────────────┐
│  Build Prompt     │  ← Grounded instructions + context
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  LLM (Ollama)     │  ← Generate answer
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Guardrails       │  ← Check for hallucination signals
└───────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  Response + Sources + Confidence      │
└───────────────────────────────────────┘
```

---

## Final Confidence Statement

"I have built a RAG system end-to-end. I understand where hallucinations come from—model knowledge leakage, poor retrieval, and over-extrapolation. I've implemented multiple mitigation techniques: retrieval thresholds, grounded prompting, low temperature, citation requirements, and post-generation guardrails. I know how to evaluate and scale this system for production use."

---

## Day-Before Checklist

- [ ] Run the system locally and verify all endpoints work
- [ ] Practice the 30-second pitch out loud 3 times
- [ ] Review the 5 hallucination reduction techniques
- [ ] Be ready to whiteboard the system flow diagram
- [ ] Have specific numbers ready (chunk size: 512, threshold: 0.3, temp: 0.1)
