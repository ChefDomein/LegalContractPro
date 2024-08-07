from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import os
import re

# Create your views here.

@csrf_exempt
@require_http_methods(["POST"])
def analyze_contract(request):
    try:
        data = json.loads(request.body)
        contract_text = data.get('contract_text')
        language = data.get('language', 'en')  # Default to English if not specified

        if not contract_text:
            return JsonResponse({'error': 'No contract text provided'}, status=400)

        api_endpoint = "https://api.openai.com/v1/chat/completions"
        api_key = os.environ.get('OPENAI_API_KEY')

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        system_message = (
            "Je bent een juridische contractanalyse-assistent. Analyseer het volgende contract voor clausuleherkenning, "
            "risico-identificatie, inconsistenties en extractie van sleuteltermen. Formatteer je antwoord als volgt:\n\n"
            "CLAUSULEHERKENNING:\n[Lijst van herkende clausules]\n\n"
            "RISICO-IDENTIFICATIE:\n[Lijst van geïdentificeerde risico's]\n\n"
            "INCONSISTENTIES:\n[Lijst van eventuele inconsistenties]\n\n"
            "SLEUTELTERMEN:\n[Lijst van sleuteltermen]"
        ) if language == 'nl' else (
            "You are a legal contract analysis assistant. Analyze the following contract for clause recognition, "
            "risk identification, inconsistencies, and key terms extraction. Format your response as follows:\n\n"
            "CLAUSE RECOGNITION:\n[List recognized clauses]\n\n"
            "RISK IDENTIFICATION:\n[List identified risks]\n\n"
            "INCONSISTENCIES:\n[List any inconsistencies]\n\n"
            "KEY TERMS:\n[List key terms]"
        )

        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": contract_text}
            ]
        }

        response = requests.post(api_endpoint, headers=headers, json=payload)

        if response.status_code == 200:
            analysis_result = response.json()['choices'][0]['message']['content']
            return JsonResponse({
                'analysis': analysis_result,
                'clause_recognition': extract_clause_recognition(analysis_result, language),
                'risk_identification': extract_risk_identification(analysis_result, language),
                'inconsistencies': extract_inconsistencies(analysis_result, language),
                'key_terms': extract_key_terms(analysis_result, language)
            })
        else:
            return JsonResponse({'error': 'Failed to analyze contract'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def advanced_search(request):
    # Placeholder function for advanced search
    # This needs to be implemented without relying on the Contract model
    try:
        # Extract search parameters from the request
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        parties = request.GET.get('parties')
        clauses = request.GET.get('clauses')
        terms = request.GET.get('terms')

        # Placeholder: Return a message indicating that the search is not yet implemented
        return JsonResponse({
            'message': 'Advanced search is not yet implemented.',
            'search_params': {
                'date_from': date_from,
                'date_to': date_to,
                'parties': parties,
                'clauses': clauses,
                'terms': terms
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def extract_clause_recognition(analysis):
    clauses = re.search(r'CLAUSULE HERKENNING:\n(.*?)(?:\n\n|$)', analysis, re.DOTALL)
    if clauses:
        return [clause.strip() for clause in clauses.group(1).split('\n') if clause.strip()]
    return []

def extract_risk_identification(analysis):
    risks = re.search(r'RISICO IDENTIFICATIE:\n(.*?)(?:\n\n|$)', analysis, re.DOTALL)
    if risks:
        return [risk.strip() for risk in risks.group(1).split('\n') if risk.strip()]
    return []

def extract_inconsistencies(analysis):
    inconsistencies = re.search(r'INCONSISTENTIES:\n(.*?)(?:\n\n|$)', analysis, re.DOTALL)
    if inconsistencies:
        return [inconsistency.strip() for inconsistency in inconsistencies.group(1).split('\n') if inconsistency.strip()]
    return []

def extract_key_terms(analysis):
    terms = re.search(r'BELANGRIJKE TERMEN:\n(.*?)(?:\n\n|$)', analysis, re.DOTALL)
    if terms:
        return [term.strip() for term in terms.group(1).split('\n') if term.strip()]
    return []
