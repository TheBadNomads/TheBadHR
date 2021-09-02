import os

class Channels:

    LeaveApprovalsChannel = None

    @staticmethod
    def GetLeaveApprovalsChannel(client):
        if(Channels.LeaveApprovalsChannel == None):
            Channels.LeaveApprovalsChannel = client.get_channel(int(os.getenv("TestChannel_id")))

        return Channels.LeaveApprovalsChannel