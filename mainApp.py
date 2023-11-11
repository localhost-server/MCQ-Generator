# Importing modules 
import streamlit as st
import re
# import io
import json
import ast
import os
import openai
# Importing Python Docx Reader
import unicodedata
# Importing PyPanDoc
import pypandoc
# Importing Tempfile
import tempfile
# Importing Beautiful Soup
from bs4 import BeautifulSoup
# importing langchain modules
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Setting up the API key
os.environ['OPENAI_API_KEY'] = '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'
openai.api_key = os.environ['OPENAI_API_KEY']

# Setting page config to wide mode
st.set_page_config(layout="wide")
# Title for the web app
st.title('MCQ Solver')

# Uploading the file
uploaded_file = st.file_uploader("Upload Your Files",type=['docx'])

# Available models
# models=openai.Engine.list()
# print(models)
# print(uploaded_file)
# type(uploaded_file)

# API JSON PARSER
def parse_string(data):
    if data.startswith("```json") and data.endswith("```"):
        start=data.find("{")
        end=data.rfind("}")+1
        json_str=data[start:end]
        return json.loads(json_str)
    else:
        return ast.literal_eval(data)
    
# Extracting data from html content from question 
def extract_data(question):
    question_dict={}
    # # Extract the question
    # question_dict[format[0]] = question.find('th').text.strip().replace('\n', '\t')
    # Extract the question
    p_tags = question.find('th').find_all('p')
    question_text = p_tags[0].text if p_tags else ''
    question_text = re.sub(r'\(\d+\)', '', question_text)  # Remove the year
    question_dict[format[0]] = question_text.strip().replace('\n', '\t')


    # Extract the options
    options = question.find_all('td')[:4]
    for i, option in enumerate(options, 1):
        text = option.text.strip().replace('\n', '')
        text = unicodedata.normalize("NFKD", text)  # Normalize the Unicode data
        question_dict[format[i]] = text

    # Extract the correct answer
    correct_answer = question.find_all('td')[4].text.strip().replace('\n', '')
    question_dict[format[5]] = unicodedata.normalize("NFKD", correct_answer)

    # Extract the explanation and sub-topic
    extras = question.find_all('td')[5:]
    question_dict[format[6]] = unicodedata.normalize("NFKD", extras[0].text.strip().replace('\n', ''))  # Explanation
    question_dict[format[7]] = unicodedata.normalize("NFKD", extras[1].text.strip().replace('\n', '\t'))  # Hint
    question_dict[format[8]] = unicodedata.normalize("NFKD", extras[2].text.strip().replace('\n', ''))  # Sub-topic
    return question_dict

# Creating a prompt template
genQtemplate= """I have questions in specific format and you have to generate and return new innovative practice question from same sub-topic with appropriate content even if it's not there in what i have sent to you for students in json format , keys format should be strictly same , keep sub-topic same : {question}"""
# template= """I have questions in specific format and you have to generate new innovative practice question from same sub-topic with appropriate content even if it's not there in what i have sent to you for students in json format , keys format should be strictly same : {question}"""
# genCtemplate= """I have questions in specific format and you have to correct the content and return the corrected question in json format only , improve the hint or explanation if you feel it's not correct , keys format should be strictly same , keep sub-topic same , don't send additional data like description of what you have done : {question}"""
genCtemplate= """I have questions in specific format and you have to correct the content and return the corrected question in json format only , rephrase the hint or explanation if you feel it's not correct , keys format should be strictly same , keep sub-topic same , don't send additional data like description of what you have done : {question}"""
genAdtemplate= """I have questions in specific format and you have to generate and return new innovative practice question from same sub-topic but it should involve some advanced concepts or more tough with appropriate content even if it's not there in what i have sent to you for students in json format , keys format should be strictly same , keep sub-topic same : {question}"""


llm = ChatOpenAI(model="gpt-4-1106-preview")
prompt = PromptTemplate(template=genQtemplate, input_variables=["question"])
llm_chain = LLMChain(prompt=prompt, llm=llm)


# Checking if the file is uploaded or not
if uploaded_file:

    # Creating a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        # Write the uploaded file's content to the temporary file
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # Checking data in text format
    # opening_file=Document(uploaded_file)
    opening_file=pypandoc.convert_file(tmp_file_path, 'html')
    # Converting into Soup HTML format
    soup = BeautifulSoup(opening_file, 'html.parser')
    # Checking the number of tables in the document
    
    configs=soup.find_all('table')[0]
    questions=soup.find_all('table')[1:]
    no_questions=len(questions)

    # configs=tables[0]
    # questions=tables[1:]
    # no_questions=len(questions)
    st.info(f"No of questions in the document are {no_questions}")


    # Creating json file for the questions
    question_set={}
    format=["Question","Option A","Option B","Option C","Option D","Correct Answer","Hint","Explanation","Sub-topic"]
    
    rows = configs.find_all('tr')
    # Creating a dictionary for the configs
    question_set["Config"]={cols[0].text: cols[1].text for row in rows for cols in [row.find_all(['th', 'td'])] if cols}
    
    # question_set["Config"]=dict(zip(
    #     [keys.text for keys in configs.columns[0].cells],
    #     [values.text for values in configs.columns[1].cells]
    #     ))

    # st.info(question_set["Config"])
    for key,values in question_set["Config"].items():
        # Checking in console
        # print(f"{key} : {values}")
        st.write(f"{key} : {values}" )
    # Creating a dictionary for the questions
    # question_set["Questions"]=[dict(zip(format,[(values.text[:-6].replace('\n','') if '(20' in values.text else values.text.replace('\n','')) for values in questions[i].columns[0].cells])) for i in range(no_questions)]
    question_set["Questions"]=[extract_data(question) for question in questions]

    # print(question_set["Questions"])
    # ques=st.button("See Questions")
    # if ques:
    # q_no=st.slider("Select Question",1,no_questions)
    # st.write(question_set["Questions"][q_no-1])
        # st.write(question_set.get(3))


    # Creating Columns
    ReadQuestion,GenerateQuestion=st.columns([2,3])

    # Reading the question and setting up Column 1
    with ReadQuestion:
        q_no = st.number_input(f"Select Question No : Max {no_questions} ", 1, no_questions, 1)

        # st.write(question_set["Questions"][q_no - 1])
        qs=question_set["Questions"][q_no - 1]
        for key,values in qs.items():
            st.write(f"{key} : {values}")
            # print(f"{key} : {values}")
        
        # Dividing the Button into two Columns
        gen_similar,gen_corrected,gen_advanced=st.columns(3)

        # Creating Buttons side by side
        with gen_similar:
            gen_similar=st.button("Generate Qs")
        with gen_corrected:
            gen_corrected=st.button("Correct It")
        with gen_advanced:
            gen_advanced=st.button("Gen Advanced")

    with GenerateQuestion:
        print(f"Gen Qs : {gen_similar} , Correct It : {gen_corrected} , Gen Advanced : {gen_advanced} ")
        if gen_similar:
            # st.write(qs)
            generatedContent=llm_chain.run(str(qs))
            print(generatedContent)
            json_str=parse_string(generatedContent)
            # print(type(json_str))

            st.write(f"Generated Question : ")
            for key,values in json_str.items():
                st.write(f"{key} : {values}")
            addIt=st.button(" ➕ ")
                # print(f"{key} : {values}")
            # st.write(json_str)
        
        elif gen_corrected:
            prompt = PromptTemplate(template=genCtemplate, input_variables=["question"])
            llm_chain = LLMChain(prompt=prompt, llm=llm)

            generatedContent=llm_chain.run(str(qs))
            print(generatedContent)
            json_str=parse_string(generatedContent)
            # print(type(json_str))

            st.write(f"Generated Corrected Question : ")
            for key,values in json_str.items():
                st.write(f"{key} : {values}")
            addIt=st.button(" ➕ ")
                # print(f"{key} : {values}")
            # st.write(json_str)
                    
        elif gen_advanced:
            prompt = PromptTemplate(template=genAdtemplate, input_variables=["question"])
            llm_chain = LLMChain(prompt=prompt, llm=llm)
            generatedContent=llm_chain.run(str(qs))
            print(generatedContent)
            json_str=parse_string(generatedContent)

            # print(type(json_str))

            st.write(f"Generated Advanced Question : ")
            for key,values in json_str.items():
                st.write(f"{key} : {values}")
            addIt=st.button(" ➕ ")
                # print(f"{key} : {values}")
            # st.write(json_str)
