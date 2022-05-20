# Database process:
  # texts generator
from pymongo import MongoClient
import numpy as np

MONGODB_CONNECTION_STRING = "mongodb://lss:algo83111T%25%25@34.126.92.142:27017,35.240.200.4:27017,34.126.155.150:27017"
MONGODB_DATABASE_NAME = "lss_nlp_dataset"

client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[MONGODB_DATABASE_NAME]

class FAQs():

    client = MongoClient(MONGODB_CONNECTION_STRING)
    db = client[MONGODB_DATABASE_NAME]
    
    def _init_(self, limit=100, with_label=True):
        self.skip = 0
        self.limit = limit
        self.with_label = with_label

    def _iter_(self):
        print("iter iter iter")
        skip = 0
        while True:
            results = db.FAQ.find().skip(self.skip).limit(self.limit)
            
            no_result = True
            for result in results:
                no_result = False

                if self.with_label:
                    yield result['question'].encode('utf-8'),tf.one_hot(result['label'],config.NUM_OF_CLASS)
                else:
                    yield result['question']

            if no_result:
                break

            self.skip += self.limit

    def _next_(self):
        pass

    def _len_(self):
        return db.FAQ.count()

    def _call_(self):
        print("call call call")
        self.skip = 0
        while True:
            results = db.FAQ.find().skip(self.skip).limit(self.limit)
            
            no_result = True
            for result in results:
                no_result = False

                if self.with_label:
                    yield result['question'].encode('utf-8'),tf.one_hot(result['label'],config.NUM_OF_CLASS)
                else:
                    yield result['question']

            if no_result:
                break

            self.skip += self.limit