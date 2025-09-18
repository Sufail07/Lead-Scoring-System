from django.conf import settings
import google.generativeai as genai
from rest_framework import status
from rest_framework.response import Response

GEMINI_API_KEY = settings.GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
system_instruction = '''You are a lead qualification AI. Your task is to analyze a prospect's professional background against a product/offer and classify their buying intent as High, Medium, or Low. You must also provide a 1-2 sentence explanation for your classification.

Your final output must be strictly formatted as "Intent: [label]" and "Reasoning: [1-2 sentence explanation] The Intent and Reasoning must always be seperated by a \n".

You will always receive the offer and lead details in the following formats:

Offer Details:
* Offer Name
* Value Propositions
* Ideal Use Cases

Lead Details:
* Name
* Role
* Company
* Industry
* Location
* LinkedIn Bio' '''

model = genai.GenerativeModel(model_name='gemini-2.5-flash')
chat = model.start_chat(history=[
    {"role": "user", "parts": [system_instruction]}
])
'''
Helper function to calculate the rule points for a specific lead.
'''
def get_rule_points(lead):
    offer = lead.offer
    total_score = 0
    total_score += get_role_score(lead.role)
    total_score += get_industry_score(lead.industry, offer.ideal_use_cases)
    total_score += get_completeness_score(lead)
    return min(total_score, 50)

'''
Calculating role score for rule points. There are 2 scenarios where the lead can be given points for the role score. If the lead is a decision_maker or if the lead is an influencer. Points rewarded are 20 and 10 respectively.  
'''
def get_role_score(role):
    if not role:
        return 0
    decision_maker_keywords = ['ceo', 'cto', 'cfo', 'coo', 'president', 'founder', 'owner','vp', 'vice president', 'director', 'head of', 'chief']
    influencer_keywords = ['manager', 'lead', 'senior', 'principal', 'supervisor', 'team lead', 'coordinator']

    for keyword in decision_maker_keywords:
        if keyword in role.lower():
            return 20
    
    for keyword in influencer_keywords:
        if keyword in role.lower():
            return 10
    
    return 0

'''
Getting the industry score by checking if the industry of the lead matches with the use cases of offer.
'''
def get_industry_score(industry, use_cases):
    if not industry or use_cases:
        return 0
    
    # Check for exact match
    lead_industry_lower = industry.lower()
    for use_case in use_case:
        use_case_lower = use_case.lower()

        if lead_industry_lower in use_case_lower or use_case_lower in lead_industry_lower:
            return 20
        
    # Check for similar words
    for use_case in use_cases:
        use_case_lower = use_case.lower()
        if has_keyword_overlap(lead_industry_lower, use_case_lower):
            return 10
    
    return 0

'''
Similarity search of leads industry with the offers use cases is done by checking if the leads industry has any overlapping keyword with the use case of offer.
'''
def has_keyword_overlap(lead_industry, use_case):
    # Checking if the industry string of the lead has any overlapping word with the offer use cases to find similarity.
    industry_words = set(lead_industry.split())
    use_case_words = set(use_case.split())
    return bool(industry_words.intersection(use_case_words))

'''
Helper function to see if a lead has complete details. If so, 10 points are rewarded, else 0.
'''
def get_completeness_score(lead):
    required_fields = ['name', 'role', 'company', 'industry', 'location', 'linkedin_bio']
    for field in required_fields:
        value = getattr(lead, field, '')
        if not value:
            return 0
    return 10

'''
Function to get the AI response. The AI is fed with offer details and each lead details. Output is formatted as: Intent: [intent] Reasoning:[reason]. And the AI score is also calculated as well, as High, Medium, or Low. The output scoring is mapped to 50, 30 and 10 respectively.
'''
def get_ai_response(lead):
    offer = lead.offer
    offer_details = {
        'Offer name': offer.name,
        'Value Propositions': offer.value_props,
        'Ideal use cases': offer.ideal_use_cases
    }
    lead_details = {
        'Name': lead.name,
        'Role': lead.role,
        'Company': lead.company,
        'Industry': lead.industry,
        'Location': lead.location,
        'LinkedIn Bio': lead.linkedin_bio
    }
    response = chat.send_message(f'''Offer details: {offer_details}
                      Lead details: {lead_details}''')
    
    api_response = response.text
    if api_response:
        lines = api_response.split('\n')
        intent_line, reason_line = lines[0], lines[1]
        intent_value = intent_line.split(': ')[1]
        reason_value = reason_line.split(': ')[1]
        score_mapping = {'High': 50, 'Medium': 30, 'Low': 10}
        return {'Intent': intent_value, 'Reason': reason_value, 'AI_score': score_mapping[intent_value]}
    
    return Response({'error': "API call failed"}, status=status.HTTP_400_BAD_REQUEST)
