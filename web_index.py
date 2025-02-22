import os
import sys
import yaml
import requests
import tempfile
from lib.engine import Engine
from lib.index import index_text,index_pdf
from pathlib import Path
from bs4 import BeautifulSoup


if __name__=="__main__":
    with open('conf/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    e = Engine({"index_dir": config['whoosh_index_dir']})
    # Get data from all URLs 
    for con in config['web']:
        content = []
        r = requests.get(con['url'])
        content_lines = BeautifulSoup(r.text, 'html.parser').get_text().strip().split('\n')
        for line in content_lines:
            if line.strip() == '':
                continue
            content.append(line.strip())
        content = '\n'.join(content)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content.encode('UTF-8'))
        index_text(e, temp_file.name, con['url'])
        os.unlink(temp_file.name)
