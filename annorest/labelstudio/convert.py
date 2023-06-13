
## 轉換為標準交換格式的範例函數
# def load_xx(data, keep_all_information=False):
#     def text_to_unified(text):
#         # 實作此程式
#         return text
#     def label_to_unified(labels, text=None):
#         # 實作此程式
#         return labels
#     # 轉換
#     db = []
#     for single_doc in data:
#         if keep_all_information==False:
#             db.append({
#                 'text': text_to_unified(single_doc['text']),
#                 'labels': label_to_unified(single_doc['labels'])
#             })
#     return db

# 可輸入單筆資料或多筆資料
# 單筆資料格式不限
# 多筆資料為單筆資料的list
def convert(data, input = "DATABASE", output='BIO'):
    if not isinstance(data, list):
        data = [data]
    # 輸入層
    if input == "DATABASE":
        formated_data = import_db(data)
    
    # 輸出層
    if output == "UNIFIED":
        output_data = formated_data
    elif output == "BIO":
        output_data = export_bio(formated_data)
    return output_data


def import_db(data, keep_all_information=False):
    def text_to_unified(text):
        return text
    def label_to_unified(labels, text=None):
        unified_label = []
        for label in labels:
            unified_label.append({
                'start': label[0],
                'end': label[1],
                'label': label[2]
            })
        return unified_label
    # 載入資料庫
    db = []
    for single_doc in data:
        if keep_all_information==False:
            db.append({
                'text': text_to_unified(single_doc['article_content']),
                'labels': label_to_unified(single_doc['result']['2'])
            })
    return db

def export_bio(data):
    def unified_to_bio_text(text):
        # 實作此程式
        return text
    def unified_to_bio_label(labels, text=None):
        # 實作此程式
        instance_label=['O'] * len(text) #先全部填寫O
        for label in labels:
            start_index = label['start']
            end_index = label['end']
            label = label['label']
            for i in range(start_index, end_index):
                if i == start_index:
                    instance_label[i] = "B-" + str(label)
                else:
                    instance_label[i] = "I-" + str(label)
        return instance_label
    result = []
    for single_doc in data:
        result_single_doc = {}
        result_single_doc['text'] = unified_to_bio_text(single_doc['text'])
        result_single_doc['labels'] = unified_to_bio_label(single_doc['labels'], single_doc['text'])
        assert len(result_single_doc['text']) == len(result_single_doc['labels'])
        result.append(result_single_doc)
   
    return result





def db_to_labelstudio_import(data, model_version ="20230521", mode = "pred", remove_duplicate=None):
    """
    Converts input data into a list of tasks for importing into LabelStudio.

    Args:
        data (list): A list of dictionaries containing the input data for each sentence. Each dictionary contains a
                     'sentence' key with the text of the sentence and a 'result' key with the NER results for that sentence.
        model_version (str, optional): A string representing the version of the NER model used to generate the results.
                                       Default is set to "20230521".
        mode (str, optional): A string indicating the mode of the task. Default is set to "pred".
        remove_duplicate (bool, optional): A boolean indicating whether to remove duplicate entities. Default is set
                                            to None.

    Returns:
        list: A list of tasks that can be imported into LabelStudio for annotation.
    """
    def get_result(data_result):
        """
        Helper function to format NER results for a single sentence into the required format for LabelStudio.

        Args:
            data_result (list): A list of NER results for a single sentence in the format [[start, end, label, text], ...].

        Returns:
            list: A list of NER results formatted for LabelStudio in the format [{'from_name': 'label',
                                                                                 'to_name': 'text',
                                                                                 'type': 'labels',
                                                                                 'value': {'start': start_index,
                                                                                           'end': end_index,
                                                                                           'text': entity_text,
                                                                                           'labels': [label]}}].
        """
        # input format: [[78, 81, 'GPE', '土耳其'], ...]
        # 注意：不支援 multi-label
        results = []
        for idx in range(len(data_result)):
            ent_in_result = {
                "from_name": "label",
                "to_name": "text",
                "type": "labels",
                "value": {
                    "start": data_result[idx][0],
                    "end": data_result[idx][1],
                    "text": data_result[idx][3],
                    "labels": [
                        data_result[idx][2]
                    ]
                }
            }
            results.append(ent_in_result)
        return results

    tasks = []
    for sentence_idx in range(len(data)):
        # 一筆資料
        build_dict = {
            "data": {
                "text": data[sentence_idx]['sentence']
            },
            "predictions": [
                {
                    "model_version": model_version,
                    "result": get_result(data[sentence_idx]['result'][2])
                }
            ]
        }
        tasks.append(build_dict)
    return tasks


    
def labelstudio_output_to_db(data, article_id="", sentence_id=""):
    """
    Converts input format to output format.
    Args:
    input_data (dict): Input data in the given format.
    article_id (str): ID of the article to which the input data belongs.
    sentence_id (int): ID of the sentence in the article to which the input data belongs.
    sentence (str): Sentence in the article to which the input data belongs.
    
    Returns:
    dict: Output data in the given format.
    """
    output = []
    for input_data in data:
        output_data = {"_id": "",
                    "article_id": article_id,
                    "sentence_id": sentence_id,
                    "sentence": input_data['text'],
                    "result": [[], [], []]
        }

        for label in input_data["label"]:
            start = label["start"]
            end = label["end"]
            entity_type = label["labels"][0]
            entity_text = label["text"]
            output_data["result"][2].append([start, end, entity_type, entity_text])
        output.append(output_data)

    return output




def list_to_labelstudio_import(data):
    tasks = []
    for sentence_idx in range(len(data)):
        # 一筆資料
        build_dict = {
            "data": {
                "text": data[sentence_idx]
            },
        }
        tasks.append(build_dict)
    return tasks




#### 以下是轉換所有資料
def get_result_0604(data):
    final = []
    def find_index_by_id(id, result):
        for i in range(len(result)):
            if result[i]['id'] == id:
                return list(range(int(result[i]["value"]['start']), int(result[i]["value"]['end'])))
        raise Exception("ID not found")
    def build_result(tokens, head, tail, label):
        result = {"triplets": [{
                "tokens": tokens, 
                "head": head, 
                "tail": tail, 
                "label": label, 
                "head_id": "", 
                "tail_id": "", 
                "label_id": "", 
                "error": "", 
                "raw": "", 
                "score": 0, 
                "zerorc_included": False
            }]
        }
        return result
    # Iterate over each item in the data
    for item in data:
        # Iterate over each result in the annotations of the current item
        for result in item['annotations'][0]['result']:
            # Check if the result is of type 'relation' and has no labels
            if result['type'] == 'relation':
                head = find_index_by_id(result['from_id'], item['annotations'][0]['result'])
                tail = find_index_by_id(result['to_id'], item['annotations'][0]['result'])
                label = result['labels'][0]
                tokens = [i for i in item['data']['text']]
                new_result = build_result(tokens, head, tail, label)
                final.append(new_result)
                # skip this data
                break
    # Return the modified data
    return final
    


def get_result_RE_Triplets(data):
    final = []
    def find_index_by_id(id, result):
        for i, res in enumerate(result):
            if res['id'] == id:
                return list(range(int(res['value']['start']), int(res['value']['end'])))
        raise Exception("ID not found")
    
    def build_triplet(tokens, head, tail, label, zerorc_included, ner):
        triplet = {
                "tokens": tokens, 
                "head": head, 
                "tail": tail, 
                "label": label, 
                "head_id": "", 
                "tail_id": "", 
                "label_id": "", 
                "error": "", 
                "raw": "", 
                "score": 0, 
                "zerorc_included": zerorc_included,
                "ner": ner
        }
        return triplet
    # Iterate over each item in the data
    for item in data:
        triplets = {"triplets": []}

        ner = {result["value"]["text"]:result["value"]["labels"][0] for result in item['annotations'][0]['result'] if result['type'] == 'labels'}
        for result in item['annotations'][0]['result']:
            
            # Check if the result is of type 'relation' and has no labels
            if result['type'] == 'relation' and result['labels']:
                tokens = list(item['data']['text'])
                head = find_index_by_id(result['from_id'], item['annotations'][0]['result'])
                tail = find_index_by_id(result['to_id'], item['annotations'][0]['result'])
                label = result['labels'][0]
                zerorc_included = False
                new_result = build_triplet(tokens, head, tail, label, zerorc_included, ner)
                triplets['triplets'].append(new_result)

        if triplets['triplets']:
            triplets['triplets'][0]['zerorc_included'] = True
            final.append(triplets)

    # Return the modified data
    return final