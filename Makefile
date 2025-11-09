.PHONY: start backend frontend install stop help

# Start both frontend and backend with reload (opens new terminal windows)
start:
	@echo "Starting Deep Chatbot (Frontend + Backend)..."
	@./dev.sh

# Start only backend with reload
backend:
	@echo "Starting backend with reload..."
	@cd backend && .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Start only frontend with reload
frontend:
	@echo "Starting frontend with reload..."
	@cd frontend && npm run dev

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	@cd backend && poetry install
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "Dependencies installed successfully!"

# Stop all running services
stop:
	@echo "Stopping services..."
	@pkill -f "uvicorn main:app" || true
	@pkill -f "vite" || true
	@echo "Services stopped"

# Show help
help:
	@echo "Deep Chatbot Development Commands:"
	@echo ""
	@echo "  make start     - Start both frontend and backend with reload"
	@echo "  make backend   - Start only backend with reload"
	@echo "  make frontend  - Start only frontend with reload"
	@echo "  make install   - Install all dependencies"
	@echo "  make stop      - Stop all running services"
	@echo "  make help      - Show this help message"
	@echo ""
	@echo "URLs:"
	@echo "  Backend:  http://127.0.0.1:8000"
	@echo "  Frontend: http://localhost:5173"
	@echo "  API Docs: http://127.0.0.1:8000/docs"
