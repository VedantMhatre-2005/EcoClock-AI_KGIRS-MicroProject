import pytest
from app.rag.query_validator import QueryValidator

def test_valid_cypher_read_queries():
    valid_query = "MATCH (b:Building) RETURN b.name, b.area_m2 LIMIT 10"
    is_valid, sanitized = QueryValidator.validate_cypher(valid_query)
    assert is_valid is True
    assert "LIMIT 10" in sanitized

def test_query_validator_appends_limit():
    query_without_limit = "MATCH (s:SDG) RETURN s.name"
    is_valid, sanitized = QueryValidator.validate_cypher(query_without_limit)
    assert is_valid is True
    assert "LIMIT 25" in sanitized

def test_reject_write_cypher():
    malicious_queries = [
        "CREATE (n:Building {name: 'Fake'})",
        "MATCH (n) DELETE n",
        "MATCH (b:Building) SET b.name = 'Hacked'",
        "DROP INDEX ON :Building(id)",
        "MATCH (n) REMOVE n.name",
        "CALL apoc.cypher.runSchema('DROP ALL')"
    ]
    for q in malicious_queries:
        is_valid, err = QueryValidator.validate_cypher(q)
        assert is_valid is False
        assert "violation" in err.lower() or "invalid" in err.lower()

