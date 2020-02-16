# coding: utf-8

import requests

try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

headers = {
            "Host": "freemidi.org",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
           }

def clean_name(n):
	k = '\xa0'
	return n.replace(k, ' ')

def preority(dsk):
	def num_there(s):
		return any(i.isdigit() for i in s)

	if '%' in dsk or '+' in dsk or num_there(dsk):
		return " / H"
	return ""

if __name__ == '__main__':
	ROOT='https://finex-etf.ru'
	r = requests.get(ROOT+'/products/')  # , auth=('user', 'pass'))
	assert r.status_code == 200

	# Parse
	html = r.text
	soup = BeautifulSoup(html, features="html.parser")
	#print(soup.findAll('a', attrs={'class':'etf-card'}))

	ticker_to_data = {}
	keys = set()

	ptr = 0
	for link in soup.findAll('a',{'class':'etf-card'}):
		title = link.get('title')
		print(title)
		href = link.get('href')
		r = requests.get(ROOT + href)
		assert r.status_code == 200

		ticker_to_data[title] = {}

		# Subcall
		html = r.text
		sub_soup = BeautifulSoup(html, features="html.parser")
		sub_table = sub_soup.find('div',{'class':'fund-basic-information__table'})
		for l in sub_table.findAll('div',{'class':'fund-basic-information__table-item'}):
			# Search pairs
			name = l.find('div',{'class':'fund-basic-information__table-item-name'})
			descr = l.find('div',{'class':'fund-basic-information__table-item-descr'})
			dsk = descr.text.strip()
			name = clean_name(name.text)
			ticker_to_data[title][name+preority(dsk)] = dsk

		#session = requests.Session()

		# # Value report
		# #the website sets the cookies first
		# req1 = session.get(ROOT + href+"#", headers = headers)
		# #Request again to download
		# req2 = session.get(ROOT + href + "#", headers = headers)
		# with open(title+".xls", "wb") as xls:
		#     xls.write(req2.content)

		d = 'more-info-fund-table__row'
		extra_table = sub_soup.findAll('div',{'class': d})
		for v in extra_table:	
			name = v.find('span',{'class':'more-info-fund-table__item-name'})
			descr = v.find('span',{'class':'more-info-fund-table__item-descr'})
			
			if descr and name:
				dsk = descr.text.strip()
				name = clean_name(name.text)
				ticker_to_data[title][name+preority(dsk)] = dsk

		# Summary
		d = 'characteristics-fund__table-item'
		extra_table = sub_soup.findAll('div',{'class': d})
		for vv in extra_table:
			v = vv.find('p',{'class': 'characteristics-fund__table-name'})
			name = v.text.strip()
			v = vv.find('p',{'class': 'characteristics-fund__table-descr'})
			descr = v.text.strip()
			name =clean_name(name+" / hdr")
			dsk = descr.strip().replace(",", ".")
			ticker_to_data[title][name+preority(dsk)] = dsk

		# Pack
		ks = ticker_to_data[title].keys()
		for k in ks:
			keys.add(k)
		# ptr += 1
		# if ptr > 1:
		# 	break
		
		# break

	def MyFn(s):
		return s[-1] == 'H'

	keys = sorted(list(keys), reverse=True, key=MyFn)
	hdr = ["Ticker"]
	for k in keys:
		hdr.append(k.replace("/ H", ""))


	hdr = ','.join(hdr)

	with open('/tmp/finex_etf.csv', 'w') as the_file:
		the_file.write(hdr+'\n')

	for t in ticker_to_data:
		data = ticker_to_data[t]
		row = t
		for k in keys:
			if k in data:
				row += ',' + data[k]
			else:
				row += ',NAN'

		with open('/tmp/finex_etf.csv', 'a') as the_file:
			the_file.write(row+'\n')





