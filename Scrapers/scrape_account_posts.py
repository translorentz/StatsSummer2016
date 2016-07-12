#! python2
# -*- coding: utf-8 -*-
# Version 2
# This is a script for scraping the posts from a list of weibo users's timelines (where each user is identified through their ID
# number). It uses the selenium python libraries to interact with the javascript on weibo's pages and scrape content. For each user
# it collects the number of statuses they have posted and all of their posts on or after January 1st, 2013. For each post it collects 
# the date posted, the ID of the post, the text content, any links the user may have posted, the number of likes/comments/forwards, and 
# whether the post was forwarded. If the post was forwarded, it also collects the forwarded content, the author of the post, the original date 
# of the forwarded post and the number of likes/comments/forwards. 
#
# In order to run selenium remotely (and to prevent it from opening up a visibile browser session every time the script
# runs) we create a virtual display. This is supported by the pythonvirtualdisplay library and Xvfb, a virtual frame buffer.
# More information can be found at http://django-notes.blogspot.com/2012/10/xvfb.html
#
# In order to conduct the scraping we first use the account credentials (username and password) of a valid weibo account to 
# log on to weibo.com. We then navigate to the page of every user and scrape the posts off their timeline. 

import selenium
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys  
import re
import pickle
import math
import contextlib
import selenium.webdriver.support.ui as ui
from pyvirtualdisplay import Display
from selenium import webdriver
from datetime import datetime
from datetime import date
import json
reload(sys)  
sys.setdefaultencoding('utf8')


class weibo_scraper(object): 

	def __init__ (self,show_window=False):
		if not show_window:
			# Create the display 
			self.display = Display(visible=0, size=(1349, 724)) 
			self.display.start()
		
		# Create the browser session using selenium. The page object represents the browser. We use it to navigate to webpages and interact with the content on these pages. 
		self.page = webdriver.Firefox()

		# A wait object that forces the page to wait until something on the page loads 
		self.wait = ui.WebDriverWait(self.page,10) 

	# login opens www.weibo.com/login.php. It enters the username/password combination and "clicks" the submit button. 
	def login(self, credentialFile):

		# Open the credential file and read in username/password
		for line in open(credentialFile):
			username,password = line.split(",")
		
		self.page.get("http://weibo.com/login.php") # load the login page
		print('Please Manually Switch Tabs')
		proceed = raw_input()
		#self.page.execute_script('var childDiv=document.getElementsByTagName("a")[2]; childDiv.click()') # Click the Username/Password Tab
		
		# submit username and password info
		username_element= self.page.find_elements_by_name("username")[0]
		username_element.send_keys(username)
		password_element = self.page.find_elements_by_name("password")[0]
		password_element.send_keys(password)
		self.page.find_elements_by_class_name("W_btn_a")[0].click()
	
	def getFollowers(self, accountID):
	
		# Open the file that contains the list of account ID numbers
		for line in open("actual_ids.txt", "r"):
			account_url = ('http://weibo.com/u/' + line)
			self.page.get(account_url) # Go to specific account homepage
			
			followers = self.page.execute_script("return document.evaluate(\"//a[@class='W_f18']/child::text()\", document, null, XPathResult.STRING_TYPE, null).stringValue;")
			print followers
			
			
			# felement = self.page.find_element_by_tag_name("strong")[1]
			# print self.page.execute_script("return arguments[0].innerHTML", felement)
			
			
			# followers_element = self.page.execute_script("return document.getElementsByTagName('strong')[1].innerHTML;")
			
			# print followers_element
			
			
			
			
			
			# followers_element = self.page.find_element_by_css_selector("td.S_line1:nth-child(2) > a.t_link > strong.W_f18")
			# strong = self.page.find_element_by_css_selector("td.S_line1:nth-child(2) > a:nth-child(1) > strong:nth-child(1)")
			#strong = self.page.find_element_by_tag_name("strong")[1]
			#Numbe_of_Followers = strong.get_attribute('innerHTML')
			
			
			# print followers_element
			# print Numbe_of_Followers
			# print ('Account number: ' + line + '\n Followers: ' + followers_element)
			# print ('Account number ' + line + 'has ' + followers_element + 'followers')
			

	# getAccount collects all the post data for a given account ID.  
	# end_date is a datetime object cutoff date for scraping (collect all posts after this date)
	def getAccount(self, base_url, end_date, num_pages_to_scrape = 0):
		account_data = dict()
		base_url = "http://weibo.com/u/" + str(base_url)
		# Go to first page of the account 
		self.page.get(base_url + "?page=1") 
		print "Starting Account: %s" % str(base_url)

		try:
			# Wait for the account self.page to load by looking for the presence of an HTML element of class 'tb_counter'
			ui.WebDriverWait(self.page,20).until(lambda page: page.find_element_by_class_name('tb_counter'))
			# Collect the number of statuses posted by the account. The labels for this HTML class can change - if you get an error double chekc the weibo page. 
			counts = self.page.find_element_by_class_name('tb_counter').find_elements_by_class_name("S_line1")
			account_data['status_counts'] = int(re.sub("[^0-9]", "", counts[2].get_attribute("textContent")))
		except:
			try: 
				self.page.get(base_url + "?page=1") 
				ui.WebDriverWait(self.page,20).until(lambda page: page.find_element_by_class_name('tb_counter'))
				counts = self.page.find_element_by_class_name('tb_counter').find_elements_by_class_name("S_line1")
				account_data['status_counts'] = int(re.sub("[^0-9]", "", counts[2].get_attribute("textContent")))
			except Exception as e:
				print "Failed to find counts for this account - please check HTML or try again. " + str(e)
			return	

		print "Number of posts: %d" % account_data['status_counts']

		# weibo splits a user's timeline into pages, with each self.page containing 45 posts. 
		numpages = int(math.ceil(account_data['status_counts']/45.0)) 
		if (num_pages_to_scrape == 0):
			num_pages_to_scrape = numpages

		account_data['posts'] = list() # the list object in account_data (where each element is a post)
		
		# Cycle through each self.page in the account and collect the posts from that self.page. 
		for p in range(1,numpages+1):
			
			# If we can't or don't need to collect any more posts from this account, getPosts() will return False
			if (p > num_pages_to_scrape):
				break
			print "\t Account %s, Page (%d/%d)" % (base_url, p,numpages)
			if (self.getPosts(base_url,p,account_data,end_date) == False):
				break
		return account_data

	# Gets the posts from a self.page of an account. Adds these posts to account_data
	def getPosts(self,base_url, pageNum,account_data,end_date):

		print "fetching: " + base_url+ "?is_all=1&page=" + str(pageNum),
		self.page.get(base_url+ "?is_all=1&page=" + str(pageNum)) # Navigate to the self.page of the account 
		
		# Wait for the self.page to successfully load by checking for the presence of the "WB_detail" HTML element. If 10 seconds passes 
		# we reload the self.page and try again. If we try 4 or more times we abort this account. 
		timesTried = 0 
		while True:
			try:
				timesTried = timesTried + 1
				self.wait.until(lambda page: page.find_elements_by_class_name("WB_detail"))
				break
			except:
				if (timesTried < 4):
					self.page.get(base_url + "?is_all=1&page=" + str(pageNum))
					pass
				else:
					account_data = None
					return False

		# Though each page of a user's timeline contains 45 posts, weibo initially only displays 15. In order to get 
		# get the other posts we have to simulate scrolling down on the page. Everytime we scroll to the bottom weibo
		# loads another 15. We thus scroll twice to get the other 30 posts. Everytime we scroll to the bottom we check 
		# to see if the number of posts on the page has changed. We stop when there are 45 or more posts on the page or 
		# if the number of posts hasn't changed (on a profile's last page there may be fewer than 45 posts).
		num_current = 0
		while(num_current < 45):
			self.page.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			try:
				self.wait.until(lambda page: len(page.find_elements_by_xpath("//*[contains(concat(' ', @class, ' '), ' WB_detail ')]")) > num_current)
				num_current = len(self.page.find_elements_by_xpath("//*[contains(concat(' ', @class, ' '), ' WB_detail ')]"))
			except:
				break
		
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
				if (d < end_date):
					account_data['posts'] = account_data['posts'] + posts
					return False

				# Get post likes, comments, and forwards counts
				try:
					post_stats = element.find_element_by_xpath('../../div[2]').find_elements_by_tag_name("li")
					for p in range(0, len(post_stats)):
						if ('转发' in post_stats[p].get_attribute("textContent")):
							post['numForwards'] = re.sub("[^0-9]", "", post_stats[p].get_attribute("textContent"))
						if ('评论' in post_stats[p].get_attribute("textContent")):
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
		return True

	def get_forwards_comments(self, url):
		post_data = dict()
		post_data['url'] = url
		self.page.get(url)
		ids = []
		while(True):
			try:
				self.wait.until(
					lambda page: page.find_elements_by_class_name("list_ul")[0].find_elements_by_class_name("WB_text") or page.find_elements_by_class_name("icon_bed"))
			except:
				self.page.get(post_data['url'])
				try:
					self.wait.until(
						lambda page: page.find_elements_by_class_name("list_ul")[0].find_elements_by_class_name("WB_text") or page.find_elements_by_class_name("icon_bed"))
				except:
					print "No commenters/forwarders."
					return post_data

			if (len(self.page.find_elements_by_class_name("icon_bed")) == 1):
				print "No IDs gathered."
				return post_data

			accounts = self.page.find_elements_by_class_name("list_ul")[0].find_elements_by_class_name("WB_text")
			
			
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
		return post_data

	def get_hot_post(self,id):
		
		# Go to first page of the account 
		self.page.get("http://weibo.com/u/" + str(id)) 
		print "Starting Account: %s" % str(id)
		
		# Wait for the self.page to successfully load by checking for the presence of the "WB_detail" HTML element. If 10 seconds passes 
		# we reload the self.page and try again. If we try 4 or more times we abort this account. 
		timesTried = 0 
		while True:
			try:
				timesTried = timesTried + 1
				self.wait.until(lambda page: page.find_elements_by_class_name("WB_detail"))
				break
			except:
				if (timesTried < 4):
					self.page.get("http://weibo.com/u/" + str(id))
					pass
				else:
					account_data = None
					return False

		# posts_element is a list of HTML elements where each element corresponds to a post.			
		posts_element = self.page.find_elements_by_xpath("//*[contains(concat(' ', @class, ' '), ' WB_detail ')]")
		num_current = len(posts_element)
		posts = list()
		x = 0

		# Loop through each post element, collecting the relevant data from the post. The HTML elements which contain the data we 
		# need were identified by manually looking at the source HTML. 
		element  = posts_element[0]
		try:
			post = dict()
			post['status'] = str(element.find_element_by_class_name("W_f14").text).decode("UTF-8")
			post['forwarded'] = None
			post['attached_url'] = None
			post['date'] = element.find_elements_by_class_name("WB_from")[-1].find_element_by_tag_name("a").get_attribute("title")
			post['url'] =  element.find_elements_by_class_name("WB_from")[-1].find_element_by_tag_name("a").get_attribute("href")
			# Get the date for a post. If it is before end_date, then return False (we don't need to collect any more posts)
			d = datetime.strptime(post['date'].split(" ")[0],"%Y-%m-%d")

			# Get post likes, comments, and forwards counts
			try:
				post_stats = element.find_element_by_xpath('../../div[2]').find_elements_by_tag_name("li")
				for p in range(0, len(post_stats)):
					if ('转发' in post_stats[p].get_attribute("textContent")):
						post['numForwards'] = re.sub("[^0-9]", "", post_stats[p].get_attribute("textContent"))
					if ('评论' in post_stats[p].get_attribute("textContent")):
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
		return post


