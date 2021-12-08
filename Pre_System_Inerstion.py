from datetime import datetime, timedelta
import Utilities
import pandas as pd

from Member import member_db 
from Leave import leave_interface, leave_db

data = pd.read_excel (r'Leaves_Modified.xlsx')
data_dic = data.T.to_dict().values()

for record in data_dic:
    member_leaves_dates = Utilities.GetDatesOfLeaves(leave_db.GetLeavesByMemberID(record["Member_ID"]))
    first_date = member_db.GetMemberByID(record["Member_ID"])["start_date"]
    counter = 0
    days_count = record["Days_Count"]
    while counter < days_count:
        date = first_date + timedelta(days = counter)
        counter += 1
        if(date in member_leaves_dates):
            days_count += 1
            continue
        print(leave_db.InsertLeave(record["Member_ID"], -1, record["Leave_Type"], date, "", "", "Approved", record["Is_Emergency"], record["Is_Unpaid"]))
