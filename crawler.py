#!/usr/bin/python2.7

import re, getopt, sys
import operator
from bs4 import BeautifulSoup, Comment
import urllib2
from collections import Counter
from pytagcloud import create_tag_image, create_html_data, make_tags, LAYOUT_HORIZONTAL, LAYOUTS, LAYOUT_MIX, LAYOUT_VERTICAL, LAYOUT_MOST_HORIZONTAL, LAYOUT_MOST_VERTICAL
from pytagcloud.colors import COLOR_SCHEMES
from pytagcloud.lang.counter import get_tag_counts 

VERBOSE = False

def crawlSub(seed, nLinks): # returns index, graph of inlinks
    tocrawl = [seed]
    crawled = []
    index = Counter()
    while len(crawled) < nLinks and tocrawl: 
        page = tocrawl.pop()
        if VERBOSE:
            print("Crawling "+ page + "...")
        if page not in crawled:
            outlinks, index = processPage(page, seed, index)
            #for i in index: #WORKS! :D
                #if i == "skydive":
                #    print i, index[i]
            union(tocrawl, outlinks)

            crawled.append(page)
    return index
def processPage(page, seed, index):
    content = getPage(page)
    #print content
    soup = BeautifulSoup(content, "html.parser")
     #kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    rows = soup.find_all("div", attrs={"class": "content"})
    for row in rows:
        addPageToIndex(index, page, row.text)

    #print seed.find("comments")
    if seed.find("comments") == -1: #not already on comments page
         
        outlinks = getAllLinks(content, seed)
        #print outlinks
    else:
        outlinks = []
    return outlinks, index


def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def getPage(url):
	try:
		headers = { 'User-Agent' : 'redditWordGraph:v1 (by /u/kedibonye)' }
		req = urllib2.Request(url, None, headers)
		return urllib2.urlopen(req).read()
	except:
		return ""
    
def getNextTar(page, sub):

    start = page.find('<a href="' + sub)
    if start == -1: 
        return None, 0
    startQuote = page.find('"', start)
    endQuote = page.find('"', startQuote + 1)
    url = page[startQuote + 1:endQuote]
    return url, endQuote

def getAllLinks(page, subreddit):
    links = []
    while True:
        url, endpos = getNextTar(page, subreddit)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links


def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

def addPageToIndex(index, url, content):
    regex = re.compile('[^a-z]')
    words = ' '.join(s for s in content.split() if not any(c.isdigit() for c in s))
    words = words.split() 
    for word in words:
        word = word.lower()
        word = regex.sub('', word)
        if word:
            index[word] += 1
def usage(status=0):
    print >>sys.stderr, '''./crawler -h
Usage: crawler.py [-n PAGES-TO-CRAWL -o IMAGE-NAME -r SUB-REDDIT]

Options:

    -h              Show this help message
    -o IMAGE-NAME   Save wordcloud to specified file
    -r SUB-REDDIT   Sub-reddit to crawl
    -v              Enable verbose mode
    -n NUMBER       Maximum pages to visit

    '''
    sys.exit(status)
if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:r:hvn:")
    except getopt.GetoptError as err:
        print(err)
        usage()

    output_filename = "test.png" #default
    subreddit = "SkyDiving" #default
    n = 10
    base = "https://www.reddit.com/r/"

    for opt, arg in opts:
        if opt in ('-o', '--output'):
            output_filename = arg
        elif opt in ('-v', '--verbose'):
            VERBOSE = True
        elif opt in ('-h', '--help'):
            usage(1)
        elif opt == '-r':
            subreddit =  arg
        elif opt == '-n':
            n = int(arg)
        else:
            usage(1)
    f = open('commonWords.txt')
    common = f.read().split()
    index = crawlSub(base+subreddit, n)
    #print removeCommon
    for k, v in index.items():
        for w in common:
            if index[w]:
                del index[w]
        if k.find("submitted") != -1: #input error
            del index[k]
    wordscount = {w:f for w, f in Counter(index).most_common() if f > 2}
    sorted_wordscount = sorted(wordscount.iteritems(), key=operator.itemgetter(1),reverse=True)

    tags = make_tags(sorted_wordscount[:50], maxsize=100)
    create_tag_image(tags, output_filename, size=(1000,1000),  background=(0, 0, 0, 255), layout=LAYOUT_MIX, fontname='Molengo', rectangular=True)



