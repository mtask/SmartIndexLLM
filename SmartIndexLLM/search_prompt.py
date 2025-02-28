import string
import re
import os
import subprocess
import sys
import argparse
import yaml
from lib.engine import Engine, schema_builder

def parse_args():
    parser = argparse.ArgumentParser(
                    prog='Doc Indexer')
    parser.add_argument('-c', help="Path to yaml config file", required=True)
    parser.add_argument('--model', default="llama3.2:3b", help="LLM to use (default 'llama3.2:3b')", required=False)
    parser.add_argument('--whoosh_query', help="Whoosh query to search context for prompt", required=True)
    parser.add_argument('--ollama_prompt', help="Ollama prompt that is combined with context", required=True)
    return parser.parse_args()

if __name__=="__main__":
    args = parse_args()
    with open('conf/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    # Get index settings
    index_schema = schema_builder(config['whoosh_index']['schema'])
    index_dir = config['whoosh_index']['dir']
    e = Engine(index_dir, schema=index_schema)
    response = e.generate_response(query=args.whoosh_query, prompt=args.ollama_prompt)
    print(response)
