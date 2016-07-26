rm(list=ls())
options(stringsAsFactors=FALSE)

library(jsonlite)
library(plyr)

# --------------------------------------------------------------
# setCurl
#   - reference: http://open.weibo.com/wiki/2/place/nearby_timeline
# --------------------------------------------------------------
setCurl <- function(lat=39.989385149193, lon=116.46606445312, range=1000,
                    sort=1, count=50, page=1, offset=1, 
                    starttime=1388505600, # 2014-01-01 00:00:00
                    endtime=1404144000, # 2014-07-01 00:00:00
                    access_token="2.00X_6UXFFwdXVBaaf98ddc1daYn7UD"){
  
  prefix <- "curl \"http://open.weibo.com/tools/aj_interface.php\" -H \"Cookie: USRHAWB=usrmdinst_9; _s_tentry=-; Apache=2114088018715.4697.1469480746783; SINAGLOBAL=2114088018715.4697.1469480746783; ULV=1469480746796:1:1:1:2114088018715.4697.1469480746783:; SCF=Ail4JcnmGvtOUiNyBM5KBMZaiWML29tQdkHy53rxBviqxGwd9909IymxsSZ8jN7gHsmPfNTV58ijBYjj_-nqu7g.; SUB=_2A256kg8eDeTxGeNO7FcU8y7PwjWIHXVZ5mfWrDV8PUJbmtBeLWz2kW9OJaUfB7R3QH5-K_DbAN_OvUSEIQ..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWDN.RkNZ2J8aDl-cExqfNN5JpX5K2hUgL.Fo-7S0-fe0501K.2dJLoI7pQ9gpjdNUydJU3Ih2t; SUHB=0cS3MEYrGkYfxX; SSOLoginState=1469480783; un=hellowangjh1@126.com\" -H \"RA-Sid: 9FE26E1C-20141205-075022-3ab5e4-b42a2e\" -H \"Origin: http://open.weibo.com\" -H \"Accept-Encoding: gzip, deflate\" -H \"Accept-Language: zh-CN,zh;q=0.8,en;q=0.6\" -H \"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36\" -H \"Content-Type: application/x-www-form-urlencoded\" -H \"Accept: */*\" -H \"Referer: http://open.weibo.com/tools/console?uri=place/nearby_timeline&httpmethod=GET&key1=lat&value1=39.98437&key2=long&value2=116.30987\" -H \"X-Requested-With: XMLHttpRequest\" -H \"Connection: keep-alive\" -H \"RA-Ver: 2.8.0\" --data \"api_url=https%3A%2F%2Fapi.weibo.com%2F2%2Fplace%2Fnearby_timeline.json&request_type=get&request_data="
  
  suffix <- "&_t=0\" --compressed"
  url <- paste0(prefix, 
                "lat\"%\"3D", lat, 
                "\"%\"26long\"%\"3D", lon, 
                "\"%\"26range\"%\"3D", range,
                "\"%\"26sort\"%\"3D", sort, 
                "\"%\"26count\"%\"3D", count, 
                "\"%\"26page\"%\"3D", page, 
                "\"%\"26offset\"%\"3D", offset, 
                "\"%\"26starttime\"%\"3D", starttime, 
                "\"%\"26endtime\"%\"3D", endtime, 
                "\"%\"26access_token\"%\"3D", access_token, 
                suffix)
  return(as.character(url))
}

# --------------------------------------------------------------
# curlJSON: curl json data for given time if it is failed
# --------------------------------------------------------------

curlJSON <- function(curl.string){
  repeat.num <- 0
  json <- NULL
  repeat {
    repeat.num <- repeat.num + 1
    json <- try(paste(system(curl.string, intern=TRUE, ignore.stderr=TRUE),
                      collapse=""),
                silent = TRUE)
    if (class(json) != "try-error") {
      break
    } else {
      cat("Warning! Failed to curl for web, try for", repeat.num, "times.\n")
      Sys.sleep(2)
    }
    if (repeat.num > 100) {
      cat("Warning! Failed to curl for web, try for", repeat.num, "times.\n")
      break
    }
  } # end of repeat
  return(json)
}

curl <- setCurl(lat=39.989385149193, lon=116.46606445312, range=1000,
                    sort=1, count=50, page=1, offset=1, 
                    starttime=1388505600, # 2014-01-01 00:00:00
                    endtime=1404144000, # 2014-07-01 00:00:00
                    access_token="2.00X_6UXFFwdXVBaaf98ddc1daYn7UD")



json <- curlJSON(curl)
test <- fromJSON(json)
test$retjson$statuses$user$id
