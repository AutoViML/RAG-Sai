# RAG Strategy Lab - UI Guide

## 🚀 Running the Application

1.  **Navigate to the implementation directory:**
    ```bash
    cd implementation
    ```

2.  **Ensure dependencies are installed:**
    ```bash
    pip install -r requirements-advanced.txt
    ```

3.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

## 🧪 Experiment Playground Features

The interface is designed for side-by-side comparison of RAG strategies (A/B/C testing).

### 1. Strategy Configuration
You can configure up to **3 distinct strategies** simultaneously. Each strategy column allows you to customize:

*   **Chunking:** (Note: Changing this requires re-ingestion, but it's documented for experiment tracking).
*   **Embedding Model:** Select model version (informational unless multi-index support is added).
*   **Retrieval Method:**
    *   *Vector Search (Baseline):* Standard semantic similarity.
    *   *Multi-Query:* Expands your query into 3 variations for broader recall.
    *   *Hybrid:* Combines Vector search with BM25 keyword search.
*   **Reranking:** Toggle Cross-Encoder reranking on/off for higher precision.
*   **LLM Model:** Choose between models (e.g., `gpt-4o-mini` vs `gpt-4o`) to see impact on answer quality.
*   **Generation Style:**
    *   *Standard:* Direct answer generation.
    *   *Fact Verification:* Generates an answer and then cross-checks claims against source text.
    *   *Multi-Hop:* Performs iterative retrieval for complex questions.
    *   *Uncertainty:* Generates multiple answers to estimate confidence.

### 2. Side-by-Side Results
When you click **🚀 Run Comparison**:
*   All selected strategies run in parallel.
*   Results are displayed in side-by-side columns.
*   **Metrics:** Each result shows:
    *   ⏱️ **Latency:** Execution time in milliseconds.
    *   🏷️ **Cost Class:** Estimated cost (Fast/Medium/Slow).

### 3. Metrics Documentation
Expand the "📊 Understanding RAG Metrics" section at the bottom for detailed definitions.