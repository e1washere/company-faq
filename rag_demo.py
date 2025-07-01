from __future__ import annotations

import argparse
import os
from pathlib import Path

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain


def ingest_docs(source_path: str | Path, persist_directory: str = "chroma_store") -> Chroma:
    loader = TextLoader(str(source_path), encoding="utf‑8")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()

    vectordb = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name="company_faq_demo",
    )
    vectordb.persist()
    return vectordb


def load_vectordb(persist_directory: str = "chroma_store") -> Chroma:
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="company_faq_demo",
    )
    return vectordb

def chat_loop(vectordb: Chroma) -> None:
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    chain = ConversationalRetrievalChain.from_llm(llm, vectordb.as_retriever())

    chat_history: list[tuple[str, str]] = []
    print("\n Ask me anything about the company (type 'exit' to quit)\n")
    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting…")
            break
        if query.lower() in {"exit", "quit", "q"}:
            break

        result = chain({"question": query, "chat_history": chat_history})
        answer: str = result["answer"]
        print(f"Bot: {answer}\n")
        chat_history.append((query, answer))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small RAG FAQ bot.")
    parser.add_argument("--source", required=True, help="Path to FAQ .md/.txt file")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild vector store from source")
    args = parser.parse_args()

    persist_dir = "chroma_store"
    source = Path(args.source)
    if args.rebuild or not Path(persist_dir).exists():
        print("[+] Building vector store…")
        vectordb = ingest_docs(source, persist_directory=persist_dir)
    else:
        print("[+] Loading existing vector store…")
        vectordb = load_vectordb(persist_directory=persist_dir)
    chat_loop(vectordb)


if __name__ == "__main__":
    main()
