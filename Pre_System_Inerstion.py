import pandas as pd

from datetime import datetime
from Leave import leave_db, leave_interface

path = input("Please enter the path of your csv file:\n")
data = pd.read_csv(path)
data_dic = data.iterrows()
members_dic = {
    "Ant"     : 158010930200838144,
    "Amr"     : 487749805636976651,
    "Alex"    : 475048962869428250,
    "Abdo"    : 202837588397129728,
    "Alberto" : 155752025798344704,
    "Noah"    : 252146643388858370,
    "Moody"   : 855503936365920296,
    "Hawas"   : 504953339067498496,
    "Brian"   : 174932293134188544,
    "Omar"    : 757347719135363192
}
leave_types = ["Emergency Leave", "Leave"]
date = datetime(2021, 12, 1)
automatic_leave_id = -1
is_emergency = False
for record in data_dic:
    if record[0] == "":
        continue

    if record[0] == "Total Leaves":
        break
    
    if record[0] in leave_types:
        is_emergency = False
        if record[0] == "Emergency Leave":
            is_emergency = True

    if record[0] in members_dic:
        days_count = record[11]
        member_id = members_dic[record[0]]
        for counter in range(days_count):
            leave_interface.AddRetroactiveLeaveToDB(member_id, automatic_leave_id, date, date, "Annual", "Approved", "", is_emergency, None)
