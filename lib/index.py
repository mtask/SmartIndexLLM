import string
import re
import os
import subprocess
import sys

def recursive(doc_type):
    docs = []
    for root, dirs, files in os.walk(target_path):
        for file in files:
            path = os.path.join(root,file)
            if path.endswith(doc_type):
                docs.append(path)
    return docs

def index_pdf(engine, path, title):
    content = []
    printable = set(string.printable)
    for line in subprocess.check_output(f"pdftotext '{path}' -|perl -0pe 's/([^\\n])\\n([^\\n])/\\1 \\2/g;'", shell=True).decode('UTF-8').split('\n'):
        if re.match(r'.*[A-z]+.*', line) and '......' not in line and len(line) >= 1:
            content.append(''.join(filter(lambda x: x in printable, line)))
    if not title:
        title = os.path.basename(path)
    engine.index_doc(title, '\n'.join(content), path)

def index_text(engine, path, title):
    content = []
    printable = set(string.printable)
    with open(path, 'r', encoding='UTF-8') as f:
        for line in f.readlines():
            if re.match(r'.*[A-z]+.*', line) and len(line) >= 1:
                content.append(''.join(filter(lambda x: x in printable, line)))
    if not title:
        title = os.path.basename(path)
    engine.index_doc(title, '\n'.join(content), path)
