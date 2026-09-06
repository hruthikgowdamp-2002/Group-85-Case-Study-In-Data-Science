# Walert Reproduction Notes

## Setup

I reproduced the Walert baseline on my Windows laptop using WSL (Ubuntu). I used Python 3.9.25 inside a virtual environment called `walert_env` and Java 11 for Pyserini.

I faced a few setup issues while getting Walert to run. Pyserini initially could not find Java, so I installed OpenJDK 11. I also had an ONNX Runtime error related to the executable stack. After fixing this issue, I was able to run the retrieval scripts successfully.

## BM25 Reproduction

I first reproduced the BM25 retrieval using the existing Lucene index provided with Walert.

Before running it, I kept a copy of the original `rag-bm25.txt` so that I could compare it with my reproduced result. After running `search.py`, I compared the new file with the original using `cmp`.

There was no difference between the two files, which showed that I was able to reproduce the original BM25 retrieval results successfully.

## Dense/FAISS Reproduction

Next, I reproduced the Dense/FAISS retrieval using the provided FAISS index and DPR question encoder.

The reproduced file was not completely identical to the original file because there were very small differences in some floating-point scores. The run name was also slightly different (`dense-faiss` instead of `dense.faiss`).

I then compared only the query IDs, document IDs and ranking positions between the two files. There were no differences, meaning that the same documents were retrieved in the same ranking order.

## Evaluation Results

After reproducing the retrieval runs, I ran the Walert evaluation using the provided qrels.

| Model | NDCG@1 | NDCG@3 | NDCG@5 |
|---|---:|---:|---:|
| Walert Intent | 0.0833 | 0.0391 | 0.0391 |
| Walert RAG BM25 | 0.1667 | 0.2566 | 0.3291 |
| Walert RAG Dense/FAISS | 0.2500 | 0.2380 | 0.2380 |

From these results, Dense/FAISS performed better at NDCG@1 with 0.2500. BM25 performed better when more results were considered, with NDCG@3 of 0.2566 and NDCG@5 of 0.3291.

## Outcome

Overall, I was able to reproduce the Walert baseline successfully. The BM25 output matched the original file exactly. The Dense/FAISS run produced the same document rankings as the original, with only very small differences in the retrieval scores and the run-name formatting.

This reproduction also helped me understand how the BM25 and dense retrieval approaches in Walert are executed and evaluated before we move on to developing our own RAG system for the RMIT Scholarship and Financial Support Assistant.
