from flask import Flask, jsonify, request
import re
from groq import Groq
from flask_cors import CORS
import psycopg
from fastapi import FastAPI, Depends

app = Flask(__name__)
CORS(app)

# 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
# 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

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

messages = [
    {
        "role": "system",
        "content": "You are The Business Startup Portal (BSP), a tool to help people who want to start a business decide what that business could be, how to plan its development and get to launch. Be conversational yet professional, and lead the user step by step through the business startup cycle."
    },
    {
        "role": "user",
        "content": "Hello, I need help finding a business to start."
    }
]

global_headlines = []
global_content = []

def generate_chat_response(messages, model="llama3-8b-8192"):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
    )
    return chat_completion.choices[0].message.content

def parse_ideas(response):
    pattern = r"(\d+)\.\s\*\*(.*?)\*\*"
    matches = re.findall(pattern, response)
    headlines = [match[1] for match in matches]
    
    content_pattern = r"\d+\.\s\*\*.*?\*\*:\s(.*)"
    content_matches = re.findall(content_pattern, response)
    
    return headlines, content_matches

def parse_swot(response):
    description_pattern = r"(?<=Description:).*?(?=Strengths:)"
    strengths_pattern = r"(?<=Strengths:).*?(?=Weaknesses:)"
    weaknesses_pattern = r"(?<=Weaknesses:).*?(?=Opportunities:)"
    opportunities_pattern = r"(?<=Opportunities:).*?(?=Threats:)"
    threats_pattern = r"(?<=Threats:).*?(?=Pestel Analysis:)"

    description_match = re.search(description_pattern, response, re.DOTALL)
    strengths_match = re.search(strengths_pattern, response, re.DOTALL)
    weaknesses_match = re.search(weaknesses_pattern, response, re.DOTALL)
    opportunities_match = re.search(opportunities_pattern, response, re.DOTALL)
    threats_match = re.search(threats_pattern, response, re.DOTALL)

    return {
        "description": description_match.group(0).strip() if description_match else "",
        "strengths": strengths_match.group(0).strip() if strengths_match else "",
        "weaknesses": weaknesses_match.group(0).strip() if weaknesses_match else "",
        "opportunities": opportunities_match.group(0).strip() if opportunities_match else "",
        "threats": threats_match.group(0).strip() if threats_match else "",
    }

def parse_pestel(response):
    political_pattern = r"(?<=Political:).*?(?=Economical:)"
    econimical_pattern = r"(?<=Economical:).*?(?=Social:)"
    social_pattern = r"(?<=Social:).*?(?=Technological:)"
    technological_pattern = r"(?<=Technological:).*?(?=Environmental:)"
    environmental_pattern = r"(?<=Environmental:).*?(?=Local:)"
    local_pattern = r"(?<=Local:).*"

    political_match = re.search(political_pattern, response, re.DOTALL)
    econimical_match = re.search(econimical_pattern, response, re.DOTALL)
    social_match = re.search(social_pattern, response, re.DOTALL)
    technological_match = re.search(technological_pattern, response, re.DOTALL)
    environmental_match = re.search(environmental_pattern, response, re.DOTALL)
    local_match = re.search(local_pattern, response, re.DOTALL)

    return {
        "Political": political_match.group(0).strip() if political_match else "",
        "Economical": econimical_match.group(0).strip() if econimical_match else "",
        "Social": social_match.group(0).strip() if social_match else "",
        "Technological": technological_match.group(0).strip() if technological_match else "",
        "Environmental": environmental_match.group(0).strip() if environmental_match else "",
        "Local": local_match.group(0).strip() if local_match else "",
    }
    
def parse_target(response):
    best_practices_pattern = r"(?<=Best Practices:).*?(?=Improve First:)"
    improve_first_pattern = r"(?<=Improve First:).*?(?=Poor Prospects:)"
    poor_prospects_pattern = r"(?<=Poor Prospects:).*?(?=Worst Prospects:)"
    worst_prospects_pattern = r"(?<=Worst Prospects:).*"

    best_practices_match = re.search(best_practices_pattern, response, re.DOTALL)
    improve_first_match = re.search(improve_first_pattern, response, re.DOTALL)
    poor_prospects_match = re.search(poor_prospects_pattern, response, re.DOTALL)
    worst_prospects_match = re.search(worst_prospects_pattern, response, re.DOTALL)

    return {
        "best_practices": best_practices_match.group(0).strip() if best_practices_match else "",
        "improve_first": improve_first_match.group(0).strip() if improve_first_match else "",
        "poor_prospects": poor_prospects_match.group(0).strip() if poor_prospects_match else "",
        "worst_prospects": worst_prospects_match.group(0).strip() if worst_prospects_match else "",
    }

@app.route('/generate-ideas', methods=['POST'])
def generate_ideas():
    data = request.json
    location = data.get("location")
    skills = data.get("skills")
    interests = data.get("interests")
    specific_area = data.get("specific_area")
    resources = data.get("resources")
    additional_section = data.get("additionalSections")

    prompt = f"""
    User is in {location}.
    They have skills: {skills}.
    Their interests are: {interests}.
    They have in mind: {specific_area}.
    Their resources include: {resources}.
    And additional information about user : {additional_section}

    Provide a set of exact 5 business startup ideas suitable for this user. Keep the answers little descriptive and conversational. Offer to help with designing their service or product offering after they choose an option.
    """
    print(additional_section)
    messages.append({"role": "user", "content": prompt})
    response = generate_chat_response(messages)
    headlines, content = parse_ideas(response)
    
    # global_headlines.extend(headlines)
    # global_content.extend(content)
    
    global_headlines = headlines[:5]
    global_content = content[:5]
    
    return jsonify({
        "headlines": global_headlines,
        "content": global_content
    })


@app.route('/generate-swot', methods=['POST'])
def generate_swot():
    data = request.json
    headline = data.get("headline")
    content = data.get("content")

    prompt = f"""
    Analyze the following business idea:
    {headline}
    {content}
    
    Provide a detailed description and SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) of the idea. Must ensure that the Strengths, Weaknesses, Opportunities, Threats must contain less than 30 words. Description must contain more than 80 words.

    Format the response as follows:
    Description:
    <Your description here>

    Strengths:
    <Your strengths here>

    Weaknesses:
    <Your weaknesses here>

    Opportunities:
    <Your opportunities here>

    Threats:
    <Your threats here>
    
    Provide a detailed description and Pestel analysis (Political, Economical, Social, Technological, Environmental, Local) of the idea. Each point except description contains not more than 20 words.

    Format the response as follows:
    Political:
    <Your description here>

    Economical:
    <Your strengths here>

    Social:
    <Your weaknesses here>

    Technological:
    <Your opportunities here>

    Environmental:
    <Your threats here>
    
    Local:
    <Your threats here>
    
    """

    messages.append({"role": "user", "content": prompt})
    response = generate_chat_response(messages)
    swot_analysis = parse_swot(response)
    pestel_analysis = parse_pestel(response)
    
    return jsonify({
        "description": swot_analysis['description'],
        "swot": {
            "strengths": swot_analysis['strengths'],
            "weaknesses": swot_analysis['weaknesses'],
            "opportunities": swot_analysis['opportunities'],
            "threats": swot_analysis['threats']
        },
        "pestel":{
            "Political": pestel_analysis['Political'],
            "Economical": pestel_analysis['Economical'],
            "Social": pestel_analysis['Social'],
            "Technological": pestel_analysis['Technological'],
            "Environmental": pestel_analysis['Environmental'],
            "Local": pestel_analysis['Local'],
        }
    })
@app.route('/generate-strategy', methods=['POST'])
def generate_strategy():
    data = request.json
    location = data.get("location")
    detailed_location = data.get("detailed_location")
    skills = data.get("skills")
    interests = data.get("interests")
    additional_sections = data.get("additionalSections")
    resources = data.get("resources")
    print(data)

    prompt = f"""
    The user is located in {location}, specifically {detailed_location}.
    They have the following skills: {skills}.
    Their interests include: {interests}.
    Their resources are: {resources}.
    Additional sections provided are: {additional_sections}.
    
    Please provide a dynamic analysis of the target market. Include the following:
    - Best Practices
    - Improve First
    - Poor Prospects
    - Worst Prospects
    
    Format the response as follows:
    Best Practices:
    <Your description here>

    Improve First:
    <Your strengths here>

    Poor Prospects:
    <Your weaknesses here>

    Worst Prospects:
    <Your opportunities here>
    
    Each category should include a descriptive analysis and strategic suggestions. The content should be tailored to the user’s specific context and inputs.
    """

    messages.append({"role": "user", "content": prompt})
    response = generate_chat_response(messages)
    print(response)
    target = parse_target(response)

    # Return the response elements as individual JSON keys
    return jsonify({
        "bestPractices": target['best_practices'],
        "improveFirst": target['improve_first'],
        "poorProspects": target['poor_prospects'],
        "worstProspects": target['worst_prospects']
    })



if __name__ == '__main__':
    app.run(debug=True)
