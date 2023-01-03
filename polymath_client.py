"""The simplest possible client for the Polymath server."""

import json
import urllib3

from ask_embeddings import (base64_from_vector, get_completion_with_context,
                            get_embedding, Library, get_context_for_library,
                            get_chunk_infos_for_library, CURRENT_VERSION,
                            EMBEDDINGS_MODEL_ID)

CONTEXT_TOKEN_COUNT = 2000


def query_server(query_embedding, server):
    http = urllib3.PoolManager()
    response = http.request(
        'POST', server, fields={
            "version": CURRENT_VERSION,
            "query_embedding": query_embedding,
            "query_embedding_model": EMBEDDINGS_MODEL_ID,
            "count": CONTEXT_TOKEN_COUNT}).data
    obj = json.loads(response)
    print(f"Got response from the server")
    if 'error' in obj:
        error = obj['error']
        raise Exception(f"Server returned an error: {error}")
    return Library(data=obj)


def ask_polymath(query, server):
    query_vector = base64_from_vector(get_embedding(query))
    library = query_server(query_vector, server)
    context = get_context_for_library(library)
    sources = [(info["url"], info["title"])
               for info in get_chunk_infos_for_library(library)]
    answer = get_completion_with_context(query, "\n".join(context))
    print("Got completion")
    return answer, sources
