###########################################################
### Script to download weibo POIs                       ###
### Jianghao Wang,                                      ###
### wangjh@lreis.ac.cn                                  ###
### August 15, 2014  v2                                 ### 
### Dec. 16, 2014  v2.1                                 ### 
###########################################################
### Readme
# - change OS, month, starttime, endtime, access taken, and items before running
# - make sure curl has been installed before running it

# -----------------------
# initial
# -----------------------
rm(list=ls())
options(stringsAsFactors=FALSE)

library(rjson)
library(jsonlite)
library(plyr)
library(dplyr)
library(data.table)

# I have test it on Win, Linux, Mac
# change work dir 
OS <- "Mac"
if (OS == "Win") setwd("G:/Project/Weibo/geotagged/")
if (OS == "Linux"){
  setwd("/root/project/geotagged/")
  system("echo 1 > /proc/sys/vm/drop_caches")
}
if (OS == "Linux1") setwd("/wps/home/wangjh/project/geotagged/")
#if (OS == "Mac") setwd("/Users/wangjianghao/Desktop/geotagged/")
if (OS == "Mac") setwd("/Users/debnil/Documents/Stanford/Senior/Research/SummerChina/Repo/Scrapers")

# load functions
source(file="fetch_weibo_APIs_fun_v2.1.R")
# load searching grid with a spatial resolution of 0.05 * 0.05
# you make change the spatial resolution as you need
load("Grid_CN_WGS84_0.05d.Rdata")
grid$Id <- seq(1,nrow(grid),1)

# load initial blank data frame
# you would better using GBK encoding because of Chinese characters
fddf.blank <- read.csv("fddf_null.csv", fileEncoding="gbk")

# initial input parameters
month <- "CN-20160725"  # I download it every month
range <- 4000; sort=0; count=50; page=1; offset=1
starttime <- as.numeric(strptime("2016-07-25 00:00:01", "%Y-%m-%d %H:%M:%S"))
endtime <- as.numeric(strptime("2016-07-25 23:59:59", "%Y-%m-%d %H:%M:%S"))
# change access_token
#access_token <- "2.00X_6UXFI7nSsD008f8258ee0uqs6P"
access_token <- "2.00X_6UXFFwdXVBaaf98ddc1daYn7UD"
# access_token <- "2.00X_6UXF0GqvuGca49b109136M4UTC"
# access_token <- "2.00X_6UXFQ9y5QD678d6a30e80YnACX"
# access_token <- "2.00X_6UXFwXYrFD089496f37cRKW2TB"

# set output dir
outputwd <- ifelse(OS == "Win",  paste0("F:/geotagged/Rdata/", month, "/"), paste0("Rdata/", month, "/"))
dir.create(outputwd, recursive = TRUE, showWarnings = FALSE)
# I store results in every 10000 grids in each folder
items <- 1:ceiling(nrow(grid)/10000)

# for each items
for  (item.index in items){
  # load functions again because you may update cookies
  source(file="fetch_weibo_APIs_fun_v2.1.R")
  
  item <- item.index
  # set output folder name
  folder <- ifelse(nchar(item) == 1, 
                   paste0("0",as.character(item),"e4"), 
                   paste0(as.character(item),"e4"))
  
  # create output folders
  dir.create(paste0(outputwd, folder), showWarnings=TRUE, recursive=TRUE)
  
  # set indexes
  if((10000*item) < nrow(grid)) {
    indexes <- (10000*(item-1)+1):(10000*item)
  } else {
    indexes <- (10000*(item-1)+1):nrow(grid)
  }
  
  start <- Sys.time()
  for (index in indexes){
    # set parameters
    grid.index <- grid[index, ]
    id  <- grid.index[, "Id"]
    lon <- grid.index[, "central_X"]
    lat <- grid.index[, "central_Y"]
    top    <- grid.index[, "top"]
    bottom <- grid.index[, "bottom"]
    right  <- grid.index[, "right"]
    left   <- grid.index[, "left"]
      
    # set output file
    output.rdata <- paste0(outputwd, folder, "/", index,".Rdata")
    
    if(!file.exists(output.rdata)){
      start.time <- Sys.time()
      
      # get total num in this grid
      curl.string <- setCurl(lat=lat, lon=lon, range=range,
                             sort=sort, count=1, page=1, offset=offset, 
                             starttime=starttime, endtime=endtime, 
                             access_token=access_token)
      json <- curlJSON(curl.string = curl.string)
      total.num1 <- getTotalNumber(json = json, max = 8000, first = TRUE)
      cat(item, "-", index, ":", total.num1, "\n")
      
      # - case 1: when 0.05 grid less than 8000 weibos
      if (total.num1 <= 8000 & total.num1 > 0){
        page.num <- as.integer(total.num1 / 50) + 1
        if (page.num > 0) {
          if(page.num > 1) pb <- txtProgressBar(min=1, max=page.num, initial=1, style=3)
          listofDF <- NULL
          for ( page.index in 1:page.num){
            if (page.num > 1) setTxtProgressBar(pb, page.index)
            curl.string <- setCurl(lat=lat, lon=lon, range=range,
                                   sort=sort, count=count, page=page.index, offset=offset, 
                                   starttime=starttime, endtime=endtime, 
                                   access_token=access_token)
            json <- curlJSON(curl.string = curl.string)
            df <- try(json2df(json = json, fddf.blank = fddf.blank), silent=TRUE)
            if(class(df) != "try-error"){
              listofDF[[page.index]] <- df
            }else{
              listofDF[[page.index]] <- fddf.blank
            }
          }
          #rbind.fill data.frame
          if (page.num > 1){
            fddf <- do.call("rbind.fill", listofDF)
          } else {
            fddf <- listofDF[[1]]
          }
        }
      } # end of case 1
        
        
      # - case 2: when 0.05 grid large than 8000 weibos
      if(total.num1 >= 8000){
        if(total.num1 < 40000) {
          grid.sub <- setGrid(left = left, bottom = bottom, right = right,
                              top = top, resx = 0.01, resy = 0.01)
          range1 <- 800
        }
        if(total.num1 >= 40000) {
          grid.sub <- setGrid(left = left, bottom = bottom, right = right,
                              top = top, resx = 0.005, resy = 0.005)
          range1 <- 400
        }
        ListofDataFrame <- NULL
        for(sub.index in 1:nrow(grid.sub)){
          # get total num in this grid
          curl.string <- setCurl(lat=grid.sub[sub.index, "central_Y"], lon=grid.sub[sub.index, "central_X"], range=range1,
                                 sort=sort, count=1, page=1, offset=offset, 
                                 starttime=starttime, endtime=endtime, 
                                 access_token=access_token)
          json <- curlJSON(curl.string = curl.string)
          total.num <- getTotalNumber(json = json, max = 8000, first = FALSE)
          cat("         ...........", sub.index, ": ", total.num, "\n")
          
          # get json data
          if (total.num > 0){
            page.num <- as.integer(total.num / 50) + 1
            if (page.num > 0) {
              if(page.num > 1) pb <- txtProgressBar(min=1, max=page.num, initial=1, style=3)
              listofDF <- NULL
              for ( page.index in 1:page.num){
                if (page.num > 1) setTxtProgressBar(pb, page.index)
                curl.string <- setCurl(lat=grid.sub[sub.index, "central_Y"], lon=grid.sub[sub.index, "central_X"], range=range1,
                                       sort=sort, count=count, page=page.index, offset=offset, 
                                       starttime=starttime, endtime=endtime, 
                                       access_token=access_token)
                json <- curlJSON(curl.string = curl.string)
                df <- try(json2df(json = json, fddf.blank = fddf.blank), silent=TRUE)
                if(class(df) != "try-error"){
                  listofDF[[page.index]] <- df
                }else{
                  listofDF[[page.index]] <- fddf.blank
                }
              }
              #rbind.fill data.frame
              if (page.num > 1){
                fddf <- do.call("rbind.fill", listofDF)
              } else {
                fddf <- listofDF[[1]]
              }
            } # end of if page.num
            ListofDataFrame[[sub.index]] <- fddf
          } else{
            ListofDataFrame[[sub.index]] <- fddf.blank
          }
        } # end of for sub.index
        #rbind.fill data.frame
        fddf <- do.call("rbind.fill", ListofDataFrame)
      } # end of case2
       
      if (total.num1 > 0){
        # remove duplicates
        fddf <- fddf[!duplicated(fddf$id),]
        # remove un-geotagged-weibo
        fddf <- fddf[!(is.na(fddf$geo.coordinates1) & is.na(fddf$geo.coordinates2)),]
        # remove weibo outof this grid
        fddf <- filter(fddf, geo.coordinates1 >= bottom, geo.coordinates1 <= top, 
                       geo.coordinates2 >= left, geo.coordinates2 <= right)
        
        # export data
        if(nrow(fddf) > 0){
          save(fddf, file = output.rdata)
          cat("          ..... Export. ", nrow(fddf), "\n")
          rm(fddf)
        }
        
        # cat infomation
        if(total.num1 > 1e2){
          cost.time <- format(difftime(Sys.time(), start.time, units="mins"), digits=2)
          cat("          ..... Cost time:", cost.time, "\n")
        }
      }
    } else {
      cat(item, "-", index, ":", "          ..... File exist!\n")
    }# end file.exist
  } # end for index
  cat("Started!!!",as.character(start), "\n")
  cat("Finished!!!",as.character(Sys.time()), "\n")
} # end of if item

# End of script

