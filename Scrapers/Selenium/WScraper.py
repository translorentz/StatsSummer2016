#!/usr/bin/env python
# -*- coding: utf-8 -*-

import selenium
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import sys  
import re
import pickle
import codecs
import math
import contextlib
import selenium.webdriver.support.ui as ui
from pyvirtualdisplay import Display
from selenium import webdriver
from datetime import datetime
from datetime import date
import json
#reload(sys)  
#sys.setdefaultencoding('utf-8')


class w_scraper(object): 
    def login(self,credentialFile):
        # Open new window for Chrome, used for testing
        self.page = webdriver.Chrome()
        self.page.get("http://weibo.com/login.php") # load the login page
        time.sleep(5)
        
        # Read in account username and password
        for line in credentialFile:
            username,password = line.split(",")
            
        #self.page.get("http://weibo.com/login.php#_loginLayer_1468518776979")
        #time.sleep(2)
        
        # Logs into account
        # Login button option
        login_button = self.page.find_element_by_xpath("//body/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/ul[1]/li[3]/a")#("//body/div[1]//ul[@class='gn_login_list']/li[3]/a")#("//body/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/ul[1]/li[3]/a")
        login_button.click()
        time.sleep(3)
        
        self.page.get("http://weibo.com/login.php#_loginLayer_1468518776979")
        time.sleep(3)
        
        # Sign in with username option
        email_button = self.page.find_element_by_xpath("//body/div[3]/div[2]/div[3]/div[1]/a[2]")
        email_button.click()
        time.sleep(5)
        
        # Enter Username
        username_box = self.page.find_element_by_xpath("//body/div[3]/div[2]/div[3]/div[3]/div[1]/input")
        username_box.send_keys(username)
        
        # Enter password
        password_box = self.page.find_element_by_xpath("//body/div[3]/div[2]/div[3]/div[3]/div[2]/input")
        password_box.send_keys(password)
        time.sleep(1)
        
        # Hit Enter button
        password_box.send_keys(Keys.ENTER)
        #enter_button = self.page.find_element_by_xpath("//body/div[3]/div[2]/div[3]/div[3]/div[6]/a")
        #enter_button.click()
        time.sleep(4)
        self.page.get('http://weibo.com/u/2407651573')
        time.sleep(4)
  
    def getFollowers(self):
        followers = list()
        # Open the file that contains the list of account ID numbers
        # for line in open('actual_ids.txt', 'r'):
        # account_url = ('http://weibo.com/u/' + line)
        
        #self.page.get(account_url) # Go to specific account homepage

        # Click to go to followers page
        follow_button = self.page.find_element_by_xpath("//body/div[1]//td[@class='S_line1'][2]/a/strong[@class='W_f18']")
        follow_button.click()

        time.sleep(2)
        # print out followers on that page
        html_list = self.page.find_element_by_css_selector("ul[class='follow_list']")
        items = html_list.find_elements_by_tag_name("li")
        for item in items:
            text = item.text
            followers.append(text)
            #print text
            
        # Figure out how many pages of followers there are
        total_pages = self.page.find_element_by_xpath("//body/div[1]//a[@class='page S_txt1'][last()]")
        totPage = int(total_pages.get_attribute('text'));
        time.sleep(2)
        
        # Keep clicking on next button in order to get all the followers
        for x in range(1, totPage):
            # wait for the page to completely load by looking for presence of HTML element of class 'page next S_txt1 S_line1'
            #try:
            ui.WebDriverWait(self.page,10).until(lambda page: page.find_element_by_xpath("//body/div[1]//a[@class='page next S_txt1 S_line1']"))
            self.page.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.page.find_element_by_xpath("//body/div[1]//a[@class='page next S_txt1 S_line1']").click() # next button
            time.sleep(2)
            html_list = self.page.find_element_by_css_selector("ul[class='follow_list']")
            items = html_list.find_elements_by_tag_name("li")
            for item in items:
                text = item.text
                followers.append(text)
        return followers
                #print text
    '''        
            except NoSuchElementException:
                try: 
                    self.page.navigate().refresh();
                    ui.WebDriverWait(self.page,10).until(lambda page: page.find_element_by_xpath("//body/div[1]//a[@class='page next S_txt1 S_line1']"))
                    self.page.find_element_by_xpath("//body/div[1]//a[@class='page next S_txt1 S_line1']").click() # click next button
                    time.sleep(2)
                    html_list = self.page.find_element_by_css_selector("ul[class='follow_list']")
                    items = html_list.find_elements_by_tag_name("li")
                    for item in items:
                        text = item.text
                        followers.append(text)
                        print text
                except Exception as e:
                    print "Failed to find followers - please check HTML or try again. " + str(e)
    '''

                
    # getAccount collects all the post data for a given account ID.  
    # end_date is a datetime object cutoff date for scraping (collect all posts after this date)
    def getAccount(self, num_pages_to_scrape = 0): #(self, base_url, end_date, num_pages_to_scrape = 0):
        account_data = dict()
        # base_url = "http://weibo.com/u/" + str(base_url)
        base_url = "http://weibo.com/u/2407651573?page=1&is_all=1#_0"
        # Go to first page of the account 
        self.page.get(base_url)
        #self.page.find_element_by_xpath("//body//a[@action-type='select_year']").click()
        # print "Starting Account: %s" % str(base_url)
        
        try:
            # Wait for the account self.page to load by looking for the presence of an HTML element of class 'tb_counter'
            ui.WebDriverWait(self.page,10).until(lambda page: page.find_element_by_xpath("//body//a[@action-type='select_year']"))
            # Collect the number of statuses posted by the account. The labels for this HTML class can change - if you get an error double chekc the weibo page. 
            counts = self.page.find_element_by_xpath("//body/div[1]//td[@class='S_line1'][3]/a/strong").text
            #counts = self.page.find_element_by_class_name('tb_counter').find_elements_by_class_name("S_line1")
            account_data['status_counts'] = int(counts)
        except NoSuchElementException:
            try: 
                #print ("tried")
                self.page.get("http://weibo.com/u/2407651573?page=1&is_all=1#_0") 
                ui.WebDriverWait(self.page,20).until(lambda page: page.find_element_by_xpath("//body//a[@action-type='select_year']"))
                counts = self.page.find_element_by_xpath("//body/div[1]//td[@class='S_line1'][3]/a/strong").text
                account_data['status_counts'] = int(counts)
            except Exception as e:
                print "Failed to find counts for this account - please check HTML or try again. " + str(e)
            return
        print "Number of posts: %d" % account_data['status_counts']
        
    
        # weibo splits a user's timeline into pages, with each self.page containing 45 posts. 
        numpages = int(math.ceil(account_data['status_counts']/45.0)) 
        print numpages
        if (num_pages_to_scrape == 0):
            num_pages_to_scrape = numpages
        
        account_data['posts'] = list() # the list object in account_data (where each element is a post)
        # Cycle through each self.page in the account and collect the posts from that self.page. 
        for p in range(1,numpages+1):
            # If we can't or don't need to collect any more posts from this account, getPosts() will return False
            if (p > num_pages_to_scrape):
                break
            print "\t Account %s, Page (%d/%d)" % (base_url, p,numpages)
            if (self.getPosts(base_url,p,account_data) == False):  #,end_date) == False):
                break
        return account_data
        
    
    
    # Gets the posts from a self.page of an account. Adds these posts to account_data
    def getPosts(self,base_url, pageNum, account_data): #, account_data): #,end_date):
        print "fetching: " + base_url+ str(pageNum) #"?is_all=1&page=" + str(pageNum),
        self.page.get(base_url+ "?is_all=1&page=" + str(pageNum)) # Navigate to the self.page of the account 
        
        # Wait for the self.page to successfully load by checking for the presence of the "WB_detail" HTML element. If 10 seconds passes 
        # we reload the self.page and try again. If we try 4 or more times we abort this account. 
        timesTried = 0 
        while True:
            try:
                timesTried = timesTried + 1
                ui.WebDriverWait(self.page,10).until(lambda page: page.find_elements_by_class_name("WB_detail"))
                break
            except NoSuchElementException:
                if (timesTried < 4):
                    self.page.get(base_url + "?is_all=1&page=" + str(pageNum))
                    pass
                else:
                    account_data = None
                    return False
                
        print ("done loading")
                
        # Though each page of a user's timeline contains 45 posts, weibo initially only displays 15. In order to get 
        # get the other posts we have to simulate scrolling down on the page. Everytime we scroll to the bottom weibo
        # loads another 15. We thus scroll twice to get the other 30 posts. Everytime we scroll to the bottom we check 
        # to see if the number of posts on the page has changed. We stop when there are 45 or more posts on the page or 
        # if the number of posts hasn't changed (on a profile's last page there may be fewer than 45 posts).
        num_current = 0
        while(num_current < 44):
            self.page.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            num_current = len(self.page.find_elements_by_xpath("//*[contains(concat(' ', @class, ' '), ' WB_detail ')]"))
            time.sleep(3)
            print ("num current is " + str(num_current))
        print ("done")
                
        # posts_element is a list of HTML elements where each element corresponds to a post.
        posts_element = self.page.find_elements_by_xpath("//*[contains(concat(' ', @class, ' '), ' WB_detail ')]")
        num_current = len(posts_element)
        posts = list()
        x = 0

        # Loop through each post element, collecting the relevant data from the post. The HTML elements which contain the data we 
        # need were identified by manually looking at the source HTML. 
        for element in posts_element:
            try:
                post = dict()
                post['status'] = str(element.find_element_by_class_name("W_f14").text).decode("UTF-8")
                post['forwarded'] = None
                post['attached_url'] = None
                post['date'] = element.find_elements_by_class_name("WB_from")[-1].find_element_by_tag_name("a").get_attribute("title")
                post['url'] =  element.find_elements_by_class_name("WB_from")[-1].find_element_by_tag_name("a").get_attribute("href")
                # Get the date for a post. If it is before end_date, then return False (we don't need to collect any more posts)
                d = datetime.strptime(post['date'].split(" ")[0],"%Y-%m-%d")
                #if (d < end_date):
                account_data['posts'] = account_data['posts'] + posts
                #return False
                
                # Get post likes, comments, and forwards counts
                try:
                    post_stats = element.find_element_by_xpath('../../div[2]').find_elements_by_tag_name("li")
                    for p in range(0, len(post_stats)):
                        if ('转发' in post_stats[p].get_attribute("textContent")):
                            post['numForwards'] = re.sub("[^0-9]", "", post_stats[p].get_attribute("textContent"))
                        if ('评论'.decode('utf-8') in post_stats[p].get_attribute("textContent")):
                            post['numComments'] = re.sub("[^0-9]", "", post_stats[p].get_attribute("textContent"))
                            post['numLikes'] = re.sub("[^0-9]", "", post_stats[p+1].get_attribute("textContent"))
                except ValueError:
                    pass
                
                # If the post contains forwarded content then it will contain and HTML element called "WB_feed_expand". We search for this 
                # element and collect the data about the forwarded content. 
                try: 
                    expanded = element.find_element_by_class_name("WB_feed_expand")
                    post['forwarded'] = dict()
                    post['forwarded']['account_id'] = expanded.find_element_by_class_name("W_fb").get_attribute("usercard").replace("id=","")
                    post['forwarded']['text'] = expanded.find_element_by_class_name("WB_text").text
                    post['forwarded']['date']=expanded.find_element_by_class_name("WB_from").find_element_by_class_name("S_txt2").text
                    post['forwarded']['url'] = expanded.find_element_by_class_name("WB_from").find_element_by_class_name("S_txt2").get_attribute("href")
                    WB_handle = expanded.find_element_by_class_name("WB_handle")
                    post['forwarded']['post_mid'] = WB_handle.get_attribute("mid")
                    counts = WB_handle.find_elements_by_tag_name("li")
                    post['forwarded']['num_forward']= re.sub("[^0-9]", "", counts[0].text)
                    post['forwarded']['num_comments']= re.sub("[^0-9]", "", counts[1].text)
                    post['forwarded']['num_likes'] = counts[2].text
                except:
                    pass
                
                # collect any URLs the user may have posted in the status. 
                url = element.find_elements_by_tag_name("a")
                for e in url:
                    if ("W_btn_b" in e.get_attribute("class")):
                        post['attached_url'] = e.get_attribute("href")
                        
            except Exception,e:
                print e
            num_current = num_current - 1
            posts.append(post)
        print " collected: %d posts" % len(posts)
        account_data['posts'] = account_data['posts'] + posts
        #return True
        
        
    def get_forwards_comments(self, url):
        post_data = dict()
        post_data['url'] = url
        self.page.get(url)
        ids = []
        while(True):
            try:
                ui.WebDriverWait(self.page,10).until(lambda page: page.find_elements_by_class_name("list_ul").find_elements_by_class_name("WB_text") or page.find_elements_by_class_name("icon_bed"))
            except NoSuchElementException:
                self.page.get(post_data['url'])
                try:
                    ui.WebDriverWait(self.page,10).until(lambda page: page.find_elements_by_class_name("list_ul").find_elements_by_class_name("WB_text") or page.find_elements_by_class_name("icon_bed"))
                except:
                    print "No commenters/forwarders."
                    return post_data
                
            if (len(self.page.find_elements_by_class_name("icon_bed")) == 1):
                print "No IDs gathered."
                return post_data
            
            accounts = self.page.find_elements_by_class_name("list_ul").find_elements_by_class_name("WB_text")
            
            for account in accounts:
                account_id = account.find_element_by_xpath("./a").get_attribute("usercard").replace("id=","")
                ids.append(account_id)
                next_button = self.page.find_elements_by_class_name("next")
            if (len(next_button) == 0):
                post_data['ids'] = ids
                print str(len(post_data['ids'])) + " ids collected."
                return post_data
            else:
                next_button[0].find_element_by_xpath("./span").click()
                time.sleep(5)
                #print "Next Page"
        print ("done")
        return post_data
              
credFile = open('credentialFile', 'r')
w1 = w_scraper()
w1.login(credFile)
account_followers = list()
account_followers = w1.getFollowers()
print(len(account_followers))
account_followers_utf = [x.encode('utf-8') for x in account_followers]
with open('WeiboFollowers.txt', 'w') as f:
    f.write(account_followers_utf)


#account_data = list()
#account_data = w1.getAccount()
#post_data = w1.get_forwards_comments('http://weibo.com/u/2407651573')
#post = get_hot_post(240765157)
#with codecs.open("AccountData", "wb", "utf-8") as temp:
#    temp.write(account_data)

#with open("AccountData",'wb') as f:
    
    #pickle.dump(account_data,f)
#w1.getPosts("http://weibo.com/u/2407651573?page=1&is_all=1#_0", 1)
