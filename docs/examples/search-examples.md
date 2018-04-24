Read the [troubleshooting searches for beginners doc](https://www.elastic.co/blog/found-beginner-troubleshooting).  It’s not too long.  It will help explain some of the ***weirdness*** that you may encounter when the searches don't return what you thought it would. 

## Example 1
Get the latest 20 entries (by default it only shows the last 5) for any dns events and sort by the received\_at value in descending order (newest first).  

```json
GET sfn-dns-event/_search
{
  "size": 20, 
  "query": {
    "match_all": {}
  },
  "sort": [
    {
      "received_at": {
        "order": "desc"
      }
    }
  ]
}
```
**Why sort?** 
By default, ES “weighs” each response with a relevancy score and you get the most heavily weighted response first.  This gives us the results ordered by the score, not by the order in which we added them.  ES does have “Search” in the name, so this makes sense – it actually performs searches on relevant data, not just grabbing stuff dumped to the DB.  So, we just have to order it by one of the date fields.  

**Why use received\_at vs msg\_gen_time or the @timestamp value?**
The received_at timestamp is the true time that we received the event.  The msg\_gen\_time can be "faked" to be something than it really is - i.e. we want to load a lot of fake data for demo purposes and generate dates that would make ordering it by that value irrelevant, or at least not what you would think you would get back.  The @timestamp value is a reformatting of the msg\_gen\_time value and that
is done by Logstash at creation time. 

## Example 2
Get everything (notice we are not searching on a particular index – so it could be sfn-dns-event, sfn-iot-event, etc) and match on both threat_category having the word dns in it AND processed is 0
```json
GET _search
{
  "query":{
    "bool": {
      "must": [
        {"match": {"threat_category": "dns"}},
        {"match": {"processed":"0"}}
     ]
    }
  },
  "sort": [
    {
      "received_at": {
        "order": "desc"
      }
    }
  ]
}
```



## Example 3
Looking only in sfn-dns-event indexed documents, return unprocessed items that match the threat category having the word “wildfire” in it.  Notice that they actually have “dns-wildfire” in the results.  If you were to put dns-wildfire in the search, you would get everything with either dns OR wildfire in the text.  Why?  Since, by default, ES stores everything as a string, it uses a text analyzer to do the indexing of all the words.  It gets rid of punctuation and each word becomes an indexed item.  So in this case, it would remove the “-“ and index both dns and wildfire.  So, if we had “dns-wildfire” in the search, the text analyzer for the search would also remove the “-“ and the search would really be “show me anything with dns OR wildfire in it” – thus it would match all records that have “dns” and “dns-wildfire” in it.  
```json
GET sfn-dns-event/_search
{
  "query": {
    "bool": {
      "must": [
        {"match": {"threat_category": "wildfire"}},
        {"match": {"processed": "0" }}
      ]
    }
  },
  "sort": [
    {
      "received_at": {
        "order": "desc"
      }
    }
  ]
}
```



## Example 4
Delete all documents in the index (zero it out essentially)
```json
POST sfn-dns-event/_delete_by_query 
{
  "query" : {
     "match_all": {}
  }
}
```

If you have search examples that you believe would benefit here, please add them and submit a pull request.  