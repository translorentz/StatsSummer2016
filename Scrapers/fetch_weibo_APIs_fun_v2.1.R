# main changes in v2.1
# - change sort = 1, sort by the distance to the central
# - set the three time of resizing the grid is total.num > 8000

# --------------------------------------------------------------
# This program is based on the `script_fetch/fetch_weibo_APIs.R`
#   the main revised is to improve the efficience of codes.

# reference: http://open.weibo.com/tools/console?uri=place/nearby_timeline&httpmethod=GET&key1=lat&value1=39.98437&key2=long&value2=116.30987
# user.name: hellowangjh1@126.com
# passwords: 422
# --------------------------------------------------------------

# --------------------------------------------------------------
# setCurl
#   - reference: http://open.weibo.com/wiki/2/place/nearby_timeline
# --------------------------------------------------------------
setCurl <- function(lat=39.989385149193, lon=116.46606445312, range=4000,
                    sort=1, count=50, page=1, offset=1, 
                    starttime=1388505600, # 2014-01-01 00:00:00
                    endtime=1404144000, # 2014-07-01 00:00:00
                    access_token="2.00X_6UXFwXYrFD089496f37cRKW2TB"){
  
  prefix <- "curl \"http://open.weibo.com/tools/aj_interface.php\" -H \"Cookie: SINAGLOBAL=4821667827200.145.1415333137002; myuid=5075530399; UOR=,,login.sina.com.cn; APPB=usrmdinst_11; _s_tentry=-; Apache=3402387315873.0566.1418196664075; ULV=1418196664083:5:1:1:3402387315873.0566.1418196664075:1415764155245; SUS=SID-5075530399-1418196683-GZ-o5j1y-ce2e09d35c1e8c5b1fdd631fa7868e41; SUE=es%3D9e735132bf9b1d2c7531c574cc7aa2f8%26ev%3Dv1%26es2%3Da4c85ccbd7c50772a11584afe7b66d50%26rs0%3DkYha9vGXa%252FT23wuf3rYI3fP9z80E%252FsRxrUeTOFWr39u7RL5eumtAodrBdMb66U8a3lheYqBRG9D71Q7H4qySA8dNUhJzUPL07f3CdY69INXJ0vgLu8sY%252F43e%252FTBRJzuTOtK%252FtPk4v6rIDNIrjHa5DMSlbIZhm4rbzSRW9%252FTBswk%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1418196683%26et%3D1418283083%26d%3Dc909%26i%3D8e41%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26uid%3D5075530399%26name%3Dhellowangjh1%2540126.com%26nick%3Dhellowangjh1%26fmp%3D%26lcp%3D; SUB=_2A255g4abDeTxGeNO7FcU8y7PwjWIHXVa-y7TrDV8PUNbuNBuLVjwkW-SR7yRMTC95nvSeFk4w_JU-khrHA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWDN.RkNZ2J8aDl-cExqfNN5JpX5K2t; ALF=1449732683; SSOLoginState=1418196683; un=hellowangjh1@126.com\" -H \"RA-Sid: 9FE26E1C-20141205-075022-3ab5e4-b42a2e\" -H \"Origin: http://open.weibo.com\" -H \"Accept-Encoding: gzip, deflate\" -H \"Accept-Language: zh-CN,zh;q=0.8,en;q=0.6\" -H \"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36\" -H \"Content-Type: application/x-www-form-urlencoded\" -H \"Accept: */*\" -H \"Referer: http://open.weibo.com/tools/console?uri=place/nearby_timeline&httpmethod=GET&key1=lat&value1=39.98437&key2=long&value2=116.30987\" -H \"X-Requested-With: XMLHttpRequest\" -H \"Connection: keep-alive\" -H \"RA-Ver: 2.8.0\" --data \"api_url=https%3A%2F%2Fapi.weibo.com%2F2%2Fplace%2Fnearby_timeline.json&request_type=get&request_data="
  
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


# --------------------------------------------------------------
# json2df: json to data.frame
# input : json characters
# output: data.frame
# --------------------------------------------------------------
json2df <- function(json, fddf.blank){
  if(!is.null(json) & nchar(json) > 10){
    fdjson <- try(rjson::fromJSON(json, unexpected.escape = "skip"), silent=TRUE)
    # if rjson is failed using jsonlite, I have tested it
    if (class(fdjson) == "try-error") fdjson <- try(jsonlite::fromJSON(json, unexpected.escape = "skip"), silent=TRUE)
    if (class(fdjson) != "try-error"){
      fd.statuses <- fdjson$retjson$statuses
      
      # json to df      
      listofDF <- lapply(1:length(fd.statuses), function(i){
        temp <- try(data.frame(t(unlist(fd.statuses[[i]])), 
                               stringsAsFactors=FALSE, row.names=NULL), 
                    silent=TRUE)
        if(class(temp) != "try-error"){
          data <- temp
        } else {
          data <- fddf.blank
          cat("..........fd.statuses[[i]] is Error!\n")
        }
        return(data)
      })
      
      #rbind.fill data.frame
      if (length(fd.statuses) > 1){
        fddf <- do.call("rbind.fill", listofDF)
      } else {
        fddf <- listofDF[[1]]
      }
      fddf <- rbind.fill(fddf, fddf.blank)
      return(fddf)
    } else {
      cat("..........JSON is not available \n")
      fdjson <- NULL
      return(fddf.blank)
    }
  } else {
    cat("..........JSON is not available \n")
    return(fddf.blank)
  } # end of else
}


# --------------------------------------------------------------
# get total number of weibo
# --------------------------------------------------------------
getTotalNumber <- function (json, max=8000, first=TRUE) {
  total.num <- 0L
  if(!is.null(json) & nchar(json) > 10){
    fdjson <- try(rjson::fromJSON(json, unexpected.escape = "skip"), silent=TRUE)
    if (class(fdjson) == "try-error") fdjson <- try(jsonlite::fromJSON(json, unexpected.escape = "skip"), silent=TRUE)
    if (class(fdjson) !="try-error"){
      total.num <- try(fdjson$retjson$total_number, silent=TRUE)
      total.num <- ifelse(class(total.num) != "try-error" & !is.null(total.num), total.num, 0)
      if(!first) total.num <- ifelse(total.num > max, max, total.num)
    }
  }
  return (total.num)
}


#--------------------------
# setGrid: set the grid by given boundary and resolutin
# -------------------------
setGrid <- function(left=108.5, bottom=18.0, right=111.5, top=20.5, resx=0.01, resy=0.01){
  gridx <- seq(from=left, to=right, by=resx)
  gridy <- seq(from=bottom, to=top, by=resy)
  numx <- length(gridx) - 1
  numy <- length(gridy) - 1
  numt <- numx * numy
  left <- rep(gridx[seq(numx)], each=numy)
  bottom <- rep(gridy[seq(numy)], time=numx)
  right <- left + resx
  top <- bottom + resy
  set.grid <- data.frame(left=left, bottom=bottom, right=right, top=top)
  set.grid$central_X <- (set.grid$left + set.grid$right) / 2
  set.grid$central_Y <- (set.grid$bottom + set.grid$top) / 2
  return(set.grid)
}


