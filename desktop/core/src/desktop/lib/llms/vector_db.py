import chromadb
from chromadb.config import Settings
import pdb

import datetime

def filter_vector_db(metadata, query, database):
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="chrome"
    ))

    prompt = query
    collection = client.get_or_create_collection(name="tables")
    added_tables = set()

    current_datetime = datetime.datetime.now()

    for table in metadata:
        table_name = table['name']

        if table_name in added_tables:
            continue

        document_ids = [database + "." + table_name]

        # Check if the table already exists in the collection
        if collection.count():
            query = f'table_name:"{table_name}"'
            existing_documents = collection.get(ids=document_ids, where={"database": database})
            if len(existing_documents['documents']) > 0:
                # Check the date of the existing document
                existing_date = existing_documents['metadatas'][0].get('created_at')
                if existing_date:
                    existing_date = datetime.datetime.strptime(existing_date, "%Y-%m-%d %H:%M:%S")
                    seconds_difference = (current_datetime - existing_date).total_seconds()
                    if seconds_difference <= 60:
                        added_tables.add(table_name)
                        continue

        collection.upsert(
            documents=table,
            metadatas=[{"database": database, "table_name": table_name, "created_at": current_datetime.strftime("%Y-%m-%d %H:%M:%S")}],
            ids=document_ids
        )

        added_tables.add(table_name)

    results = collection.query(query_texts=[prompt], where={"database": database}, n_results=min(len(metadata), 10))
    table_list = [item['table_name'] for sublist in results['metadatas'] for item in sublist]
    return table_list
