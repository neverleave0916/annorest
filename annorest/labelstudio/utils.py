def remove_entity(data, remove = ["TIME", "LAW", "LANGUAGE", "EVENT-MandA"]):
    def remove(label_list, remove):
        filtered_label_list = []
        for id in range(len(label_list)):
            if label_list[id]['labels'][0] in remove:
                continue
            else:
                filtered_label_list.append(label_list[id])
        return filtered_label_list

    for id in range(len(data)):
        label_list = data[id]['label']
        label_list = remove(label_list, remove)
        data[id]['label'] = label_list
    return data

def split_to_sentence(data, delimiter = "。"):
    result = []
    for single_doc in data:
        # text_splited = single_doc['text'].split('，')
        sep= delimiter
        text_splited = [x+sep for x in single_doc['text'].split(sep)]
        text_splited[-1] = text_splited[-1].strip(sep)
        # print(re.findall('.*?[.!\?，。,]', single_doc['text']))
        # text_splited = re.findall('.*?[.!\?]', single_doc['text'], flags=re.DOTALL)
        label_splited = []
        
        index = 0
        for sentence in text_splited:
            label_splited = single_doc['label'][index:index+len(sentence)]
            index = index + len(sentence)
            
            concat = {
                'text': list(sentence),
                'label': label_splited
            }
            if len(concat['text']) == 0:
                continue
            if concat['label'][0].startswith('I-'):
                continue
            result.append(concat)
    return result