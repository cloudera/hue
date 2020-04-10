all: fellowship.content

fellowship.content: html2odt.py
	python html2odt.py http://opendocumentfellowship.org/ >fellowship.content

clean:
	rm -f *.content *.meta *.styles

