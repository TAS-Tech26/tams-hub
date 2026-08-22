# views.py


from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import EventRoom, EventStanding, TamsTeam
from .serializers import ClientLoginSerializer
from .services import PhaseOrchestrator, IdentityManager

import datetime, hmac, json, jwt


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
def register_new_team(request):
    if not verify_hub_secret(request):

        return JsonResponse({'error' : "Unauthorized request"}, status = 403)

    try:
        data = json.loads(request.body)
        team_name = data.get('team_name')
        school_id = data.get('school_id')
        event_name = data.get('event_name')

        if not all([team_name, school_id, event_name]):

            return JsonResponse({'error' : "Missing required fields."}, status = 400)

        team, message = IdentityManager.register_team(team_name, school_id, event_name)

        if team:

            return JsonResponse({'message' : "Team registered successfully.", 'team_code' : team.team_code, 'event_name' : team.event_name}, status = 201)

        else:

            return JsonResponse({'error' : message}, status = 500)

    except json.JSONDecodeError:

        return JsonResponse({'error' : "Invalid JSON"}, status = 400)

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

        for res in results:
            code = res.get('team_code')
        
            team = TamsTeam.objects.filter(team_code = code, event_name = event_name).first()

            if team:
                EventStanding.objects.update_or_create(
                    team = team,
                    event_name = event_name,
                    defaults = {'rank' : res['rank'], 'final_score_or_assets' : str(res.get('assets', ''))}
                )

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

@csrf_exempt
@require_POST
def client_lobby_login(request):
    """Client-facing endpoint. Issues a JWT that encodes the team PIN within it. Other services can get the team PIN encoded within the JWT & verify the team making the req."""

    serializer = ClientLoginSerializer(request.body)

    if not serializer.is_valid():

        return JsonResponse({'error' : serializer.errors}, status = 400)

    data = serializer.validated_data

    room = EventRoom.objects.filter(room_code = data['room_code'], is_active = True).first()

    if not room:

        return JsonResponse({'error' : "Invalid or inactive room code."}, status = 403)

    team = TamsTeam.objects.filter(team_code = data['team_code'], event_name = room.event_name).first()

    if not team:

        return JsonResponse({'error' : "Invalid team PIN for this event."}, status = 403)

    token = jwt.encode({
        'team_code' : team.team_code,
        'event_name' : room.event_name,
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours = 12)
    }, settings.HUB_SECRET_KEY, algorithm = 'HS256')

    return JsonResponse({'token' : token, 'team_name' : team.name, 'event_name' : room.event_name}, status = 200)
    
