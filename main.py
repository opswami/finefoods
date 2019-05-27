from flask import Flask
from flask import Response
from flask import request
import csv
from collections import defaultdict
import re
from nltk.corpus import stopwords
import nltk
import json

app = Flask(__name__)

stopwords_list = stopwords.words('english')

reviews_fp = open("finefoods.txt", "r", encoding="ISO-8859-1")
review_csv=open("finefood.csv",'w')
# review_dict_fp = open("finefood_dict.json", "w")
fieldnames=['productId','userId','profileName','helpfulness','score','time','summary','text']

review_writer = csv.writer(review_csv)
reviews_data_dict = {}

@app.route(r'/api/reviews/processdata/', methods=['GET'])
def process_raw_data():
    '''
    This method will process raw reviews data, create token from review summary and text, and store document
    data in JSON format for further uses
    :return:
    '''
    global tokens_dict
    block_count = 0
    block_data = []
    block_data_dict = {}
    tokens_dict = defaultdict(list)
    for row in reviews_fp.readlines():
        row = row.strip('\n')
        # To read maximum of 100k documents
        if block_count > 100000:
            break
        # documents are separated by a blank row, so on blank row it will add document data with reviews_data_dict
        if row == '':
            id = block_data[0]
            # Adding new document with reviews data
            reviews_data_dict[id] = block_data_dict
            block_data = []
            block_data_dict = {}
            block_count += 1
            continue
        row_data = row.split(':')
        field_value = row_data[1] if len(row_data) == 2 else ''
        # Indexing summary and text data to search on them
        if row_data[0] == 'review/summary' or row_data[0] == 'review/text':
            # Creating tokens from string
            tokens = field_value.split()
            for token in tokens:
                token = re.sub('[^A-Za-z\']+', '', token)
                token = token.lower()
                if token not in stopwords_list:
                    if token in tokens_dict:
                        if block_data[0] not in tokens_dict[token] :
                            tokens_dict[token].append(block_data[0])
                    else:
                        tokens_dict[token] = [block_data[0]]
        block_data.append(field_value.strip())
        block_data_dict[row_data[0]] = field_value.strip()
    # writing review documents data and tokens data in their respective files
    with open('finefood_dict.json', 'w') as outfile:
        json.dump(reviews_data_dict, outfile)
    with open('finefood_tokens.json', 'w') as outfile:
        json.dump(tokens_dict, outfile)

@app.route(r'/api/review/search/')
def process_query():
    '''
    This API will search for the query string given in request parameter
    :return: All relative document for given querystring
    '''
    q = request.args.get('q', None)
    if not q:
        return Response(json.dumps({"status": "ERROR", "message": "Query string is not present in Request"}), status=400)
    # loading review document data and tokens data from file into memory
    reviews_fp = open('finefood_dict.json', 'r')
    tokens_fp = open('finefood_tokens.json', 'r')
    try :
        reviews_data_dict = json.load(reviews_fp)
        tokens_dict = json.load(tokens_fp)
    except Exception as e:
        print(e)
        return Response(json.dumps({"status" : "ERROR", "message":"Reviews Data not present"}), status=404)
    if not reviews_data_dict or not tokens_dict:
        return Response(json.dumps({"status": "ERROR", "message": "Reviews Data not present"}), status=404)
    # spliting string into words and removing stopwords
    query_words = q.split()
    query_words = list(filter(lambda x: x not in stopwords_list, query_words))
    num_words = len(query_words)
    if num_words == 0:
        return Response(json.dumps({"status": "ERROR", "message": "Please provide valid Query String"}), status=400)
    doc_ids = []
    doc_word_score = {}
    # Getting all the document Ids related to given query string words
    for word in query_words:
        doc_ids.extend(tokens_dict.get(word, []))
    # Calculating score for all relavent document Ids
    for doc_id in doc_ids:
        if doc_id in doc_word_score:
            doc_word_score[doc_id] += 1*float(reviews_data_dict[doc_id]['review/score'])
        else :
            doc_word_score[doc_id] = 1*float(reviews_data_dict[doc_id]['review/score'])
    doc_word_score = sorted(doc_word_score.items(), key=lambda v:v[1], reverse=True)[0:19]
    doc_word_score = dict(list(map(lambda x:(x[0],x[1]/num_words), doc_word_score)))
    # Getting result document data for relavent document Ids
    result={}
    for doc_id, val in doc_word_score.items():
        result[doc_id] = reviews_data_dict[doc_id]
        result[doc_id]['score'] = val
    return Response(json.dumps(result), status=200, )


if __name__ == '__main__':
    # Processing raw reviews data file to create token and store them
    # process_raw_data()
    # downloading stop words from nltk library once only
    # nltk.download('stopwords')
    app.run(host='127.0.0.1',port='8000',debug=True)

