import re
from typing import Tuple

FORBIDDEN_CYPHER_KEYWORDS = {
    "CREATE", "MERGE", "DELETE", "DETACH", "DROP", "SET", "REMOVE",
    "LOAD", "CSV", "CALL", "DBMS", "ALTER", "GRANT", "REVOKE", "INDEX", "CONSTRAINT"
}

ALLOWED_STARTING_KEYWORDS = {"MATCH", "WITH", "RETURN", "UNWIND", "OPTIONAL"}

class QueryValidator:
    @staticmethod
    def validate_cypher(cypher_query: str) -> Tuple[bool, str]:
        """
        Validates that a Cypher query is purely read-only and safe to execute.
        Returns: (is_valid, sanitized_or_error_message)
        """
        clean_q = cypher_query.strip().rstrip(";")
        if not clean_q:
            return False, "Query is empty."

        # Tokenize query removing quoted string literals to prevent injection inside quotes
        stripped_literals = re.sub(r"(['\"]).*?\1", "", clean_q)
        tokens = [t.upper() for t in re.findall(r'\b[A-Za-z_]+\b', stripped_literals)]

        if not tokens:
            return False, "Query contains no recognizable Cypher keywords."

        # Check first token
        if tokens[0] not in ALLOWED_STARTING_KEYWORDS:
            return False, f"Invalid read query start: '{tokens[0]}'. Cypher read queries must start with MATCH, OPTIONAL MATCH, or RETURN."

        # Check for forbidden mutations
        for token in tokens:
            if token in FORBIDDEN_CYPHER_KEYWORDS:
                return False, f"Security violation: Query contains write/administrative operation '{token}'. Only read-only operations permitted."

        # Check for APOC execution vectors
        if "APOC" in clean_q.upper():
            return False, "Security violation: APOC procedure execution not allowed in user queries."

        # Ensure reasonable LIMIT if not already present
        if "LIMIT" not in tokens and "COUNT(" not in clean_q.upper():
            clean_q += " LIMIT 25"

        return True, clean_q

