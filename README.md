# Azure-Cognitive-Search-Opinion-Mining

---
Description:
- opinion_mining_skill is an Azure Cognitive Search custom skill to integrate [Azure Text Analytics - Opinion Mining](https://docs.microsoft.com/en-us/azure/cognitive-services/language-service/sentiment-opinion-mining/overview) within a Azure Cognitive Search skillset. This will enable the cracking of documents in a programmatic way to enrich your search with opining mining data.

Languages:
- ![python](https://img.shields.io/badge/language-python-orange)

Products:
- Azure Cognitive Search
- Azure Cognitive Services (Text Analytics)
- Azure Functions
---

# Steps    

1. Create or reuse a Text Analytics resource starting from the [Azure portal](https://portal.azure.com) or in [Language Studio](https://language.azure.com/home)
2. [Create a Python Function in Azure](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python)
3. Clone this repository
4. Open the folder in VS Code and [deploy the function](https://docs.microsoft.com/azure/search/cognitive-search-custom-skill-python)
5. Upload your Functions appsettings with the custom details from your deployment ('COGNITIVE_SERVICES_ENDPOINT', 'COGNITIVE_SERVICES_API_KEY)
6. Add a field in your index where you will dump the enriched classes, more info [here](#sample-index-field-definition)
7. Add the skill to your skillset as [described below](#sample-skillset-integration)
8. Add the output field mapping in your indexer as [seen in the sample](#sample-indexer-output-field-mapping)
9. Run the indexer 

## Sample Input:

You can find a sample input for the skill [here](./OpinionMining/sample.dat)

```json
{
    "values": [
        {
            "recordId": "e1",
            "data":
            {
                "text":  "il servizio clienti è ottimo. il cibo è negativo",
                "language" : "it"
            }
        },
                {
            "recordId": "e2",
            "data":
            {
                "text":  "The food and service were unacceptable, but the concierge were nice",
                "language": "en"
            }
        }
    ]
}
```

## Sample Output:

```json
{
    "values": [
        {
            "data": {
                "targets": [
                    {
                        "sentence": "il servizio clienti è ottimo. ",
                        "sentiment": "positive",
                        "text": "servizio clienti"
                    },
                    {
                        "sentence": "il cibo è negativo",
                        "sentiment": "negative",
                        "text": "cibo"
                    }
                ]
            },
            "recordId": "e1"
        },
        {
            "data": {
                "targets": [
                    {
                        "sentence": "The food and service were unacceptable, but the concierge were nice",
                        "sentiment": "negative",
                        "text": "food"
                    },
                    {
                        "sentence": "The food and service were unacceptable, but the concierge were nice",

                        "sentiment": "negative",
                        "text": "service"
                    },
                    {
                        "sentence": "The food and service were unacceptable, but the concierge were nice",
                        "sentiment": "positive",
                        "text": "concierge"
                    }
                ]
            },
            "recordId": "e2"
        }
    ]
}
```

## Sample Skillset Integration

In order to use this skill in a cognitive search pipeline, add a skill definition to your skillset.
Here's a sample skill definition for this example (inputs and outputs should be updated to reflect your scenario and skillset environment):

```json
    {
      "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
      "name": "Text Classification",
      "description": "Classify your text",
      "context": "/document",
      "uri": "https://YOUR_AZURE_FUNCTION_NAME.azurewebsites.net/api/OpinionMining?code=xx==",
      "httpMethod": "POST",
      "timeout": "PT30S",
      "batchSize": 100,
      "degreeOfParallelism": null,
      "inputs": [
        {
          "name": "language",
          "source": "/document/language"
        },
        {
          "name": "text",
          "source": "/document/content"
        }
      ],
      "outputs": [
        {
          "name": "targets",
          "targetName": "targets"
        }
      ],
      "httpHeaders": {}
    }
```

## Sample Index Field Definition

The skill will output the text classes that have been extracted for the corpus. In this example, I am expecting several classes so a Collection of ComplexType object is needed, including subfields for category and confidence.

```json
{
  "name": "textclassindex",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "facetable": false,
      "filterable": false,
      "key": true,
      "retrievable": true,
      "searchable": false,
      "sortable": false,
      "analyzer": null,
      "indexAnalyzer": null,
      "searchAnalyzer": null,
      "synonymMaps": [],
      "fields": []
    },
    {
      "name": "corpus",
      "type": "Edm.String",
      "facetable": false,
      "filterable": false,
      "key": false,
      "retrievable": true,
      "searchable": true,
      "sortable": false,
      "analyzer": "standard.lucene",
      "indexAnalyzer": null,
      "searchAnalyzer": null,
      "synonymMaps": [],
      "fields": []
    },
    {
      "name": "textclass",
      "type": "Collection(Edm.ComplexType)",
      "analyzer": null,
      "synonymMaps": [],
      "fields": [
        {
          "name": "category",
          "type": "Edm.String",
          "facetable": true,
          "filterable": true,
          "key": false,
          "retrievable": true,
          "searchable": true,
          "sortable": false,
          "analyzer": "standard.lucene",
          "indexAnalyzer": null,
          "searchAnalyzer": null,
          "synonymMaps": [],
          "fields": []
        },
        {
          "name": "confidence",
          "type": "Edm.Double",
          "facetable": true,
          "filterable": true,
          "retrievable": true,
          "sortable": false,
          "analyzer": null,
          "indexAnalyzer": null,
          "searchAnalyzer": null,
          "synonymMaps": [],
          "fields": []
        }
      ]
    }
}
```

## Sample Indexer Output Field Mapping

The output enrichment of your skill can be mapped to one of your fields described above. This can be done with the indexer setting:
```
  "outputFieldMappings": [
    {
      "sourceFieldName": "/document/targets",
      "targetFieldName": "targets"
    }
  ],
```