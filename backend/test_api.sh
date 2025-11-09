#!/bin/bash
# Script de prueba para el Deep Agent API

echo "=== Deep Agent Chatbot - Test Suite ==="
echo ""

echo "1. Health Check"
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
echo -e "\n"

echo "2. Simple Question"
curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is it?", "thread_id": "demo"}' | python3 -m json.tool
echo -e "\n"

echo "3. Calculation"
curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 15 percent of 500", "thread_id": "demo"}' | python3 -m json.tool
echo -e "\n"

echo "4. Create Plan"
curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Use create_plan to plan these steps: Research topic, Write summary, Save report", "thread_id": "plan_demo"}' | python3 -m json.tool
echo -e "\n"

echo "5. View Plan"
curl -s http://127.0.0.1:8000/plan | python3 -m json.tool
echo -e "\n"

echo "6. List Notes"
curl -s http://127.0.0.1:8000/notes | python3 -m json.tool

