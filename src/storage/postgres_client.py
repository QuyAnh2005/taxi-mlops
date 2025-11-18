"""PostgreSQL client for metadata storage"""

import json
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ..config import settings


class PostgresClient:
    """Client for interacting with PostgreSQL database"""

    def __init__(self, connection_url: str | None = None):
        """
        Initialize PostgreSQL client

        Args:
            connection_url: PostgreSQL connection URL (default: from settings)
        """
        self.connection_url = connection_url or settings.postgres_url
        self.engine: Engine = create_engine(self.connection_url)

    def execute_query(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """
        Execute a SQL query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query result
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            conn.commit()
            return result

    def create_experiment_table(self) -> None:
        """Create experiment metadata table if it doesn't exist"""
        query = """
        CREATE TABLE IF NOT EXISTS experiment_metadata (
            id SERIAL PRIMARY KEY,
            experiment_id VARCHAR(255) UNIQUE NOT NULL,
            adapter_type VARCHAR(100) NOT NULL,
            parameters JSONB,
            metrics JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute_query(query)

    def save_experiment(
        self,
        experiment_id: str,
        adapter_type: str,
        parameters: dict[str, Any],
        metrics: dict[str, Any],
    ) -> None:
        """
        Save experiment metadata

        Args:
            experiment_id: Unique experiment identifier
            adapter_type: Type of adapter used
            parameters: Experiment parameters
            metrics: Experiment metrics
        """
        self.create_experiment_table()
        query = """
        INSERT INTO experiment_metadata (experiment_id, adapter_type, parameters, metrics)
        VALUES (:experiment_id, :adapter_type, :parameters, :metrics)
        ON CONFLICT (experiment_id) 
        DO UPDATE SET 
            adapter_type = EXCLUDED.adapter_type,
            parameters = EXCLUDED.parameters,
            metrics = EXCLUDED.metrics,
            updated_at = CURRENT_TIMESTAMP;
        """
        self.execute_query(
            query,
            {
                "experiment_id": experiment_id,
                "adapter_type": adapter_type,
                "parameters": json.dumps(parameters),
                "metrics": json.dumps(metrics),
            },
        )

    def get_experiment(self, experiment_id: str) -> dict[str, Any] | None:
        """
        Get experiment metadata

        Args:
            experiment_id: Experiment identifier

        Returns:
            Experiment metadata or None if not found
        """
        query = """
        SELECT * FROM experiment_metadata 
        WHERE experiment_id = :experiment_id;
        """
        result = self.execute_query(query, {"experiment_id": experiment_id})
        row = result.fetchone()
        if row:
            return {
                "id": row[0],
                "experiment_id": row[1],
                "adapter_type": row[2],
                "parameters": row[3],
                "metrics": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }
        return None

    def list_experiments(self, adapter_type: str | None = None) -> list[dict[str, Any]]:
        """
        List all experiments

        Args:
            adapter_type: Filter by adapter type (optional)

        Returns:
            List of experiment metadata
        """
        if adapter_type:
            query = """
            SELECT * FROM experiment_metadata 
            WHERE adapter_type = :adapter_type
            ORDER BY created_at DESC;
            """
            result = self.execute_query(query, {"adapter_type": adapter_type})
        else:
            query = """
            SELECT * FROM experiment_metadata 
            ORDER BY created_at DESC;
            """
            result = self.execute_query(query)

        experiments = []
        for row in result:
            experiments.append(
                {
                    "id": row[0],
                    "experiment_id": row[1],
                    "adapter_type": row[2],
                    "parameters": row[3],
                    "metrics": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                }
            )
        return experiments

