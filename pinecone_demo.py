#!/usr/bin/env python3
"""
pinecone_demo.py
=================
Retrieval-Augmented Generation demo that stores embeddings in a Pinecone v3
index (Serverless). If `PINECONE_API_KEY` is missing, it gracefully falls back
to a local Chroma store so the script can run offline.

Usage
-----
Rebuild vectors then ask one question:

    python pinecone_demo.py --source m1-rag-faq/data/faq.md \
                            --query "What is Patrianna?" --rebuild

Chat after vectors exist:

    python pinecone_demo.py

Environment
-----------
OPENAI_API_KEY            – required
PINECONE_API_KEY          – optional (enables Pinecone)
PINECONE_REGION           – default "us-east-1"
PINECONE_CLOUD            – default "aws"
"""
from __future__ import annotations

import argparse
import os
import sys
import textwrap
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
from langchain.text_splitter import MarkdownTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma, Pinecone as PineconeVectorStore

load_dotenv()

STORE_NAME = "faq-embeddings"
CHROMA_DIR = "chroma_faq"


def load_documents(src: Path) -> list[Document]:
    """Split markdown file into 400-char chunks."""
    text = src.read_text(encoding="utf-8")
    chunks = MarkdownTextSplitter(chunk_size=400, chunk_overlap=40, add_start_index=True).split_text(text)
    return [Document(page_content=c, metadata={"src": str(src)}) for c in chunks]


def build_pinecone_store(docs: list[Document]):
    """Return PineconeVectorStore if creds exist, else None."""
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        return None, None

    try:
        from pinecone import Pinecone, ServerlessSpec  # type: ignore
    except ImportError:
        print("[!] pinecone-client not installed – skipping Pinecone")
        return None, None

    pc = Pinecone(api_key=api_key)
    region = os.getenv("PINECONE_REGION", "us-east-1")
    cloud = os.getenv("PINECONE_CLOUD", "aws")

    if STORE_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=STORE_NAME,
            dimension=len(OpenAIEmbeddings().embed_query("x")),
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
    index = pc.Index(STORE_NAME)

    vs = PineconeVectorStore(index, OpenAIEmbeddings(), "text")
    if docs:
        vs.add_documents(docs)
    return vs, f"Pinecone v3 ({STORE_NAME})"


def build_chroma_store(docs: list[Document]):
    if docs or not Path(CHROMA_DIR).exists():
        vs = Chroma.from_documents(docs, OpenAIEmbeddings(), persist_directory=CHROMA_DIR)
        vs.persist()
    else:
        vs = Chroma(persist_directory=CHROMA_DIR, embedding_function=OpenAIEmbeddings())
    return vs, "Chroma (local)"


def main() -> None:
    p = argparse.ArgumentParser(description="Pinecone v3 RAG demo with Chroma fallback")
    p.add_argument("--source", default="m1-rag-faq/data/faq.md", help="Markdown file to ingest")
    p.add_argument("--rebuild", action="store_true", help="Re-embed & overwrite store")
    p.add_argument("--query", help="One-off question")
    args = p.parse_args()

    src_path = Path(args.source).expanduser()
    if not src_path.exists():
        sys.exit(f"✗ Source file not found: {src_path}")

    docs = load_documents(src_path) if args.rebuild else []

    vectorstore, backend = build_pinecone_store(docs)
    if vectorstore is None:
        vectorstore, backend = build_chroma_store(load_documents(src_path))

    print(f"✓ Vector store ready – {backend}")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(model="gpt-3.5-turbo", temperature=0), retriever)

    history: List[Tuple[str, str]] = []

    def ask(q: str) -> str:
        resp = chain.invoke({"question": q, "chat_history": history})
        history.append((q, resp["answer"]))
        return resp["answer"]

    if args.query:
        print(ask(args.query))
        return

    # Interactive loop
    try:
        while True:
            q = input("\nYou: ")
            if q.lower() in {"exit", "quit", "q"}:
                break
            print("Bot:", textwrap.fill(ask(q), width=88))
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
