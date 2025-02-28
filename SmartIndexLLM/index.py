from lib.sftp_get import SFTPClient
from lib.engine import Engine, schema_builder
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess
import feedparser
import tempfile
import requests
import os
import yaml
import string
import re
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
                    prog='Indexer')
    parser.add_argument('-c', help="Path to yaml config file", required=True, metavar="YAML")
    return parser.parse_args()


def _index_pdf(engine, path, title, url="", datatype="pdf"):
    """
    Help function for pdf indexing
    """
    content = []
    printable = set(string.printable)
    for line in subprocess.check_output(f"pdftotext '{path}' -|perl -0pe 's/([^\\n])\\n([^\\n])/\\1 \\2/g;'", shell=True).decode('UTF-8').split('\n'):
        if re.match(r'.*[A-z]+.*', line) and '......' not in line and len(line) >= 1:
            content.append(''.join(filter(lambda x: x in printable, line)))
    if not title:
        title = os.path.basename(path)
    engine.index_doc('\n'.join(content), title=title, path=path, datatype=datatype, url=url)

def _index_text_file(engine, path, title, date=None, url="", datatype=""):
    """
    Help function for text file indexing
    """
    content = []
    printable = set(string.printable)
    with open(path, 'r', encoding='UTF-8') as f:
        for line in f.readlines():
            if re.match(r'.*[A-z]+.*', line) and len(line) >= 1:
                content.append(''.join(filter(lambda x: x in printable, line)))
    if not title:
        title = os.path.basename(path)
    engine.index_doc('\n'.join(content), title=title, path=path, date=date, url=url, datatype=datatype)


def sftp_index(config, e):
    """
    Get txt and pdf files over SFTP and index locally
    """
    print("####### Starting SFTP indexing #######")
    for con in config['sftp']:
        sftp_client = SFTPClient(con['hostname'], con['port'], con['username'], os.path.expanduser(con['private_key']), con['remote_directory'], con['local_directory'])
        Path(sftp_client.local_directory).mkdir(parents=True, exist_ok=True)
        sftp_client.connect()
        file_list = sftp_client.list_files()
        sftp_client.download_files(file_list)
        sftp_client.close()
    for fname in file_list:
        file_to_index = os.path.join(con['local_directory'], fname)
        if fname.lower().endswith('.txt'):
            _index_text_file(e, file_to_index, fname, datatype="txt", url=f"{con['username']}@{con['hostname']}:{con['port']}")
        elif fname.lower().endswith('.pdf'):
            _index_pdf(e, file_to_index, fname, datatype="pdf", url=f"{con['username']}@{con['hostname']}:{con['port']}")

def local_file_index(config, e):
    """
    index local files
    """
    print("####### Starting local file indexing #######")
    for i in config['local_file']:
        if i['path'].endswith('.pdf'):
            _index_pdf(e, i['path'], i['title'], datatype="pdf")
    else:
        _index_text_file(e, i['path'], i['title'], datatype="txt")

def web_index(config, e):
    """
    Index web content
    """
    print("####### Starting web data indexing #######")

    for con in config['web']:
        content = []
        r = requests.get(con['url'])
        content_lines = BeautifulSoup(r.text, 'html.parser').get_text().strip().split('\n')
        for line in content_lines:
            if line.strip() == '':
                continue
            content.append(line.strip())
        content = '\n'.join(content)
        e.index_doc(content, title=con['url'].replace('https://', '').replace('http://', ''), url=con['url'], datatype="web")

def rss_index(config, e):
    """
    Index rss content
    """
    print("####### Starting RSS feed indexing #######")
    for con in config['rss']:
        feed = feedparser.parse(con['url'])
        # Check if the index exists
        for entry in feed.entries:
            published = datetime(*entry.published_parsed[:6]) if 'published_parsed' in entry else datetime.now()
            # Check if 'description' attribute exists
            if 'description' in entry:
                description = BeautifulSoup(entry.description, 'html.parser').get_text()
                # Clean up description by removing empty lines and extra whitespace
                description = "\n".join(line.strip() for line in description.splitlines() if line.strip())
            else:
                description = entry.title
            summary = description[:200] + "..." if len(description) > 200 else description
            e.index_doc(description, title=entry.title, date=published, url=con['url'], datatype="rss", summary=summary)

def local_dir_index(config, e):
    def get_dir_files(ldir):
        dir_files = []
        for f in os.listdir(ldir['path']):
            if f.endswith('.txt') and ldir['txt']:
               dir_files.append(os.path.join(ldir['path'], f))
            elif f.endswith('.pdf') and ldir['pdf']:
               dir_files.append(os.path.join(ldir['path'], f))
        return dir_files
    print("####### Starting local directory indexing #######")
    for dir_path in config['local_dir']:
        for file_path in get_dir_files(dir_path):
            if file_path.endswith('.pdf'):
                _index_pdf(e, file_path, os.path.basename(file_path), datatype="pdf")
            else:
                _index_text_file(e, file_path, os.path.basename(file_path), datatype="txt")


if __name__=="__main__":
    args = parse_args()
    with open(args.c, 'r') as file:
        config = yaml.safe_load(file)
    # Get index settings
    index_schema = schema_builder(config['whoosh_index']['schema'])
    index_dir = config['whoosh_index']['dir']
    e = Engine(index_dir, index_schema=index_schema, index_chunk_size=500)
    # Index data
    if len(config['sftp']) > 0:
        sftp_index(config, e)
    if len(config['local_file']) > 0:
        local_file_index(config, e)
    if len(config['web']) > 0:
        web_index(config, e)
    if len(config['rss']) > 0:
        rss_index(config, e)
    if len(config['local_dir']) > 0:
        local_dir_index(config, e)
