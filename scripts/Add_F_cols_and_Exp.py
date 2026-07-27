# CREATES THE LIST OF JOBS FROM THE DB
import sqlite3

from Repo_root import JOBS_DB
from Exp_db_to_Excel import Exp_db_to_Excel_conn

import Update_flags

filter_cols = ",\n       ".join(
    f"{expr} AS {name}"
    for name, expr in Update_flags.filters.items() )

def add_cols_and_exp(input_db):
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TEMP TABLE WD_jobs AS
    SELECT *
            ,{filter_cols}
            ,{Update_flags.hard_skills} as Skills
            ,instr(LOWER(description),'python')>0         AS python
            ,instr(description,'SAS')>0                   AS sas
            ,instr(LOWER(description),'viya')>0           AS viya
            ,instr(LOWER(description),'spark')>0          AS spark
            ,instr(LOWER(description),'databricks')>0     AS databricks
            ,instr(LOWER(description),'database')>0       AS database_,
            ,instr(LOWER(description),'hive')>0           AS hive
            ,instr(LOWER(description),'dremio')>0         AS dremio
            ,instr(LOWER(description),'oracle')>0         AS oracle_
            ,instr(LOWER(description),'teradata')>0       AS teradata
            ,instr(LOWER(description),'sql')>0            AS sql_
            ,instr(LOWER(description),'db2')>0            AS db2
            ,instr(LOWER(description),'mainframe')>0      AS mainframe
            ,instr(LOWER(description),'data warehouse')>0 AS data_warehouse
            ,instr(LOWER(description),'snowflake')>0      AS snowflake
            ,instr(LOWER(description),'hadoop')>0         AS hadoop
            ,instr(LOWER(description),'etl')>0            AS etl
            ,instr(LOWER(description),'pandas')>0         AS pandas
            ,instr(LOWER(description),'statistics')>0     AS statistics
            ,instr(LOWER(description),'predictive')>0     AS predictive
            ,instr(LOWER(description),'power bi')>0       AS power_bi
            ,instr(LOWER(description),'analytics')>0      AS analytics
            ,instr(LOWER(description),'reports')>0        AS reports
            ,instr(LOWER(description),'reporting')>0      AS reporting
            ,instr(LOWER(description),'vba')>0            AS vba
            ,instr(LOWER(description),'excel')>0          AS excel
            ,instr(LOWER(description),'git')>0            AS git
            ,instr(LOWER(description),'github')>0         AS github
            ,instr(LOWER(description),'json')>0           AS json
            ,instr(LOWER(description),'xml')>0            AS xml
            ,instr(LOWER(description),'a&h')>0            AS a_h
            ,instr(LOWER(description),'p&c')>0            AS p_c
            ,instr(LOWER(description),'loss triangle')>0  AS loss_triangle
            ,instr(LOWER(description),' aml ')>0          AS aml
            ,instr(LOWER(description),' kyc ')>0          AS kyc
            ,instr(LOWER(description),' cdd ')>0          AS cdd
            ,instr(LOWER(description),' fcc ')>0          AS fcc
    FROM new_jobs
    WHERE platform = 'lever'
    """)

    # Export temp table to Excel here
    Exp_db_to_Excel_conn(conn,"WD_jobs","(Expanded-new)","")
    # THE END
    conn.close()

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
if __name__ == "__main__":
    new_jobs_count = add_cols_and_exp(JOBS_DB)
