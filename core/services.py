# services.py


from django.conf import settings

from .models import TamsTeam

import os, requests


class PhaseOrchestrator:

    @staticmethod
    def verify_team_registration(team_code, event_name):
        """Checks if the team_code is registered for the given event_name."""

        return TamsTeam.objects.filter(team_code = team_code, event_name = event_name).exists()
    
    @staticmethod
    def run_phase_transition(event_name):
        """Router: Fetches Kahoot scores & delegates to the correct Phase 2 logic."""

        kahoot_url = os.environ.get('KAHOOT_SERVICE_URL', 'http://127.0.0.1:8000')

        headers = {'X-Kahoot-API-Key' : getattr(settings, 'KAHOOT_SECRET_KEY', '')}
        response = requests.get(f'{kahoot_url}/api/export-scores/{event_name}/', headers = headers)

        if not response.ok:

            return False, f"Kahoot Error: {response.text}"

        kahoot_data = response.json()
        scores = kahoot_data.get('scores', [])

        if event_name == 'bid2build':

            return PhaseOrchestrator._process_bid2build(scores)
        else:

            return False, f"No transition logic defined for event: {event_name}"

    @staticmethod
    def _process_bid2build(scores):
        """Specific B2B wallet math & payload injection."""

        b2b_url = os.environ.get('B2B_SERVICE_URL', 'http://127.0.0.1:8000')

        wallets = []
        bonus_tiers = [(1, 5, 200), (6, 15, 175), (16, 30, 150), (31, 50, 100), (51, 70, 50), (71, 90, 25)]

        for rank, team_data in enumerate(scores, start = 1):
            if rank > 90:
                break

            base = 1000
            bonus = next((b for min_r, max_r, b in bonus_tiers if min_r <= rank <= max_r), 0)

            team_obj = TamsTeam.objects.filter(team_code = team_data['team_code']).first()
            team_name = team_obj.name if team_obj else team_data['team_code'] # Fallback to team_code if the team somehow bypassed global registration

            wallets.append({'team_code' : team_data['team_code'], 'team_name' : team_name, 'starting_balance' : base + bonus})

        b2b_headers = {'X-Host-Secret' : getattr(settings, 'B2B_HOST_SECRET', '')}
        b2b_payload = {'wallets' : wallets}
        b2b_response = requests.post(f'{b2b_url}/api/admin/sync-wallets/', json = b2b_payload, headers = b2b_headers)

        if not b2b_response.ok:

            return False, f"B2B Error: {b2b_response.text}"

        return True, "Phase 1 complete. B2B wallets successfully synced."
