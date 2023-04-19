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

    vectorstore = Chroma.from_documents(documents, embeddings)

    qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), vectorstore.as_retriever(search_kwargs={"k": 1}))
    
    print("QA chain initialized with file_id: ", file_id)
# Function to answer questions
def answer_question(query):
    global chat_history
    result = qa({"question": query, "chat_history": chat_history})
    chat_history.append((query, result["answer"]))
    return result

@app.route('/analyze_documents', methods=['POST'])
def analyze_documents():
    global documents, chat_history
    file_id = request.form.get('file_id')
    initial_query = request.form.get('initial_query', default="")
    file = request.files['file']
    filename = file.filename
    # file.save(filename)

    chat_history = []

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


    initialize_qa_chain(file_id)

    if initial_query == "":
        initial_query = "Give a brief about the document."
        print("===> initial query is empty")
    print(initial_query)
    
    answer = answer_question(initial_query)

    return jsonify({"message": "Documents analyzed and QA chain initialized.", "answer": answer})

import chat_gpt
@app.route('/chatqa', methods=['POST'])
def chatqa():
    global chat_history
    query = request.form.get('query')
    file_id = request.form.get('file_id')
    starting_prompt = request.form.get('starting_prompt', default="Answer the question in detail, and if you dont know the answer just answer 'i dont know the answer' also add new line characters whereever necessary, Question: ")
    print("===> starting prompt: ", starting_prompt)
    
    chat_history = []
    initialize_qa_chain(file_id)

    adv_query = starting_prompt + ' ' +query
    answer = answer_question(adv_query)

    check_sentence = "i don't know the answer"
    # find cosine similarity between the answer and the check sentence
    similarity = answer['answer'].lower().find(check_sentence)
    if similarity != -1:
        print("===> answer not there in pdf")
        answer['answer'] = chat_gpt.answer_notthere_question(query)

    # answer['answer'] = chat_gpt.add_newline_and_format_response(answer['answer'])

    return jsonify(answer)

@app.route('/new_chat', methods=['POST'])
def new_chat():
    global chat_history
    clear = request.form.get('clear')
    chat_history = []
    return jsonify({"message": "Chat history cleared."})

if __name__ == '__main__':
    app.run(host="0.0.0.0")
