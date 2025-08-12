# graph/neo4j_client.py
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
pw = os.getenv("NEO4J_PASSWORD", "neo4j")

def get_driver():
    return GraphDatabase.driver(uri, auth=(user, pw))

def add_wallet_relation(actor, wallet):
    driver = get_driver()
    with driver.session() as session:
        session.run(
            "MERGE (a:Actor {name:$actor}) "
            "MERGE (w:Wallet {addr:$wallet}) "
            "MERGE (a)-[:USES]->(w)",
            actor=actor, wallet=wallet
        )
    driver.close()
