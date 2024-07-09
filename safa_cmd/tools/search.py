import os.path
from typing import Dict, List, Optional

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from safa_cmd.config import SafaConfig
from safa_cmd.safa.safa_client import SafaClient
from safa_cmd.utils.menu import input_confirm
from safa_cmd.utils.printers import print_title


def run_search(config: SafaConfig, client: SafaClient):
    """
    Runs search on configured project
    :param config: Configuration used to get SAFA account and project.
    :param client: Client used to access SAFA API.
    :return: None
    """
    print("...retrieving project data...")
    version_id = config.get_version_id()
    project_data = client.get_version(version_id)

    if os.path.isdir(config.vector_store_path) and input_confirm("Reload previous vector store?"):
        print("...reloading vector store...")
        db = Chroma(embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
                    persist_directory=config.vector_store_path)
    else:
        print("...create new vector store...")
        db = build_vector_store(project_data["artifacts"], vector_store_path=config.vector_store_path)
        db.persist()
    while True:
        query = input("Search Query (or 'exit'):")
        if query == 'exit':
            return

        docs = db.similarity_search(query, k=3)

        for doc in docs:
            print_title(doc.metadata["name"], factor=0.25)
            print(doc.page_content.split(".")[0])


def build_vector_store(artifacts: List[Dict], vector_store_path: Optional[str] = None):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    documents = [get_artifact_document(a) for a in artifacts]
    db = Chroma.from_documents(documents, embeddings, persist_directory=vector_store_path)
    return db


def get_artifact_document(a: Dict) -> Document:
    """
    Creates document from artifact.
    :param a: Artifact whose content is placed in document.
    :return: Document.
    """
    a_content = get_artifact_embedding_content(a)
    return Document(a_content, id=a["name"], metadata={"id": a["id"], "name": a["name"]})


def get_artifact_embedding_content(a: Dict):
    """
    Returns the content used to embed an artifact.
    :param a: The artifact JSON.
    :return: Artifact content to embed.
    """
    summary = a["summary"]
    if isinstance(summary, str) and len(summary) > 0:
        return summary
    return a["body"]
