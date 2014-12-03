# Python web crawler

Simple web crawler written in Python. Consists of a Python module 'crawl', and a script to render its outputted site map into a simple HTML format.

To use, simply run:

- `pip install -r requirements.txt`
- `python create_site_map.py [domain]` to print the HTML, or
- `python create_site_map.py [domain] -f [filename]` to output to a file

For example, running `python create_site_map.py joelotter.com -f map.html` will output a site map for my own website into the file *map.html*.
