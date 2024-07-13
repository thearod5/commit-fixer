import os.path
from typing import Dict, List, Optional

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.utils.fs import delete_dir
from safa.utils.markdown import list_formatter
from safa.utils.menus.printers import print_title


def run_search(config: SafaConfig, client: SafaClient, done_title: str = "done", k: int = 3):
    """
    Runs search on configured project
    :param config: Configuration used to get SAFA account and project.
    :param client: Client used to access SAFA API.
    :param done_title: Title used to finish search feature.
    :param k: Number of items to show.
    :return: None
    """
    print_title("Search Project")
    version_id = config.get_version_id()
    project_data = client.get_version(version_id)

    if os.path.isdir(config.vector_store_path):  # user should refresh if they want to create new one
        print("...reloading vector store...")
        db = Chroma(embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
                    persist_directory=config.vector_store_path)
    else:
        db = create_vector_store(project_data["artifacts"], vector_store_path=config.vector_store_path)

    project_artifact_types = [t["name"] for t in project_data["artifactTypes"]]
    search_types = input(f"Search Types ({','.join(project_artifact_types)}):").strip().split(",")

    while True:
        query = input(f"Search Query (or '{done_title}'):")
        if query.lower() == done_title.lower():
            return
        filter_dict = {"type": {"$in": search_types}}
        docs = db.similarity_search_with_score(query, k=k, filter=filter_dict)  # type: ignore

        print_title("Results")
        results = [f"{d.metadata['name']}\n\t{d.page_content.split('.')[0]}" for d, score in docs if
                   score > .1 and len(d.page_content) > 0]
        print(list_formatter(results), "\n")


def create_vector_store(artifacts: List[Dict], vector_store_path: Optional[str] = None):
    print("...creating vector store...")
    if len(artifacts) == 0:
        print("No artifacts in project.")
        return
    if os.path.isdir(vector_store_path):
        delete_dir(vector_store_path)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    documents = [get_artifact_document(a) for a in artifacts]
    db = Chroma.from_documents(documents, embeddings, persist_directory=vector_store_path)
    db.persist()
    return db


def get_artifact_document(a: Dict) -> Document:
    """
    Creates document from artifact.
    :param a: Artifact whose content is placed in document.
    :return: Document.
    """
    a_content = get_artifact_embedding_content(a)
    return Document(a_content, id=a["name"], metadata={"id": a["id"], "name": a["name"], "type": a["type"]})


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
