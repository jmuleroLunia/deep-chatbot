# Per-Thread Planning, Notes & Context

## Description
Implement per-thread isolation for plans, notes, and context. Currently, all threads share a single planning system (workspace/current_plan.json) and shared notes/context. This feature will make each thread have its own isolated plans, notes, and context stored in the database.

## Architecture Decision
- **Storage**: Database-based (SQLite) - new Plan, Note, and Context models
- **Isolation**: Full per-thread isolation for plans, notes, and context
- **Migration**: Start fresh, archive existing current_plan.json

## Tasks

### Task 1: Feature Tracking Document
- [x] Create funcionalidades/activas/per-thread-planning.md
- [x] Document implementation steps and acceptance criteria

### Task 2: Database Schema & Models
- [ ] Backend: Create Plan model in backend/models.py
  - Fields: id, thread_id (FK), task, steps (JSON), status, created_at, updated_at
  - Relationships: Plan belongs to Thread
- [ ] Backend: Create Note model in backend/models.py
  - Fields: id, thread_id (FK), filename, content, created_at, updated_at
  - Relationships: Note belongs to Thread
- [ ] Backend: Create Context model in backend/models.py (if needed)
  - Fields: id, thread_id (FK), key, value (JSON), created_at, updated_at
  - Relationships: Context belongs to Thread
- [ ] Backend: Create Alembic migration script
- [ ] Testing: Run migration and verify tables in threads.db

### Task 3: Update Planning Tools
- [ ] Backend: Refactor backend/tools/planning_tools.py
  - Remove PLAN_FILE constant and file operations
  - Add database session management
  - Update create_plan() to insert into Plan table
  - Update view_plan() to query Plan table by thread_id
  - Update update_plan_step() to update Plan table
  - Update add_plan_step() to modify Plan table
- [ ] Backend: Add thread_id parameter injection via RunnableConfig
- [ ] Backend: Handle tool context to extract thread_id
- [ ] Testing: Test planning CRUD operations with multiple thread_ids
- [ ] Testing: Verify thread isolation (thread A can't see thread B's plan)

### Task 4: Update Notes & Context Tools
- [ ] Backend: Refactor backend/tools/file_tools.py
  - Remove workspace/notes/ and workspace/context/ file operations
  - Add database session management
  - Update save_note() to insert into Note table with thread_id
  - Update read_note() to query Note table by thread_id and filename
  - Update list_notes() to query Note table by thread_id
  - Update context operations (if any) to use Context table
- [ ] Backend: Add thread_id parameter injection for file tools
- [ ] Testing: Test note operations with multiple thread_ids
- [ ] Testing: Verify notes are isolated per thread

### Task 5: Update API Endpoints
- [ ] Backend: Update GET /plan endpoint in main.py
  - Add required thread_id query parameter
  - Query Plan table by thread_id
  - Return 404 if no plan exists for thread
- [ ] Backend: Update DELETE /plan endpoint
  - Add required thread_id query parameter
  - Delete plan only for specified thread
- [ ] Backend: Add GET /threads/{thread_id}/plan RESTful endpoint (optional)
- [ ] Backend: Update GET /notes endpoints
  - Add thread_id query parameter or filter by current thread
  - Return only notes for specified thread
- [ ] Backend: Update GET /notes/{filename} endpoint
  - Add thread_id parameter to ensure proper isolation
- [ ] Testing: Test all endpoints with curl/Postman
- [ ] Testing: Verify proper 404 responses for missing resources

### Task 6: Frontend Integration
- [ ] Frontend: Update PlanPanel component (if exists)
  - Fetch plan using active thread_id
  - Display plan for current thread only
  - Handle empty plan state gracefully
- [ ] Frontend: Update notes display components
  - Filter notes by active thread_id
  - Show thread-specific notes only
- [ ] Frontend: Update any context display
  - Filter by active thread_id
- [ ] Testing: Verify UI shows correct data per thread
- [ ] Testing: Test thread switching updates plans/notes correctly

### Task 7: Cleanup & Documentation
- [ ] Backend: Archive workspace/current_plan.json (move to workspace/archive/)
- [ ] Backend: Archive workspace/notes/ directory
- [ ] Backend: Archive workspace/context/ directory
- [ ] Backend: Update CLAUDE.md with new architecture
  - Document database-based planning
  - Update workspace structure section
  - Add migration notes
- [ ] Backend: Update backend/README.md
  - Document new Plan/Note/Context models
  - Update API endpoint documentation
- [ ] Testing: Full end-to-end test with 3+ concurrent threads
- [ ] Testing: Verify no data leakage between threads
- [ ] Testing: Verify all existing functionality still works

## Acceptance Criteria
- [x] Feature tracking document created
- [ ] Plan model exists in database with thread_id foreign key
- [ ] Note model exists in database with thread_id foreign key
- [ ] Each thread has isolated plans (no cross-thread visibility)
- [ ] Each thread has isolated notes (no cross-thread visibility)
- [ ] Planning tools (create_plan, view_plan, etc.) work with database
- [ ] File tools (save_note, read_note, etc.) work with database
- [ ] API endpoints properly filter by thread_id
- [ ] Frontend displays correct per-thread data
- [ ] No data leakage between threads (verified by testing)
- [ ] All existing conversation functionality still works
- [ ] Documentation updated (CLAUDE.md, backend/README.md)
- [ ] Old workspace files archived

## Testing Strategy
1. **Unit Testing**: Test each modified function with multiple thread_ids
2. **Integration Testing**: Test API endpoints with concurrent requests
3. **End-to-End Testing**: Create 3 threads, each with different plans/notes, verify isolation
4. **Regression Testing**: Ensure existing chat/thread functionality unchanged

## Notes
- Started: 2025-11-09
- Implementation approach: Database-based for robustness
- Migration strategy: Archive existing files, start fresh per thread
