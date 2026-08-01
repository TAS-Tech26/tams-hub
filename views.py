# views.py


from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import EventStanding, School, TamsTeam
from .services import PhaseOrchestrator

import hmac, json, os


def verify_hub_secret(request):
    provided = request.headers.get('X-Hub-Secret', '')
    expected = settings.HUB_SECRET_KEY

    return expected and hmac.compare_digest(provided, expected)

@require_GET
def verify_team_code(request, team_code, event_name):
    """Endpoint for game systems to verify if a team code is registered for the given event name."""

    if not verify_hub_secret(request):

        return JsonResponse({'error' : "Unauthorized request."}, status = 403)

    is_valid = PhaseOrchestrator.verify_team_registration(team_code, event_name)

    if is_valid:

        return JsonResponse({'message' : f"Team code {team_code} is registered for event {event_name}."}, status = 200)
    else:

        return JsonResponse({'error' : f"Team code {team_code} is NOT registered for event {event_name}."}, status = 404)

@csrf_exempt
@require_POST
def trigger_phase_transition(request, event_name):
    """Hub pulls Kahoot data, calculates Phase 2 wallets/rules & pushes to target server"""

    if not verify_hub_secret(request):

        return JsonResponse({'error' : "Unauthorized admin action."}, status = 403)

    success, message = PhaseOrchestrator.run_phase_transition(event_name)

    return JsonResponse({'message' : message} if success else {'error' : message}, status = 200 if success else 400)

@csrf_exempt
@require_POST
def ingest_phase_2_results(request, event_name):
    """Input: Event hits this webhook when their game is fully over. Payload contains final ranks mapped to team_codes"""
    
    if not verify_hub_secret(request):

        return JsonResponse({'error' : "Unauthorized admin action."}, status = 403)

    try:
        data = json.loads(request.body)
        results = data.get('results', [])

        standings_to_create = []

        for res in results:
            code = res.get('team_code')
        
            team = TamsTeam.objects.filter(team_code = code).first()

            if team:
                standings_to_create.append(EventStanding(event_name = event_name, rank = res['rank'], team = team, final_score_or_assets = str(res.get('assets', ''))))

        EventStanding.objects.filter(event_name = event_name).delete()
        EventStanding.objects.bulk_create(standings_to_create)

        return JsonResponse({'message' : "Phase 2 results locked & saved."}, status = 200)
    except json.JSONDecodeError:

        return JsonResponse({'error' : "Invalid JSON."}, status = 400)

@require_GET
def export_event_standings(request, event_name):
    standings = EventStanding.objects.filter(event_name = event_name).select_related('team__school')

    if not standings.exists():

        return JsonResponse({'error' : "No final standings available for this event yet."}, status = 404)

    payload = [{
        'rank' : standing.rank,
        'team_name' : standing.team.name,
        'school_name' : standing.team.school.name,
        'team_code' : standing.team.team_code,
        'event_metric' : standing.final_score_or_assets
    } for standing in standings]

    return JsonResponse({'event_name' : event_name, 'leaderboard' : payload}, status = 200)