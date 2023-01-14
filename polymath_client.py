"""The simplest possible client for the Polymath server."""

import json
import urllib3

from ask_embeddings import (base64_from_vector, get_completion_for_multiple_subjects,
                            get_completion_for_subjects_and_topics,
                            get_completion_with_context,
                            get_embedding, Library, get_context_for_library,
                            get_chunk_infos_for_library, CURRENT_VERSION,
                            EMBEDDINGS_MODEL_ID)

# Smaller number to allow for all three endpoints.
CONTEXT_TOKEN_COUNT = 500

KNOWN_POLYMATH_ENDPOINTS = {
    "alex": {
        "nickname": "Alex",
        "url": "https://polymath.komoroske.com"
    },
    "dimitri": {
        "nickname": "Dimitri",
        "url": "https://polymath.glazkov.com"
    },
    "dion": {
        "nickname": "Dion",
        "url": "https://polymath.almaer.com"
    },
    "flux": {
        "nickname": "FLUX",
        "url": "https://polymath.fluxcollective.org"
    }
}


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


def format_polymath_embed(answer, sources):
    sources_label = "Here are some inks to explore" if answer == "I don't know." else "Sources"
    links = "\n".join([f" - [{title}]( {url} )" for url, title in sources[:4]])
    return f"{answer}\n\n{sources_label}:\n{links}"


def dion_action(prompt):
    return format_polymath_embed(*ask_polymath(prompt, KNOWN_POLYMATH_ENDPOINTS["dion"]["url"]))


def polymath_action(prompt):
    known_subjects = [endpoint["nickname"]
                      for endpoint in KNOWN_POLYMATH_ENDPOINTS.values()]
    print(known_subjects)
    # First, determine subjects and topics
    subjects_and_topics = json.loads(
        get_completion_for_subjects_and_topics(known_subjects, prompt))
    print(f"Got subjects and topics: {subjects_and_topics}")
    context_query = ", ".join(subjects_and_topics.get("topics"))
    query_vector = base64_from_vector(get_embedding(context_query))

    context = ""

    # Then, query Polymath endpoints on the subject and get contexts
    # and compose context out of subjects's contexts
    for subject in subjects_and_topics.get("subjects"):
        server = KNOWN_POLYMATH_ENDPOINTS.get(subject.lower(), '')
        if not server:
            continue
        library = query_server(query_vector, server["url"])
        context += f"\n{server['nickname']} says:\n {' '.join(get_context_for_library(library))}\n"

    print("Got context")

    # Then, do the usual completion with the composed context
    answer = get_completion_for_multiple_subjects(prompt, context)

    print("Got completion")
    return answer
