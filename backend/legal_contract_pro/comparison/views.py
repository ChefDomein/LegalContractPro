from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import difflib

@csrf_exempt
@require_http_methods(["POST"])
def compare_contracts(request):
    try:
        data = json.loads(request.body)
        contract1 = data.get('contract1', '')
        contract2 = data.get('contract2', '')

        if not contract1 or not contract2:
            return JsonResponse({'error': 'Both contracts are required for comparison'}, status=400)

        # Split the contracts into lines
        lines1 = contract1.splitlines()
        lines2 = contract2.splitlines()

        # Create a differ object
        differ = difflib.Differ()

        # Compare the lines
        diff = list(differ.compare(lines1, lines2))

        # Process the diff to create a more structured output
        structured_diff = []
        for line in diff:
            if line.startswith('  '):  # Unchanged
                structured_diff.append({'type': 'unchanged', 'text': line[2:]})
            elif line.startswith('- '):  # Removed
                structured_diff.append({'type': 'removed', 'text': line[2:]})
            elif line.startswith('+ '):  # Added
                structured_diff.append({'type': 'added', 'text': line[2:]})

        return JsonResponse({'diff': structured_diff})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
