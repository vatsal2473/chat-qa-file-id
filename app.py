from flask import Flask, request, jsonify
import os
import pickle
from werkzeug.utils import secure_filename
from flask_cors import CORS

# Import the necessary libraries
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import TextLoader

import file_conversion

import os

app = Flask(__name__)
CORS(app)

# Initialize global variables
documents = []
qa = None
chat_history = []

# Function to initialize the QA chain
def initialize_qa_chain(file_id):
    global qa

    with open(f'pkl_files/{file_id}.pkl', 'rb') as f:
        documents, embeddings = pickle.load(f)
    # with open('pkl_files/documents/'+file_id+'.pkl', 'rb') as f:
    #     documents = pickle.load(f)
    # with open('pkl_files/embeddings/'+file_id+'.pkl', 'rb') as f:
    #     embeddings = pickle.load(f)

    vectorstore = Chroma.from_documents(documents, embeddings)

    qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), vectorstore.as_retriever())
    
    print("QA chain initialized with file_id: ", file_id)
# Function to answer questions
def answer_question(query):
    global chat_history
    result = qa({"question": query, "chat_history": chat_history})
    chat_history.append((query, result["answer"]))
    return result

@app.route('/analyze_documents', methods=['POST'])
def analyze_documents():
    global documents
    file_id = request.form.get('file_id')
    file = request.files['file']
    filename = file.filename
    # file.save(filename)

    file.save(os.path.join('data/all_files', filename))

    new_filename = filename
    if filename.endswith('.docx'):
        file_conversion.docx_to_text(filename)
        new_filename = filename[:-5] + '.txt'
    elif filename.endswith('.pdf'):
        file_conversion.pdf_to_text(filename)
        new_filename = filename[:-4] + '.txt'
    elif filename.endswith('.txt'):
        # move file to all_files folder to txt_files folder
        os.rename(os.path.join('data/all_files', filename), os.path.join('data/txt_files', filename))
        new_filename = filename
    else:
        return jsonify({"message": "Invalid file type."})

    filename = os.path.join('data/txt_files', new_filename)
    print(filename)

    loader = TextLoader(filename)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    
    documents = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()

    # Save documents and vectorstore as a pickle file
    with open(f'pkl_files/{file_id}.pkl', 'wb') as f:
        pickle.dump((documents, embeddings), f)
    # with open('pkl_files/documents/'+file_id+'.pkl', 'wb') as f:
    #     pickle.dump(documents, f)
    # with open('pkl_files/embeddings/'+file_id+'.pkl', 'wb') as f:
    #     pickle.dump(embeddings, f)

    # os.remove(filename)
    initialize_qa_chain(file_id)
    return jsonify({"message": "Documents analyzed and QA chain initialized."})

@app.route('/chatqa', methods=['POST'])
def chatqa():
    global chat_history
    query = request.form.get('query')
    file_id = request.form.get('file_id')
    chat_history = []
    initialize_qa_chain(file_id)
    answer = answer_question(query)
    return jsonify(answer)

@app.route('/new_chat', methods=['POST'])
def new_chat():
    global chat_history
    clear = request.form.get('clear')
    chat_history = []
    return jsonify({"message": "Chat history cleared."})

if __name__ == '__main__':
    app.run(host="0.0.0.0")
