
import json
from datetime import datetime
from neo4j import GraphDatabase
import os 

# === CONFIG ===
## Load JSON Credentials file
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..\config\credentials.json')
    with open(config_path, 'r') as f:
        return json.load(f)

config = load_config()

URI = config["neo4j_uri"]
USERNAME = config["neo4j_user"]
PASSWORD = config["neo4j_password"]
DATABASE = "ai-eng-worldfair"

# === LOAD JSON DATA FILE ===
jsondata_path = os.path.join(os.path.dirname(__file__), '..\data\worldeng2025.json')
with open(jsondata_path, "r", encoding="utf-8") as f:
    raw_json = f.read()

# Fix potential trailing comma issues
trimmed = raw_json.rsplit("}", 1)[0] + "}]"
sessions = json.loads(trimmed)

def normalize_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%d %b %Y %I:%M %p").isoformat()
    except:
        return None

def create_constraints(session):
    constraints = [
        "CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE",
        "CREATE CONSTRAINT speaker_name_unique IF NOT EXISTS FOR (sp:Speaker) REQUIRE sp.name IS UNIQUE",
        "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
        "CREATE CONSTRAINT track_name_unique IF NOT EXISTS FOR (t:Track) REQUIRE t.name IS UNIQUE",
        "CREATE CONSTRAINT room_name_unique IF NOT EXISTS FOR (r:Room) REQUIRE r.name IS UNIQUE",
        "CREATE CONSTRAINT time_unique IF NOT EXISTS FOR (ts:TimeSlot) REQUIRE ts.datetime IS UNIQUE"
    ]
    for c in constraints:
        session.run(c)

def main():
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    with driver.session(database=DATABASE) as session:
        create_constraints(session)

        for s in sessions:
            session_id = s.get("Session ID")
            title = s.get("Title")
            description = s.get("Description")
            session_format = s.get("Session Format")
            level = s.get("Level")
            scope = s.get("Scope")
            track = s.get("Assigned Track")
            room = s.get("Room")
            scheduled = normalize_datetime(s.get("Scheduled At", "").strip())
            speakers = [x.strip() for x in s.get("Speakers", "").split(",") if x.strip()]
            companies = [x.strip() for x in s.get("Companies", "").split(",") if x.strip()]
            domains = [x.strip() for x in s.get("Company Domains", "").split(",") if x.strip()]
            titles = [x.strip() for x in s.get("Titles", "").split(",") if x.strip()]

            cypher = '''
            MERGE (sess:Session {session_id: $session_id})
              SET sess.title = $title,
                  sess.description = $description,
                  sess.session_format = $session_format,
                  sess.level = $level,
                  sess.scope = $scope

            WITH sess
            OPTIONAL MATCH (sess)
            FOREACH (_ IN CASE WHEN $track <> "" THEN [1] ELSE [] END |
              MERGE (t:Track {name: $track})
              MERGE (sess)-[:PART_OF]->(t))

            FOREACH (_ IN CASE WHEN $room <> "" THEN [1] ELSE [] END |
              MERGE (r:Room {name: $room})
              MERGE (sess)-[:LOCATED_IN]->(r))

            FOREACH (_ IN CASE WHEN $scheduled IS NOT NULL THEN [1] ELSE [] END |
              MERGE (ts:TimeSlot {datetime: datetime($scheduled)})
              MERGE (sess)-[:SCHEDULED_AT]->(ts))

            WITH sess, $speakers AS speakers, $companies AS companies, $domains AS domains
            UNWIND range(0, size(speakers)-1) AS i
            WITH sess, speakers[i] AS speaker_name,
                       CASE WHEN i < size(companies) THEN companies[i] ELSE null END AS company_name,
                       CASE WHEN i < size(domains) THEN domains[i] ELSE null END AS domain

            MERGE (sp:Speaker {name: speaker_name})
            MERGE (sess)<-[:SPEAKS_AT]-(sp)

            FOREACH (_ IN CASE WHEN company_name IS NOT NULL AND company_name <> "" THEN [1] ELSE [] END |
              MERGE (c:Company {name: company_name})
              SET c.domain = domain
              MERGE (sp)-[:REPRESENTS]->(c))
            '''

            session.run(cypher, {
                "session_id": session_id,
                "title": title,
                "description": description,
                "session_format": session_format,
                "level": level,
                "scope": scope,
                "track": track,
                "room": room,
                "scheduled": scheduled,
                "speakers": speakers,
                "companies": companies,
                "domains": domains,
                "titles": titles
            })
    driver.close()

if __name__ == "__main__":
    main()
