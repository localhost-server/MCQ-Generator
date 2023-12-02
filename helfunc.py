import json
import ast
import re
import streamlit as st
from streamlit import session_state as ss
import unicodedata


# Function to save API key to a configuration file
def save_api_key(api_key):
    try:
        with open('.config', 'w') as file:
            file.write(f"OPENAI_API_KEY={api_key}")
    except Exception as e:
        st.warning(f"Error saving API key: {e}")

# Function to load API key from a configuration file
def load_api_key():
    try:
        with open('.config', 'r') as file:
            for line in file:
                if line.startswith("OPENAI_API_KEY="):
                    return line[len("OPENAI_API_KEY="):].strip()
    except FileNotFoundError:
        return None
    except Exception as e:
        st.warning(f"Error loading API key: {e}")
        return None



def file_upload_check(file):
    if not hasattr(ss, 'uploaded_file') or ss.uploaded_file is None:
        # If there is no previously uploaded file, set the current file as the uploaded file
        ss.uploaded_file = file
        return True
    elif ss.uploaded_file.name == file.name:
        # If the current file has the same name as the previously uploaded file, return True
        return True
    else:
        # If the current file is different from the previously uploaded file, update the uploaded file and return False
        ss.uploaded_file = file
        return False

# Displaying data in streamlit
def disGen(data):
    for key,values in data.items():
        st.write(f"{key} : {values}")

# API JSON PARSER
def parse_string(data):
    if data.startswith("```json") and data.endswith("```"):
        start = data.find("{")
        end = data.rfind("}") + 1
        data = data[start:end]
        data_dict = json.loads(data)
        print("String PARSED")
    else:
        data_dict = ast.literal_eval(data)
        print("String PARSED")

    if 'Question' in data_dict:
        lines = data_dict['Question'].splitlines()
        for i in reversed(range(len(lines))):
            if re.search(r'\b\d{4}\b', lines[i]):
                lines.pop(i)
                print("Year Section Removed")
                break
        data_dict['Question'] = '\n'.join(lines)
    return data_dict

# API CORRECT ANSWER PARSER
def parse_C_string(data):
    if data.startswith("```json") and data.endswith("```"):
        start=data.find("{")
        end=data.rfind("}")+1
        json_str=data[start:end]
        return json.loads(json_str)
    else:
        return ast.literal_eval(data)

    
# Extracting data from html content from question
# Question Extraction function
def extract_data(question):
    question_dict = {}
    format = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer", "Hint", "Explanation", "Sub-topic"]

    # Extract the question
    # p_tags = question.find('th').find_all('p')
    # question_text = ' '.join([p.text for p in p_tags[:-1]])  # Join all p tags except the last one (year)
    try:
        question_text=question.find('tr',class_='header').text.strip()
        # question_text = re.sub(r'\(\d+\)', '', question_text)  # Remove the year

        question_dict[format[0]] = question_text.strip() #.replace('\n', ' ')

        # Extract the options
        options = question.find_all('td')
        for i, option in enumerate(options[:5], 1):  # Only the first 5 td tags are options
            if option.find('blockquote'):  # If the option is in a blockquote tag
                text = option.find('blockquote').text.strip().replace('\n', ' ')
            elif option.find('p'):  # If the option is in a p tag
                text = option.find('p').text.strip().replace('\n', ' ')
            else:  # If the option is directly in the td tag
                text = option.text.strip().replace('\n', ' ')
            question_dict[format[i]] = unicodedata.normalize("NFKD",text)

        # Extract the correct answer
        mapping = {'1': 'a', 'a': 'a', '2': 'b', 'b': 'b', '3': 'c', 'c': 'c', '4': 'd', 'd': 'd'}

        correct_answer = options[4].text.strip().replace('\n', ' ')
        question_dict[format[5]] = unicodedata.normalize("NFKD", mapping.get(correct_answer.lower(),None))

        # Extract the hint (assuming it's the text in the 7th td tag)
        hint = options[5].text.strip().replace('\n', ' ')
        question_dict[format[6]] = unicodedata.normalize("NFKD",hint)

        # Extract the explanation
        explanation = options[6]  # Explanation is in multiple p tags
        explanation_text = ' '.join([p.text for p in explanation]).strip().replace('\n', ' ')
        question_dict[format[7]] = unicodedata.normalize("NFKD",explanation_text)

        # Extract the sub-topic
        sub_topic = options[7].text.strip().replace('\n', ' ')
        question_dict[format[8]] = sub_topic

        return question_dict
    except:
        for i , content in enumerate(question.find_all('tr')):
            if i==5:
                # Extract the correct answer
                mapping = {'1': 'a', 'a': 'a', '2': 'b', 'b': 'b', '3': 'c', 'c': 'c', '4': 'd', 'd': 'd'}
                correct_answer = content.text.strip().replace('\n', ' ')
                question_dict[format[5]] = mapping.get(correct_answer.lower(),None)
            else:
                question_dict[format[i]]=unicodedata.normalize("NFKD",content.text.strip())
        return question_dict
