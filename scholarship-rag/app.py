#!/usr/bin/env python3
"""Interactive terminal scholarship RAG demonstration."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from rag import (
    LexicalRetriever,
    generate_ollama_answer,
    ingest_pdf,
    load_chunks,
    select_evidence,
)

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "data/source/terms-conditions.pdf"
INDEX = ROOT / "data/index/chunks.json"


def build_retriever(reindex: bool = False) -> LexicalRetriever:
    chunks = ingest_pdf(PDF, INDEX) if reindex or not INDEX.exists() else load_chunks(INDEX)
    return LexicalRetriever(chunks)


def print_results(label: str, results: list[dict]) -> None:
    print(f"\n{'=' * 72}")
    print(label)
    print("=" * 72)
    for result in results:
        print(f"#{result['rank']}  Score: {result['score']:.6f}")
        print(f"    Chunk: {result['chunk_id']}")
        print(f"    {result['citation']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve scholarship evidence and answer with Ollama")
    parser.add_argument("--reindex", action="store_true", help="rebuild chunks from the PDF")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3.2:3b"), help="Ollama model name")
    parser.add_argument("--ollama-url", default=os.getenv("OLLAMA_URL", "http://localhost:11434"), help="Ollama server URL")
    args = parser.parse_args()

    retriever = build_retriever(args.reindex)
    print(f"\nScholarship retrieval demo loaded {len(retriever.chunks)} chunks.")
    print("Enter a question to compare BM25 and TF-IDF.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("Question > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        if not question:
            continue

        comparison = retriever.compare(question)
        print(f"\nTokens: {comparison['tokens']}")
        print_results("BM25 — top 3 chunks", comparison["bm25"])
        print_results("TF-IDF — top 3 chunks", comparison["tfidf"])
        same = comparison["bm25"][0]["chunk_id"] == comparison["tfidf"][0]["chunk_id"]
        print(f"\nAgreement: {'YES — both selected the same chunk' if same else 'NO — they selected different chunks'}")

        evidence = select_evidence(comparison)
        print(f"\nGenerating a grounded answer with Ollama model {args.model}...")
        try:
            answer = generate_ollama_answer(question, evidence, args.model, args.ollama_url)
        except RuntimeError as exc:
            print(f"\nOllama error: {exc}\n")
            continue

        print(f"\n{'=' * 72}\nOLLAMA ANSWER\n{'=' * 72}")
        print(answer)
        print("\nSources used:")
        for item in evidence:
            print(f"- {item['citation']} ({item['chunk_id']})")
        print()


if __name__ == "__main__":
    main()
