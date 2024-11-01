
from pymongo import MongoClient, UpdateOne
import pandas as pd
from tqdm import tqdm

class MongoDB():
    def __init__(self, username, password, cluster_url):
        
        self.username = username
        self.connection_str = f"mongodb+srv://{username}:{password}@{cluster_url}/test?retryWrites=true&w=majority".format(username, password, cluster_url)
        self.dbname='hasaki_data'
        self.client = MongoClient(self.connection_str)
       
    
    def collection(self, collection_name):
        self.db = self.client[self.dbname]
        return self.db[collection_name]
    
    def upsert_data(self, data, collection, unique_field):
        
        operations = []

        # Loop over each row in the DataFrame
        for _, row in data.iterrows():
            # Create a filter and update dictionary
            filter_query = {unique_field: row[unique_field]}
            update_query = {"$set": row.to_dict()}

            # Append the UpdateOne operation for each row
            operations.append(UpdateOne(filter_query, update_query, upsert=True))

        # Bulk write to the collection
        if operations:
            result = collection.bulk_write(operations)
            print("Upsert complete. Matched:", result.matched_count, "Inserted:", result.upserted_count)

    def query_pid(self, pid, collection_name='product_data'):
        col = self.collection(collection_name=collection_name)
        
        try:
            # Query the document using the pid
            result = col.find_one({"pid": pid})

            if result is not None:
                print("Document found:", result)
                return result  # Return the found document
            else:
                print("No document found with the given PID.")
                return None  # Return None if no document was found
        except Exception as e:
            print(f"Error querying PID: {e}")
            return None
