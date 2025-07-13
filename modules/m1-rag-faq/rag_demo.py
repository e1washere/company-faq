from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

load_dotenv()

DEFAULT_SOURCE = Path("data/faq.md")
PERSIST_DIR = "vector_store"
COLLECTION = "company_faq_demo"


def ingest_docs(source_path: Path, persist_directory: str = PERSIST_DIR) -> Chroma:
    """Load a markdown/txt file, embed chunks, and persist to Chroma."""
    docs = TextLoader(str(source_path), encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1_000, chunk_overlap=200
    ).split_documents(docs)

    vectordb = Chroma.from_documents(
        chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory,
        collection_name=COLLECTION,
    )
    return vectordb


def load_vectordb(persist_directory: str = PERSIST_DIR) -> Chroma:
    """Load an existing on-disk Chroma store."""
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=OpenAIEmbeddings(),
        collection_name=COLLECTION,
    )


def single_query(
    query: str,
    vectordb: Chroma,
    history: List[Tuple[str, str]] | None = None,
) -> str:
    """Run a single retrieval-augmented query."""
    chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0),
        vectordb.as_retriever(),
    )
    result = chain.invoke({"question": query, "chat_history": history or []})
    return result["answer"]


def chat_loop(vectordb: Chroma) -> None:
    """Simple REPL until user types ‘exit’."""
    history: List[Tuple[str, str]] = []
    print("\nAsk me anything about the company (type 'exit' to quit)\n")
    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting…")
            break
        if query.lower() in {"exit", "quit", "q"}:
            break
        answer = single_query(query, vectordb, history)
        print(f"Bot: {answer}\n")
        history.append((query, answer))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny RAG FAQ bot.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE),
                        help="Path to FAQ .md/.txt file")
    parser.add_argument("--rebuild", action="store_true",
                        help="Rebuild vector store from source")
    parser.add_argument("--query",
                        help="Run one-off question and quit")
    args = parser.parse_args()

    if args.rebuild or not Path(PERSIST_DIR).exists():
        print("[+] Building vector store…")
        vectordb = ingest_docs(Path(args.source))
    else:
        print("[+] Loading existing vector store…")
        vectordb = load_vectordb()

    if args.query:
        print("\nAnswer:", single_query(args.query, vectordb), "\n")
    else:
        chat_loop(vectordb)


if __name__ == "__main__":
    main()