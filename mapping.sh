#!/usr/bin/env bash

curl -XPOST 'http://127.0.0.1:9200/logservice'

curl -XPOST 'http://127.0.0.1:9200/logservice/_mapping/logs' -d '
{
    "logs" : {
        "properties" : {
            "identifier"        : { "type" : "string", "index":"not_analyzed" },
            "log_type"          : { "type" : "string", "index":"not_analyzed" },
            "source_user_id"    : { "type" : "string", "index":"not_analyzed" },
            "log_date"          : { "type" : "date", "format" : "yyyy-MM-dd HH:mm:ss" } ,
            "history_date"      : { "type" : "date", "format" : "yyyy-MM-dd HH:mm:ss" } ,
            "source_log_date"   : { "type" : "date", "format" : "yyyy-MM-dd HH:mm:ss" }
        }
    }
}
'
curl -XGET 'http://127.0.0.1:9200/logservice/logs/_mapping?pretty=1'