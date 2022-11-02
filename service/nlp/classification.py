import traceback
from ._caller import TextClassifierApiCaller
from django.conf import settings
import numpy as np

import requests
import json

def classify_comment_v1(texts, threshold=0.9):
    try:
        categories = np.array(['neutro', 'payment', 'delivery'])

        data = {
            "instances": texts
        }
        code, response = TextClassifierApiCaller("v1/models/lss_comment_classification:predict", data=data).post()
       
        if code != 200:
            return []

        predictions = np.array(response.get("predictions"))
        max_index = np.argmax(predictions, axis=1) + 1
        threshold_filter = np.sum((predictions > threshold), axis=1)
        index = max_index * threshold_filter
    except Exception:
        return []
    return list(categories[index])

def classify_comment_v2(texts):

    try:
        categories = np.array(["chat","purchase", "delivery", "return"])

        data = {
            "instances": texts
        }
        url = f'{settings.NLP_COMPUTING_MACHINE_URL}/v1/models/lss_comment_classification:predict'
        response = requests.post(url=url,json=data, timeout=5)
        data = json.loads(response.text)
        predictions = np.array(data.get('predictions'))
        print ('predictions')
        print (predictions)
        class_index = np.argmax(predictions, axis=1)
        return list(categories[class_index])

    except Exception :
        print(traceback.format_exc())
        return []
    return []