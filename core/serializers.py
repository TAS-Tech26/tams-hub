# serializers.py


import json


class ClientLoginSerializer:

    def __init__(self, request_body):
        self.errors = None
        self.validated_data = None

        self._parse_and_validate(request_body)

    def _parse_and_validate(self, body):
        try:
            data = json.loads(body)
            room_code = data.get('room_code')
            team_code = data.get('team_code')

            if not all([room_code, team_code]):
                self.errors = "Missing credentials. Room code & PIN required."

                return

            self.validated_data = {'room_code' : str(room_code).strip(), 'team_code' : str(team_code).strip()}
        except (json.JSONDecodeError, ValueError):
            self.errors = "Invalid JSON format."

    def is_valid(self):

        return self.errors is None
