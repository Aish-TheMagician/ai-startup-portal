from flask import Flask, jsonify, request
import re
from groq import Groq
from flask_cors import CORS
import psycopg
from fastapi import FastAPI, Depends

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

messages = [
    {
        "role": "system",
        "content": "You are The Business Startup Portal (BSP), a tool to help people who want to start a business decide what that business could be, how to plan its development and get to launch. Be conversational yet professional, and lead the user step by step through the business startup cycle."
    },
]

def generate_chat_response(messages, model="llama3-8b-8192"):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
    )
    return chat_completion.choices[0].message.content

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
