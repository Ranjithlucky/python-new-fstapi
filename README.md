import os

import re

import pickle

import uuid

import json

from dotenv import load_dotenv

from office365.sharepoint.client_context import ClientContext

from office365.sharepoint.files.file import File

from office365.runtime.auth.user_credential import UserCredential

from google.cloud import (storage, aiplatform)

from langchain_community.document_loaders import PyMuPDFLoader

from langchain_google_community import GCSFileLoader

from langchain_google_vertexai import VertexAIEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_google_vertexai import VectorSearchVectorStore

                                       

load_dotenv()



PROJECT_ID = os.environ.get("PROJECT_ID")

PROJECT_LOCATION = os.environ.get("PROJECT_LOCATION")

PROJECT_INPUT_BUCKET = os.environ.get("PROJECT_INPUT_BUCKET")

PROJECT_OUTPUT_BUCKET = os.environ.get("PROJECT_OUTPUT_BUCKET")



EMBEDDINGS = VertexAIEmbeddings(model="text-embedding-005")

DIMENSIONS = 768





SITE_URL = "https://collaborate.mcd.com/sites/MCDProcess"

FOLDER_URL = "/sites/MCDProcess/Shared Documents/General/GenAI/"



aiplatform.init(project=PROJECT_ID, location=PROJECT_LOCATION, staging_bucket=PROJECT_OUTPUT_BUCKET)



def init_sharepoint_config(site_url):

   

    # User credentials

    username = os.environ.get("SHAREPOINT_USERNAME")

    password = os.environ.get("SHAREPOINT_PASSWORD")

   

    # Authentication

    ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))

    return ctx



def is_new_or_updated(file):

    storage_client = storage.Client()

    bucket = storage_client.bucket(PROJECT_INPUT_BUCKET)

    blobs = bucket.list_blobs()

    is_new = True



    for blob in blobs:

        if file.properties["Name"] == blob.name:

            is_new = False

    return is_new



def fetch_files_from_sharepoint_folder(ctx, folder_url):

    folder = ctx.web.get_folder_by_server_relative_url(folder_url)

    files = folder.files

    ctx.load(files)

    ctx.execute_query()



    # Save files locally

    for file in files:

        if is_new_or_updated(file):

            file_name = file.properties["Name"]

            file_url = file.serverRelativeUrl

            print('Updated file found:', file_url)

            response = File.open_binary(ctx, file_url)

                # local_file.write(response.content)

               

            storage_client = storage.Client()

            bucket = storage_client.bucket(PROJECT_INPUT_BUCKET)

            blob = bucket.blob(file_name)

            blob.upload_from_string(response.content)



    # Recursively fetch files from subfolders

    subfolders = folder.folders

    ctx.load(subfolders)

    ctx.execute_query()

    for subfolder in subfolders:

        fetch_files_from_sharepoint_folder(ctx, subfolder.serverRelativeUrl)



# Document Loading, Chunking, Embedding

def load_pdf(file_path):

    """Method for loading pdf file using PyMyPDFLoader"""

    return PyMuPDFLoader(file_path)



def read_gcp_bucket_file(bucket_name, file_name):

    """Method to read file from GCP Bucket using library"""

    loader = GCSFileLoader(project_name=PROJECT_ID, bucket=bucket_name, blob=file_name, loader_func=load_pdf)

    data = loader.load()

    return data

   

def read_pdfs_from_bucket(bucket_name):

    """Method for read all files from the GCP Bucket"""

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs()



    documents = []

    for blob in blobs:

        if blob.name.endswith('.pdf'):

            pdf_content = blob.download_as_bytes()

            documents.append(PyMuPDFLoader(blob))

    return documents



def chunk_document(documents, chunk_size=1000, chunk_overlap=20):

    """Method to split loaded document data using Splitter library"""

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    all_splits = text_splitter.split_documents(documents)

    return all_splits



def get_embedded_data(embedding_obj, data):

    """Method to embed given data"""

    return embedding_obj.embed_documents(data)



def get_text_from_chunks(data):

    """Method for convert splited data into string(plain text)"""

    texts = [str(chunk) for chunk in data]

    return texts



def save_file_to_bucket(bucket_name, destination_blob_name, vector=None):

    """Saves pickled PDF page embeddings to a Google Cloud Storage bucket."""

    storage_client = storage.Client(project=PROJECT_ID)

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)

    if vector:

        blob.upload_from_string(pickle.dumps(vector))

    else:

        blob.upload_from_filename(destination_blob_name)





# Index, IndexEndpoint

def create_index(display_name, dimensions=768):

    """Method to create an index"""

    new_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(

        display_name=display_name,

        # contents_delta_uri = BUCKET_URI,

        dimensions=dimensions,

        approximate_neighbors_count=10,

        distance_measure_type="DOT_PRODUCT_DISTANCE",

        leaf_node_embedding_count=100,

        leaf_nodes_to_search_percent=7,

        index_update_method="STREAM_UPDATE",  # allowed values BATCH_UPDATE , STREAM_UPDATE

        )

    return new_index



def create_index_endpoint(display_name):

    """Method to create an index enpoint"""

    new_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(

        display_name=f"{display_name}-endpoint", public_endpoint_enabled=True

        )

    return new_index_endpoint



# Vertex store

# def insert_into_vertex_datastore(documents, embeddings):

#     """Method for insert embedding into vertex datastore"""

#     # Initialize Datastore client

#     client = datastore.Client()



#     # Insert embeddings into Datastore

#     for doc, embedding in zip(documents, embeddings):

#         key = client.key("DocumentEmbedding", doc.id)

        # entity = datastore.Entity(key=key)

        # entity.update({"content": doc.content, "embedding": embedding})

        # client.put(entity)



def create_vector_store(project_id, project_region, project_bucket, embedding_model, index_id, index_endpoint):

    """Method to create vector store"""

    vector_store = VectorSearchVectorStore.from_components(

        project_id=project_id,

        region=project_region,

        gcs_bucket_name=project_bucket,

        index_id=index_id.name,

        endpoint_id=index_endpoint.name,

        embedding=embedding_model,

        )

    return vector_store



query = ["what is bucket"]

qry_emb = get_embedded_data(EMBEDDINGS, query)



# Fetch response using semantic search

def fetch_response_from_semantic_search(query_embedding, vector_store):

    response = vector_store.similarity_search(query_embedding)

    return response





response = fetch_response_from_semantic_search(qry_emb, vector_search)



# Include PDF file name in the response

for res in response:

    print(f"PDF File: {res['file_name']}, Response: {res['content']}")





# # Fetch files from the main folder and its subfolders

# ctx = init_sharepoint_config(SITE_URL)

# fetch_files_from_sharepoint_folder(ctx, FOLDER_URL)





# index_name = "test-tririga-index"

# new_index = create_index(index_name, dimensions=DIMENSIONS)

# new_index_endpoint = create_index_endpoint(index_name)



# my_index = aiplatform.MatchingEngineIndex(os.environ.get("INDEX_ID"))

# my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(os.environ.get("INDEX_ENDPOINT_ID"))





# deploy the Index to the Index Endpoint

# DEPLOYED_INDEX_ID = "test_tririga_deployed"

# my_index_endpoint.deploy_index(index=my_index, deployed_index_id=DEPLOYED_INDEX_ID)





# documents = read_pdfs_from_bucket(PROJECT_INPUT_BUCKET)



# source_file_name = "Getting_Started_with_Google_Cloud_Platform.pdf"

# documents = read_gcp_bucket_file(PROJECT_INPUT_BUCKET, source_file_name)

# chunked_data = chunk_document(documents, chunk_size=1000, chunk_overlap=20)

# text_data = get_text_from_chunks(chunked_data)



# texts = [chunk.page_content for chunk in chunked_data]



# vector_store = create_vector_store(PROJECT_ID, PROJECT_LOCATION, PROJECT_OUTPUT_BUCKET, EMBEDDINGS, my_index, my_index_endpoint)

# print("VECTOR STORE", vector_store)



# vector_store.add_texts(texts=texts)



# vectors = get_embedded_data(EMBEDDINGS, texts)





# for vector in vectors:

#     print(str(vector)[:100])  # Show the first 100 characters of the vector



# def clean_text(text):

#         cleaned_text = re.sub(r'\u2022', '', text)  # Remove bullet points

#         cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Remove extra whitespaces and strip

#         return cleaned_text



# with open("embed_file_GCP.json", 'w') as embed_file, open("sentence_file_GCP.json", 'w') as sentence_file:

#     for sentence, embedding in zip(texts, vectors):

#                     cleaned_sentence = clean_text(sentence)

#                     id = str(uuid.uuid4())

                   

#                     embed_item = {"id": id, "embedding": embedding}

#                     sentence_item = {"id": id, "sentence": cleaned_sentence}

                   

#                     json.dump(sentence_item, sentence_file)

#                     sentence_file.write('\n')

#                     json.dump(embed_item, embed_file)

#                     embed_file.write('\n')



                    # blob.upload_from_string(data=json.dumps(some_json_object),content_type='application/json')  



# destination_blob_name = "embed_file_GCP.json"

# save_file_to_bucket(PROJECT_OUTPUT_BUCKET, destination_blob_name)



# destination_blob_name = "sentence_file_GCP.json"

# save_file_to_bucket(PROJECT_OUTPUT_BUCKET, destination_blob_name)









# query = ["what is bucket"]

# qry_emb = get_embedded_data(EMBEDDINGS, query)



# # Test query

# response = my_index_endpoint.find_neighbors(

#     deployed_index_id=os.environ.get("INDEX_DEPLOYED_ID"),

#     queries=qry_emb,

#     num_neighbors=10,

# )



# # print(response[0])



# for idx, neighbor in enumerate(response[0]):

#     print(idx, f"{neighbor.distance:.2f}")

# query = ["what is bucket"]

# qry_emb = get_embedded_data(EMBEDDINGS, query)



# # Fetch response using semantic search

# def fetch_response_from_semantic_search(query_embedding, vector_store):

#     response = vector_store.similarity_search(query_embedding)

#     return response



# # vector_store = create_vector_store(PROJECT_ID, PROJECT_LOCATION, PROJECT_INPUT_BUCKET, EMBEDDINGS, my_index, my_index_endpoint)

# response = fetch_response_from_semantic_search(qry_emb, vector_store)

# # response = fetch_response_from_semantic_search(qry_emb)



# # Include PDF file name in the response

# for res in response:

#     print(f"PDF File: {res['file_name']}, Response: {res['content']}")



# show the result

# import numpy as np



# for idx, neighbor in enumerate(response[0]):

#     id = np.int64(neighbor.id)

#     similar = df.query("id == @id", engine="python")

#     print(f"{neighbor.distance:.4f} {similar.title.values[0]}")





      for this code all as to be done and stored in vector store after u have to do call the vector store and do  similairty search ..dont recreate again for vector store it as allreday stored just u call and do smilairty search
