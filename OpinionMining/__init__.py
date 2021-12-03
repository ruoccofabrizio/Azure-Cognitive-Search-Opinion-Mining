import logging

import azure.functions as func
import json
import requests
import os
import traceback

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = json.dumps(req.get_json())
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
    if body:
        result = compose_response(body)
        return func.HttpResponse(result, mimetype="application/json")
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )


def compose_response(json_data):
    values = json.loads(json_data)['values']
    results = {}
    results["values"] = transform_values(values)
    return json.dumps(results, ensure_ascii=False)


def convert_format(x):
    x["id"] = x.pop("recordId")
    x["language"] = x['data']['language']
    x["text"] = x['data']['text']
    return x

def transform_values(values):
    try:
        url = f"https://{os.environ.get('COGNITIVE_SERVICES_ENDPOINT')}.cognitiveservices.azure.com/text/analytics/v3.2-preview.1/sentiment?opinionMining=true&model-version=2021-10-01-preview"

        headers = {
            "Content-Type" : "application/json",
            "Ocp-Apim-Subscription-Key": os.environ.get('COGNITIVE_SERVICES_API_KEY')
        }

        body = {
            "documents" : list(map(lambda x: convert_format(x), values))
        }

        r = requests.post(url, headers=headers, json=body)
        doc_result = r.json()['documents']

        values = []
        for document in doc_result:
            value = {
                "recordId" : document['id'],
                "data" : {
                    "targets" : []
                }
            }
            for sentence in document['sentences']:
                for target in sentence['targets']:
                    value["data"]['targets'].append({"text" : target['text'], "sentiment": target['sentiment'], "sentence": sentence['text']})
            values.append(value)

    except:
        return list(map(lambda x: format_error(x, traceback.format_exc()), body['documents']))

    return values


def format_error(x, err):
    return {
        "recordId": x['id'],
        "error" : str(err)
    }



