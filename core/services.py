# services.py


from django.conf import settings
from django.db import IntegrityError

from .models import School, TamsTeam

import logging, os, requests, secrets, string


logger = logging.getLogger(__name__)


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

            return PhaseOrchestrator._process_bid2build(scores, event_name)
        else:

            return False, f"No transition logic defined for event: {event_name}"

    @staticmethod
    def _process_bid2build(scores, event_name):
        """Specific B2B wallet math & payload injection."""

        registered_teams = TamsTeam.objects.filter(event_name = event_name)

        b2b_url = os.environ.get('B2B_SERVICE_URL', 'http://127.0.0.1:8000')

        wallets = []
        bonus_tiers = [(1, 5, 200), (6, 15, 175), (16, 30, 150), (31, 50, 100), (51, 70, 50), (71, 90, 25)]

        for rank, team_data in enumerate(scores, start = 1):
            if rank > 90:
                break

            base = 1000
            
            bonus = next((b for min_r, max_r, b in bonus_tiers if min_r <= rank <= max_r), 0)

            team_obj = registered_teams.filter(team_code = team_data['team_code']).first()
            team_name = team_obj.name if team_obj else team_data['team_code'] # Fallback to team_code if the team somehow bypassed global registration

            wallets.append({'team_code' : team_data['team_code'], 'team_name' : team_name, 'starting_balance' : base + bonus})

        b2b_headers = {'X-Host-Secret' : getattr(settings, 'B2B_HOST_SECRET', '')}
        b2b_payload = {'wallets' : wallets}
        b2b_response = requests.post(f'{b2b_url}/api/admin/sync-wallets/', json = b2b_payload, headers = b2b_headers)

        if not b2b_response.ok:

            return False, f"B2B Error: {b2b_response.text}"

        return True, "Phase 1 complete. B2B wallets successfully synced."


class IdentityManager:

    @staticmethod
    def generate_secure_code(length = 6):
        alphabet = string.ascii_uppercase + string.digits

        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def register_team(team_name, school_id, event_name):
        """Registers a team, generating a unique code for the specific event."""

        try:
            school = School.objects.get(id = school_id)
        except School.DoesNotExist:

            return None, "Invalid School ID."

        max_retries = 5

        for _ in range(max_retries):
            # Will trigger IntegrityErr if (team_code, event_name) constraint is violated.
            team_code = IdentityManager.generate_secure_code()

            try:
                team = TamsTeam.objects.create(team_code = team_code, name = team_name, school = school, event_name = event_name)

                return team, 'Success'
            except IntegrityError:
                continue # Loop & try again with a new code

        return None, "Failed to generate a unique team code after maximum retries."
