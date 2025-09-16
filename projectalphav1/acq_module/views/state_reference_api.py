from django.http import JsonResponse
from rest_framework.decorators import api_view
from core.models.assumptions import StateReference

@api_view(['GET'])
def get_judicial_states(request):
    """
    Returns a dictionary of all states with their judicial status
    Format: { 'NY': true, 'CA': false, ... }
    """
    # Query all state references and build a state_code -> judicial dictionary
    states_data = {}
    
    # Get all state references in a single efficient query
    state_refs = StateReference.objects.all().values('state_code', 'judicialvsnonjudicial')
    
    # Build the dictionary
    for state in state_refs:
        states_data[state['state_code']] = state['judicialvsnonjudicial']
    
    return JsonResponse({
        'states': states_data
    })
