"""
Author-Divyansh Sharma
TASK ::

Write a program that takes a URL as an input, and saves the response of that URL in a file,
and then does the same for all the pages linked inside that HTML page. 

LIBRARIES USED :: urllib,re,urlparse,Queue 
All libraries used are already built-in utility libraries come packaged with Python 2.7
Please look in the comment aside the library import for more details.
PS : The links file generated are written into text files for debugging purposes,we can comment them but i have not commented as it will 
give a better view,understanding and debugging of  the program.
"""
import urllib	#used for fetching content over internet
import re 		#regex library for python  
from urlparse import urlparse 
#for parsing URL into parts: 1)Scheme:'http','https',etc the protocol 2) Netloc: is the network location of that resource,'www.google.com'
#3)Path : is the URL path like '/en/resources.html'
from Queue import Queue #built in Queue ADT for storing links
import os #os module for making directries,changing directory path etc
count=0
prgrm_path=os.getcwd() #gets the current working directory of the program
"""
init function fetches the seed URL html page and content and finds all links associated with it using regex.
Using a queue for storing links in the seed URL.I assume the seed URL is parent and the links contained inside is child.
After i recognise all the child links in the parent page i insert them into the queue,and pop the parent link from the queue.
This is done till the queue is not empty and all the child have not been visited.Basically I am doing a Breadth First Search.
"""
def init(): 
	inp=open('input.txt','r') #takes the input from a input text file
	req=inp.read()
	inp.close()
	base_url_obj=urlparse(req) #parsing the URL
	base_url=base_url_obj.scheme+"://"+base_url_obj.netloc
	#proxies={'http',''}
	#urllib.urlopen(req,proxies=proxies)
	#You can use aove commented method in case of static proxies to download content over the internet,by default the connection is DIRECT
	response = urllib.urlopen(req) #opens the URL
	the_page = response.read()     #reads the URL and saves it as a string
	urls = re.findall(r'href=[\'"]?([^\'" >]+)', the_page) #this is a regex to check for all links inside the downloaded html page,uses re module
	q=Queue(maxsize=0)
	#some preprocessing with the links if the links are external links they are not changed,but if the are attached to a parent they are 
	#modified and attached with parent base URL.example: a link referring to other child resource may be defined as < a href='/reference/index.html>'
	#using regex i am getting '/reference/index.html' as a link
	#actually its relative URL to the parent,so changing that link to : 'www.google.com/reference/index.html'
	for x in range(len(urls)):
		if urls[x].startswith('/'): #if relative to parent make it absolute
			urls[x]=base_url+urls[x]
		elif urls[x].startswith(base_url_obj.scheme): #if its third party links dont touch them
			urls[x]=urls[x]
		else : 
			urls[x]=base_url+base_url_obj.path[:(base_url_obj.path).rfind('/')]+'/'+urls[x] 
		q.put(urls[x]) #put the links in queue
	target=open('index.html','w')
	target1=open('links.txt','w')
	target.write(the_page)
	links='\n'.join(urls)
	target1.write(links)
	target.close()
	target1.close()
	#opening and closing files in python,writing html page and links to a file
	download_content(q) #call a recursive function that will do the same things for all the links in the link file,in argument it passes the initial queue
"""
This  a recursive function which does all the magic of fetching html for all the child links of the seed URL.
"""
def download_content(q) :
	global count
	global prgrm_path
	while not q.empty(): #do while the queue is not empty
		reqst=q.get() #get the top node
		# below things are almost same as init function
		bs_url_obj=urlparse(reqst) 
		bs_url=bs_url_obj.scheme+"://"+bs_url_obj.netloc
		bs_path=bs_url_obj.path
		if bs_path.endswith('/'):
			bs_path=bs_path[:-1]
		resp=urllib.urlopen(reqst)
		html_pg=resp.read()
		links=re.findall(r'href=[\'"]?([^\'" >]+)', html_pg)
		for x in range(len(links)):
			tmp=links[x]
			if links[x].endswith('/'):
				links[x]=tmp[:-1]
			if links[x].startswith('/'):
				links[x]=bs_url+links[x]
			elif links[x].startswith(bs_url_obj.scheme):
				links[x]=links[x]
			else:
				links[x]=bs_url+bs_url_obj.path[:(bs_url_obj.path).rfind('/')]+'/'+links[x]
			q.put(links[x]) #put all the child links in queue
		q.task_done() #remove parent node from queue
		
		filenm=bs_path[bs_path.rfind('/'):] #dynamic file naming according to the name of resources
		if filenm.startswith('/'): #as resources are names starting with '/',removing '/' as special symbols are not permitted in naming,so '/reference'
			filenm=filenm[1:]      #will be named as reference
		path=bs_url_obj.netloc+bs_path 
		if not os.path.exists(path): #checks if file already exists else make directory in the given path
			os.makedirs(path)
		os.chdir(path) #go to the path to write the html files in the hierarchical style
		exec "target%d=open('%s.html','w')"%(count,filenm)
		exec "target_again%d=open('link_file%d.txt','w')"%(count,count)
		exec "target%d.write(html_pg)"%count
		tp_link='\n'.join(links)
		exec "target_again%d.write(tp_link)"%count
		exec "target%d.close()"%count
		exec "target_again%d.close()"%count
		os.chdir(prgrm_path+'\\'+bs_url_obj.netloc)
		count=count+1
		download_content(q) #call again for other links in the queue
init() #call the init function
