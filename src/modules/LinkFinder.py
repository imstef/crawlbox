from html.parser import HTMLParser
from urllib import parse

class LinkFinder(HTMLParser) :
	def __init__(self, baseURL, pageURL) :
		super().__init__()
		self.baseURL = baseURL
		self.pageURL = pageURL
		self.links = set()

	def handle_starttag(self, tag, attrs) :
		if tag == 'a' :
			for (attr, val) in attrs:
				if attr == 'href' :
					url = parse.urljoin(self.baseURL, val) # if full url, it will stay the same. If it is a relative url, it will combine it with the base url provided upon object creation
					self.links.add(url) # add a properly formated URL to our set of links

	def getPageLinks(self) :
		#print(self.links)
		return self.links

	def error(self, message) :
		pass
