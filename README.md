#Tasty Search!
Simple Restful api for searching best related reviews among gourmet food reviews data

# API Implementation Detail
## Frameworks
- **Python**
- **Flask Framework**

## Food Reviews Data
All Food reviews data are stores in a file names finefoods.txt

## Food Reviews scoring 
>Scoring of Reviews is based on the number of keyward (query string keywords) matching in summary and text field of every 
review document,
let number of valid words in querystring = n,
number of matched words in any documents = k,
score = k/n

final score for every document will be calculated by using internal score of the query (0-5)
let internal score of any review document = r
final_score = k/(n*r)

## Processing Raw Reviews Data
- Raw reviews data are stored in finefoods.txt file, Every review is separated by a blank line
- Storing All Reviews data in a dictionary as JSON format
- Dumping all these reviews data in finfoo_dict.json file for further user
- For every review document creating index for search fields

## Indexing of search fields
Using Inverted indexing to store search fields text 
- spliting string in individual words(tokens)
- removing all stop-words from these tokens
- removing all special characters from these tokens
- storing all the tokens in dictionary as key and value will be document Ids in which that token is present 

# To Run/Start App
- Create Virtual environment
- install all requirement described in requirements.txt using pip
  pip install -r requirements.txt
- run server using 
  python main.py
- API endpoint for query search - "/api/review/search/?q=abc"
  
### Response
> Error Response

{

    'status':'ERROR',
    'message' : 'Some Error Message'
}

> Success Response

{
    
    {
        '<doc-id>': 
            {
                "product/productId" : string,
                "review/userId" : string,
                "review/profileName" : string,
                "review/helpfulness" : float,
                "review/score" : float,
                "review/time" : timestamp,
                "review/summary" : string,
                "review/text" :string,
                "score":float
            }
    }
}