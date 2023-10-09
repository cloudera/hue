#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import chromadb
import datetime

def filter_vector_db(metadata, query, database):
  chrome_client = chromadb.PersistentClient(path="chrome")
  prompt = f"find the table required for the prompt here: {query}"

  collection = chrome_client.get_or_create_collection(name="tables")
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
      documents=table_name,
      metadatas=[{"database": database, "table_name": table_name, "created_at": current_datetime.strftime("%Y-%m-%d %H:%M:%S")}],
      ids=document_ids
    )

    added_tables.add(table_name)

  results = collection.query(query_texts=[prompt], where={"database": database}, n_results=min(len(metadata), 10))
  table_list = [item['table_name'] for sublist in results['metadatas'] for item in sublist]
  return table_list
