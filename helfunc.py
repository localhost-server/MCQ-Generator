import json
import ast
import re
import streamlit as st

# Displaying data in streamlit
def disGen(data):
    for key,values in data.items():
        st.write(f"{key} : {values}")

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
    question_dict = {}
    format = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer", "Hint", "Explanation", "Sub-topic"]

    # Extract the question
    # p_tags = question.find('th').find_all('p')
    # question_text = ' '.join([p.text for p in p_tags[:-1]])  # Join all p tags except the last one (year)
    try:
        question_text=question.find('tr',class_='header').text.strip()
        question_text = re.sub(r'\(\d+\)', '', question_text)  # Remove the year

        question_dict[format[0]] = question_text.strip().replace('\n', ' ')

        # Extract the options
        options = question.find_all('td')
        for i, option in enumerate(options[:5], 1):  # Only the first 5 td tags are options
            if option.find('blockquote'):  # If the option is in a blockquote tag
                text = option.find('blockquote').text.strip().replace('\n', ' ')
            elif option.find('p'):  # If the option is in a p tag
                text = option.find('p').text.strip().replace('\n', ' ')
            else:  # If the option is directly in the td tag
                text = option.text.strip().replace('\n', ' ')
            question_dict[format[i]] = text

        # Extract the correct answer
        mapping = {'1': 'a', 'a': 'a', '2': 'b', 'b': 'b', '3': 'c', 'c': 'c', '4': 'd', 'd': 'd'}

        correct_answer = options[4].text.strip().replace('\n', ' ')
        question_dict[format[5]] = mapping.get(correct_answer,None)

        # Extract the hint (assuming it's the text in the 7th td tag)
        hint = options[5].text.strip().replace('\n', ' ')
        question_dict[format[6]] = hint

        # Extract the explanation
        explanation = options[6]  # Explanation is in multiple p tags
        explanation_text = ' '.join([p.text for p in explanation]).strip().replace('\n', ' ')
        question_dict[format[7]] = explanation_text

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
                question_dict[format[5]] = mapping.get(correct_answer,None)
            else:
                question_dict[format[i]]=content.text.strip()
        return question_dict