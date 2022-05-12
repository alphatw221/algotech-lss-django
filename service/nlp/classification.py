from ._caller import TextClassifierApiCaller
import numpy as np


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