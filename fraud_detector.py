import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# 1. Load the credentials
load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PWD = os.getenv("NEO4J_PASSWORD")

class FraudDetector:
    def __init__(self, uri, user, password):
        # Initialize the connection to Neo4j
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def find_shared_pii(self):
        """
        The 'Smoking Gun' Query:
        Finds different Customers who share the same Phone number.
        """
        query = """
        MATCH (c1:Customer)-[:HAS_PHONE]->(p:Phone)<-[:HAS_PHONE]-(c2:Customer)
        WHERE c1.id < c2.id
        RETURN c1.name AS Customer1, c2.name AS Customer2, p.value AS SharedPhone
        """
        with self.driver.session() as session:
            result = session.run(query)
            records = list(result)
            
            if not records:
                print("No fraud rings detected. The data looks clean.")
            else:
                print(f"--- ALERT: {len(records)} POTENTIAL FRAUD LINK(S) FOUND ---")
                for record in records:
                    print(f"MATCH: {record['Customer1']} and {record['Customer2']} both use {record['SharedPhone']}")

if __name__ == "__main__":
    # Initialize and run the detector
    detector = FraudDetector(URI, USER, PWD)
    try:
        detector.find_shared_pii()
    finally:
        detector.close()