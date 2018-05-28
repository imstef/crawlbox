from html.parser import HTMLParser
from urllib import parse
import re

class CB_Parser(HTMLParser) :
	def __init__(self, jobType, baseURL, pageURL) :
		super().__init__()
		self.baseURL = baseURL
		self.pageURL = pageURL
		self.links = set()
		self.emails = set()
		self.scripts = set()
		self.siteMeta = set()
		self.siteStylesheets = set()
		self.jobType = jobType

	def handle_starttag(self, tag, attrs) :
		if tag == 'a' :
			for (attr, val) in attrs :
				if attr == 'href' :
					url = parse.urljoin(self.baseURL, val) # if full url, it will stay the same. If it is a relative url, it will combine it with the base url provided upon object creation
					self.links.add(url) # add a properly formated URL to our set of links

		#if self.jobType != 'r' :
		if tag == 'script' :
			scriptTag = '<' + tag + ' '
			for (attr, val) in attrs :
				if attr == 'type' :
					scriptTag += attr + '="' + val + '" '

				if attr == 'src' :
					scriptTag += attr + '="' + val + '"'

			scriptTag += '</' + tag + '>'
			filteredScripts = scriptTag.encode("ascii", errors="ignore").decode()
			self.scripts.add(filteredScripts)

		if tag == 'meta' :
			metaTag = '<' + tag + ' '
			for (attr, val) in attrs :
				if attr == 'name' :
					metaTag += attr + '="' + val + '" '
				if attr == 'content' :
					metaTag += attr + '="' + val + '"'

			metaTag += '>'

			filteredMeta = metaTag.encode("ascii", errors="ignore").decode()
			self.siteMeta.add(filteredMeta)


		if tag == 'link' :
			linkTag = '<' + tag + ' '
			for (attr, val) in attrs :
				if attr == 'rel' :
					linkTag += attr + '="' + val + '" '
				if attr == 'type' :
					linkTag += attr + '="' + val + '" '
				if attr == 'href' :
					linkTag += attr + '="' + val + '" '
				if attr == 'sizes' :
					linkTag += attr + '="' + val + '"'

			linkTag += '>'
			filteredLink = linkTag.encode("ascii", errors="ignore").decode()
			self.siteStylesheets.add(filteredLink)


	def handle_data(self, data) :
		# Find email addresses
		emailRegex = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}")
		#if emailRegex.search(data) :
			#print(data)
			#self.emails.add(data)

		# Find google adsense/analytics code
		#scriptRegex = re.compile('ca-pub')
		#if scriptRegex.search(data) :
			#print(data)
			#self.scripts.add(data)

	def getPageLinks(self) :
		#print(self.links)
		return self.links

	def getPageEmails(self) :
		return self.emails

	def getPageScripts(self) :
		return self.scripts

	def getPageMeta(self) :
		return self.siteMeta

	def getPageStylesheets(self) :
		return self.siteStylesheets

	def error(self, message) :
		pass
