#-------------------------------------------------------------------------------
# Name:        NFL Schedule
# Purpose:
#
# Author:      AlastairR
#
# Created:     07/03/2018
# Copyright:   (c) AlastairR 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
import psycopg2
import csv
from collections import defaultdict

conn = None
try:
    conn = psycopg2.connect("dbname= 'nfldb' user= 'nfldb' host = 'localhost' password ='nfldb'")
    # create the connection cursors to allow us query nfldb
    cur_oc = conn.cursor()
    cur_team = conn.cursor()
    cur_opp = conn.cursor()
    offensive_coord = defaultdict(lambda: defaultdict(list))
    ##select all the teams available in nfldb team table
    opponents_by_team = defaultdict(lambda: defaultdict(list))
    ##select all the teams available in nfldb team table
    cur_team.execute("SELECT team_id FROM team")
    # print("The number of parts: ", cur_team.rowcount)
    ##take each team and list the upoming opponents using the sql below
    team = cur_team.fetchone()
    while team is not None:
        print (team)
        opponent_sql = "SELECT week,home_team,away_team FROM temp_2018_schedule WHERE season_type = 'Regular' AND\
(home_team = %s OR away_team = %s)ORDER BY week ASC;"
        cur_opp.execute(opponent_sql, (team, team,))
        sched_row = cur_opp.fetchone()
        outputfile = open('c://temp/nfl/text_files/zschedule' + "".join(team) +'.csv', 'wb')
        #outputfile.write("week,opp" + '\n')
        while sched_row is not None:
            week = sched_row[0]
            hometeam = sched_row[1]
            awayteam = sched_row[2]
            s = ''.join(team)
            if hometeam == s :
                opp = awayteam
            else:
                opp = hometeam
            print opp
            print week,hometeam,awayteam
            contentshed = '%s,%s,%s' % (str(week),hometeam,awayteam)
            #contentshed = '%s,%s,%s' % (week,s,opp)
            outputfile.write(contentshed + '\n')
            sched_row = cur_opp.fetchone()
        team = cur_team.fetchone()
    cur_team.close()
    cur_opp.close()
except psycopg2.DatabaseError as ex:
    print ("I am unable to connect the database: ")+str(ex)
    sys.exit(1)
conn.close()
