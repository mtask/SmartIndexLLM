import os
import hashlib
from whoosh import index
from whoosh.fields import Schema, KEYWORD, TEXT, ID, DATETIME
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from langchain_ollama import OllamaLLM
from datetime import datetime

def schema_builder(schema_data):
    def get_whoosh_field(field_data):
        field_type = field_data['type']
        stored = field_data['stored']
        unique = field_data.get('unique', False)
        match field_type:
            case 'ID':
                return ID(stored=stored, unique=unique)
            case 'KEYWORD':
                return KEYWORD(stored=stored)
            case 'TEXT':
                return TEXT(stored=stored)
            case 'DATETIME':
                return DATETIME(stored=stored)
            case 'NUMERIC':
                return NUMERIC(stored=stored)
            case 'BOOLEAN':
                return BOOLEAN(stored=stored)
            case 'STORED':
                return STORED()
            case 'NGRAM':
                return NGRAM(stored=stored)
            case _:
                raise ValueError(f"Unknown field type: {field_type}")

    fields = {key: get_whoosh_field(value) for key, value in schema_data.items()}
    schema = Schema(**fields)
    return schema


class Engine:

    def __init__(self, index_dir,
            model="llama3.2:1b",
            index_chunk_size=100,
            schema=Schema(id=ID(stored=True,unique=True),date=DATETIME(stored=True), title=KEYWORD(stored=True), path=TEXT(stored=True), content=TEXT(stored=True))
        ):
        self.index_dir = index_dir
        if not os.path.isdir(self.index_dir):
            print("Creating index")
            os.mkdir(self.index_dir)
            self.create_index()
        self.ix = open_dir(self.index_dir)
        self.ollama_model = model
        self.index_chunk_size = index_chunk_size

    def create_index(self):
        schema = Schema(id=ID(stored=True,unique=True),date=DATETIME(stored=True), title=KEYWORD(stored=True), path=TEXT(stored=True), content=TEXT(stored=True))
        index.create_in(self.index_dir, schema)

    def chunk_text(self, text):
        chunks = []
        current_chunk = []
        words = text.split()
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= self.index_chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def index_doc(self, title, content, path):
        print(f"[*] Indexing document with title: {title}")
        writer = self.ix.writer()
        chunks = self.chunk_text(content)
        for chunk in chunks:
            id = hashlib.sha256(chunk.encode('UTF-8')).hexdigest()
            writer.update_document(id=id, date=datetime.now(), title=title, content=chunk.strip(), path=path)
        writer.commit()

    def search(self, query_str):
        results = []
        with self.ix.searcher() as searcher:
            query = QueryParser("content", self.ix.schema).parse(query_str)
            hits = searcher.search(query, limit=1000000)
            for hit in hits:
                results.append(hit['content'])
        return results

    def query_ollama(self, prompt, context_size):
        """Send a query to Ollama and retrieve the response."""
        # Better use num_ctx with custom model's Parameters?
        llm = OllamaLLM(model=self.ollama_model)
        #llm = OllamaLLM(model=self.ollama_model, num_ctx=context_size)
        return llm.invoke(prompt)

    def generate_response(self, query, prompt, context_size=4096):
        retrieved_docs = self.search(query)
        context = " ".join(retrieved_docs)
        # Separate the prompt and the retrieved context
        augmented_prompt = f"Context: {context}\n\nQuestion: {prompt}\nAnswer:"
        print(augmented_prompt)
        ollama_response = self.query_ollama(prompt=augmented_prompt, context_size=context_size)
        return ollama_response

# Usage example
if __name__ == "__main__":
    conf = {'index_dir': 'whoosh_doc_index'}
    engine = Engine(conf)

    # Example: Indexing a document
    sample_title = "Sample Document"
    sample_content = "This is the content of the document. It contains information about various topics."
    sample_path = "path/to/sample_document.txt"
    engine.index_doc(title=sample_title, content=sample_content, path=sample_path)

    # Example: Generating a response
    whoosh_query = "title:'Sample Document'"
    ollama_prompt = "Explain the main concepts of quantum mechanics"
    response = engine.generate_response(query=whoosh_query, prompt=ollama_prompt)
    print(response)

