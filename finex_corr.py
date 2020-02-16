# coding: utf-8

if 0:
	# import PyPDF2
	# pdfFileObj = open('risk monitor_dec-2.pdf','rb')     #'rb' for read binary mode
	# pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	# print(pdfReader.numPages)
	#
	# # pageObj = pdfReader.getPage(2)          #'9' is the page number
	# # print(pageObj.extractText())
	#
	#
	# # sudo pip3 install slate3k
	#
	# import slate3k as slate
	#
	# with open('risk monitor_dec-2.pdf', 'rb') as f:
	#     doc = slate.PDF(f)
	#
	# # doc
	# #prints the full document as a list of strings
	# #each element of the list is a page in the document
	#
	# print(doc[4])
	# #prints the first page of the document
	import sys
	sys.path.append('./pdf_table_extract/src/')

	# import pdftableextract.cor

	import pdftableextract as pdf
	import pandas as pd
	import pdftableextract as pdf

	pages = ["4"]
	# pages = ["1"]
	cells = [pdf.process_page('risk monitor_dec-2.pdf',p) for p in pages]

	#flatten the cells structure
	cells = [item for sublist in cells for item in sublist ]

	#without any options, process_page picks up a blank table at the top of the page.
	#so choose table '1'
	li = pdf.table_to_list(cells, pages)[1]

	#li is a list of lists, the first line is the header, last is the footer (for this table only!)
	#column '0' contains store names
	#row '1' contains column headings
	#data is row '2' through '-1'

	# data =pd.DataFrame(li[2:-1], columns=li[1], index=[l[0] for l in li[2:-1]])
	# print data

if 1:
	# https://finexetf.ru/api/xls_nav_all.php
	pass