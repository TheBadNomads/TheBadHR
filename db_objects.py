class user:
    def __init__(self, attrs):
        self.id = attrs[0]
        self.first_name = attrs[1]
        self.last_name = attrs[2]
        self.discord_id = attrs[3]
        self.annualBalance = attrs[4]
        self.emergencyBalance = attrs[5]
        self.sickBalance = attrs[6]

class leave:
    def __init__(self, attrs):
        self.id = attrs[0]
        self.user_id = attrs[1]
        self.leave_type = attrs[2]
        self.request_id = attrs[3]
        self.leave_status = attrs[4]
        self.start_date = attrs[5]
        self.end_date = attrs[6]
        self.requested_days = attrs[7]