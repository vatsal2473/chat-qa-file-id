from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

chat = ChatOpenAI(temperature=0)

def answer_notthere_question(query):
    result = chat([SystemMessage(content = "answer the question and add new line characters to format the text"),
                   HumanMessage(content=query)])

    # print(result)
    answer = result.content
    return answer

def add_newline_and_format_response(query):
    
    result = chat([SystemMessage(content = "add new line characters to format the text"),
                #    HumanMessage(content="The seven commandments of Animalism are: 1. Whatever goes upon two legs is an enemy. 2. Whatever goes upon four legs, or has wings, is a friend. 3. No animal shall wear clothes. 4. No animal shall sleep in a bed. 5. No animal shall drink alcohol. 6. No animal shall kill any other animal. 7. All animals are equal."),
                #    AIMessage(content="""
                #      The seven commandments of Animalism are:
                #         1. Whatever goes upon two legs is an enemy.
                #         2. Whatever goes upon four legs, or has wings, is a friend.
                #         3. No animal shall wear clothes.
                #         4. No animal shall sleep in a bed.
                #         5. No animal shall drink alcohol.
                #         6. No animal shall kill any other animal.
                #         7. All animals are equal.
                #      """),
                     HumanMessage(content=query)])
    answer = result.content
    return answer