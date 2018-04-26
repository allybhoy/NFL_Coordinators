#-------------------------------------------------------------------------------
# Name:        OCvsDC
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
    matchup_count = 0
    offensive_coord = defaultdict(lambda: defaultdict(list))
    # execute our first query (selecting all the current oc)
    cur_oc.execute("SELECT coach,team,style FROM coaches_career WHERE season_year = 2018 AND coach_position = 'OC'")
    oc = cur_oc.fetchall()
    # loop over them
    for currentoc in oc:
        # print currentoc
        oc_name = currentoc[0].strip()
        oc_team = currentoc[1].strip()
        oc_style = currentoc[2].strip()
        offensive_coord[oc_name][oc_team].append(oc_style)
    ##select all the teams available in nfldb team table
    opponents_by_team = defaultdict(lambda: defaultdict(list))
    ##select all the teams available in nfldb team table
    cur_team.execute("SELECT team_id FROM team")
    # print("The number of parts: ", cur_team.rowcount)
    ##take each team and list the upoming opponents using the sql below
    team = cur_team.fetchone()
    while team is not None:
        #print team
        opponent_sql = "WITH tbl1 AS\
        (SELECT coach,coach_id,team,style \
        FROM coaches_career \
        WHERE coach_position = 'DC' AND season_year =2018),tbl2 AS\
        (SELECT *,CASE WHEN home_team = %s THEN away_team WHEN away_team = %s THEN home_team\
        END AS opponent\
        FROM temp_2018_schedule\
        WHERE season_type = 'Regular' AND season_year = 2018 AND (home_team = %s or away_team = %s)),\
        tbl3 AS (SELECT opponent,coach,team,style \
        FROM tbl2,tbl1\
        WHERE tbl2.opponent = tbl1.team\
        GROUP BY opponent,coach,team,style)\
        SELECT * FROM tbl3"

        cur_opp.execute(opponent_sql, (team, team, team, team,))
        opponent_row = cur_opp.fetchone()
        while opponent_row is not None:
            octeam = team[0]
            dcteam = opponent_row[0].strip()
            dcname = opponent_row[1].strip()
            dcstyle = opponent_row[3].strip()
            # print octeam,dcteam,dcname,dcstyle
            opponents_by_team[octeam][dcteam].append(dcname)
            opponents_by_team[octeam][dcteam].append(dcstyle)
            opponent_row = cur_opp.fetchone()
        team = cur_team.fetchone()
    cur_team.close()
    cur_opp.close()
    ###################LOOPING THE OCS#########################
    # First loop goes through the current ocs- i is the current_oc name
    for i in offensive_coord:
        print i
        ##open the database connection and two query cursors (team and opp)
        cur_matchup = conn.cursor()
        cur_matchup_query = conn.cursor()
        cur_generic = conn.cursor()
        for j in offensive_coord[i]:
            # j is the oc team
            outputfile = open('c://temp/nfl/text_files/matchups/matchups' + i + '_' + j + '.csv', 'wb')
            #outputfile = open('c://temp/nfl/text_files/Allmatchups.csv', 'wb')
            # create a file to take the output
            outputfile.write("team,off_coach,off_style,opp,def_coach,def_style,position,touches,targets,carries,rec_yds,rush_yds,hth" + '\n')
            oc_style = offensive_coord[i][j][0]
            #print i, j, oc_style
            ####loop over the opponents###
            for key in opponents_by_team[j]:
                # key is the dcteam
                currentocname = str(i)
                currentdcname = str(opponents_by_team[j][key][0])
                currentocstyle = str(oc_style)
                currentdcstyle = str(opponents_by_team[j][key][1])
                currentdcteam = str(key)
                currentocteam = '%s' % (j)
                ##print currentocname,currentocstyle,currentocteam,currentdcname,currentdcstyle,currentdcteam
                content = '%s,%s,%s,%s,%s,%s' % (currentocteam, currentocname, currentocstyle, currentdcteam, \
                                                 currentdcname, currentdcstyle)

                ##sql for oc vs dc
                sql_matchup = "SELECT season_position_rank,(round(AVG(touches),1))as touches,(round(AVG(rec_tar),1))as targets,\
                (round(AVG(att),1))as rushatt,(round(AVG(rec_yds),1))as recyds,(round(AVG(rush_yds),1))as rushyds \
                FROM play_distribution_new \
                WHERE season_type = 'Regular' AND ((home_oc = \'" + currentocname + "\'\
                AND away_dc = \'" + currentdcname + "\') \
                OR (away_oc = \'" + currentocname + "\'\
                AND home_dc = \'" + currentdcname + "\')) \
                GROUP BY season_position_rank \
                ORDER BY season_position_rank ASC"

                sql_generic_matchup = "SELECT season_position_rank,(round(AVG(touches),1))as touches,(round(AVG(rec_tar),1))as targets,\
                (round(AVG(att),1))as rushatt,(round(AVG(rec_yds),1))as recyds,(round(AVG(rush_yds),1))as rushyds \
                FROM play_distribution_new \
                WHERE season_type = 'Regular' AND ((home_oc = \'" + currentocname + "\' OR home_oc_style = \'" + currentocstyle + "\')\
                AND (away_dc = \'" + currentdcname + "\' OR away_dc_style =\'" + currentdcstyle + "\')) \
                OR ((away_oc = \'" + currentocname + "\' OR away_oc_style = \'" + currentocstyle + "\'\
                AND (home_dc = \'" + currentdcname + "\' OR home_dc_style =\'" + currentdcstyle + "\'))) \
                GROUP BY season_position_rank \
                ORDER BY season_position_rank ASC"

                sql_matchup_count = "SELECT COUNT(DISTINCT gsis_id) AS games\
                FROM play_distribution_coaches\
                WHERE ((home_oc = \'" + currentocname + "\' AND away_dc = \'" + currentdcname + "\' )\
                OR (away_oc = \'" + currentocname + "\' AND home_dc = \'" + currentdcname + "\'))"

                ##produces the matchup stats
                #cur_matchup.execute(sql_matchup)
                cur_matchup_query.execute(sql_matchup_count)
                # print("The number of parts: ", cur_matchup.rowcount)
                #matchup = cur_matchup.fetchone()
                countmatch = cur_matchup_query.fetchone()
                matchup_count = countmatch[0]
                if matchup_count > 2:
                    cur_matchup.execute(sql_matchup)
                    matchup = cur_matchup.fetchone()
                    while matchup is not None:
                        content2 = '%s,%s,%s,%s,%s,%s,%s,%s' % (content, matchup[0], matchup[1], matchup[2], matchup[3], matchup[4],matchup[5],countmatch[0])
                        outputfile.write(content2 + '\n')
                        matchup = cur_matchup.fetchone()
                else:
                    cur_generic.execute(sql_generic_matchup)
                    generic = cur_generic.fetchone()
                    while generic is not None:
                        content3 = '%s,%s,%s,%s,%s,%s,%s,%s' % (content, generic[0], generic[1], generic[2], generic[3], generic[4],generic[5],countmatch[0])
                        outputfile.write(content3 + '\n')
                        generic = cur_generic.fetchone()
                # loop over them
                #while matchup is not None:
                    #content2 = '%s,%s,%s,%s,%s,%s,%s,%s' % (content, matchup[0], matchup[1], matchup[2], matchup[3], matchup[4],matchup[5],countmatch[0])
                    #outputfile.write(content2 + '\n')
                    ##print matchup[1]
                    #matchup = cur_matchup.fetchone()

except psycopg2.DatabaseError, ex:
    print "I am unable to connect the database: " + str(ex)
    sys.exit(1)
    ##close the postgres cursors
    cur_matchup.close()
    curs_oc.close()
    cur_team.close()
    cur_opp.close()
##for i in ocdict:
##print i, ocdict[i][0]
##for j in oppdict:
##print j, oppdict[j]
#print opponents_by_team
#print offensive_coord
conn.close()