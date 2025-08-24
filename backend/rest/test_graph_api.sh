#!/bin/bash

# Graph API Testing Script

BASE_URL="http://127.0.0.1:8000"
ROOT_ENTITY_ID="0728d481-9f62-4509-aed8-acc96b21b51f"

# Test 1: Get full graph (all entities and relationships)
echo "=== Test 1: Get full graph ==="
curl -X GET "$BASE_URL/graph" -H "Content-Type: application/json"
echo -e "\n"

# Test 2: Get full graph with limits
echo "=== Test 2: Get full graph with limits ==="
curl -X GET "$BASE_URL/graph?limit_nodes=100&limit_edges=200" -H "Content-Type: application/json"
echo -e "\n"

# Test 3: Get graph without extradata
echo "=== Test 3: Get graph without extradata ==="
curl -X GET "$BASE_URL/graph?include_extradata=false" -H "Content-Type: application/json"
echo -e "\n"

# Test 4: Get graph filtered by relationship type
echo "=== Test 4: Get graph filtered by relationship type ==="
curl -X GET "$BASE_URL/graph?relationship_type=works_at" -H "Content-Type: application/json"
echo -e "\n"

# Test 5: Get graph by entity type
echo "=== Test 5: Get graph by entity type ==="
curl -X GET "$BASE_URL/graph?scope=by_type&entity_type=person" -H "Content-Type: application/json"
echo -e "\n"

# Test 6: Get graph by entity type with relationship filter
echo "=== Test 6: Get graph by entity type with relationship filter ==="
curl -X GET "$BASE_URL/graph?scope=by_type&entity_type=person&relationship_type=works_at" -H "Content-Type: application/json"
echo -e "\n"

# Test 7: Get neighborhood graph around a specific entity
echo "=== Test 7: Get neighborhood graph around a specific entity ==="
curl -X GET "$BASE_URL/graph?scope=neighborhood&root_id=$ROOT_ENTITY_ID" -H "Content-Type: application/json"
echo -e "\n"

# Test 8: Get neighborhood graph with depth
echo "=== Test 8: Get neighborhood graph with depth ==="
curl -X GET "$BASE_URL/graph?scope=neighborhood&root_id=$ROOT_ENTITY_ID&depth=2" -H "Content-Type: application/json"
echo -e "\n"

# Test 9: Get neighborhood graph with relationship filter
echo "=== Test 9: Get neighborhood graph with relationship filter ==="
curl -X GET "$BASE_URL/graph?scope=neighborhood&root_id=$ROOT_ENTITY_ID&relationship_type=works_at" -H "Content-Type: application/json"
echo -e "\n"

# Test 10: Get neighborhood graph with limits
echo "=== Test 10: Get neighborhood graph with limits ==="
curl -X GET "$BASE_URL/graph?scope=neighborhood&root_id=$ROOT_ENTITY_ID&limit_nodes=50&limit_edges=100" -H "Content-Type: application/json"
echo -e "\n"

# Error test cases

# Error Test 1: by_type scope without entity_type
echo "=== Error Test 1: by_type scope without entity_type ==="
curl -X GET "$BASE_URL/graph?scope=by_type" -H "Content-Type: application/json"
echo -e "\n"

# Error Test 2: neighborhood scope without root_id
echo "=== Error Test 2: neighborhood scope without root_id ==="
curl -X GET "$BASE_URL/graph?scope=neighborhood" -H "Content-Type: application/json"
echo -e "\n"

# Error Test 3: invalid scope
echo "=== Error Test 3: invalid scope ==="
curl -X GET "$BASE_URL/graph?scope=invalid_scope" -H "Content-Type: application/json"
echo -e "\n"

# Error Test 4: invalid UUID for root_id
echo "=== Error Test 4: invalid UUID for root_id ==="
curl -X GET "$BASE_URL/graph?scope=neighborhood&root_id=invalid-uuid" -H "Content-Type: application/json"
echo -e "\n"

echo "All tests completed!"
