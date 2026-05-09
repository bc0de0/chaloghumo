from sqlalchemy import text
from typing import List, UUID
from core.database import SessionLocal

class PostgresService:
    """
    Lightweight service for executing dynamically generated relational queries.
    Focuses on candidate pruning based on hard constraints.
    """

    async def fetch_candidate_ids(self, sql_query: str) -> List[UUID]:
        """
        Executes a pruned SQL query and returns a list of matching Destination IDs.
        """
        try:
            db = SessionLocal()
            # Safety check: Ensure only SELECT statements are executed
            if not sql_query.strip().upper().startswith("SELECT"):
                print(f"SECURITY ALERT: Non-SELECT query blocked: {sql_query}")
                return []

            result = db.execute(text(sql_query))
            ids = [row[0] for row in result]
            db.close()
            return ids
        except Exception as e:
            print(f"Postgres Query Error: {e}")
            return []

postgres_service = PostgresService()
