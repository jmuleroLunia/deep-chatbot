# Refactorización: Clean Architecture + Screaming Architecture

**✅ COMPLETADO: 2025-11-09**

## Descripción

Refactorización completa del backend aplicando **Clean Architecture** (Uncle Bob) y **Screaming Architecture**. El objetivo es reorganizar el código actual (organizado por capas técnicas) a una arquitectura que **grite el dominio del negocio**, implementando estrictamente los principios **SOLID**.

### Estado Actual (Problemas Identificados)

**Organización actual:**
```
backend/
├── agents/          # Capa técnica
├── tools/           # Capa técnica
├── models.py        # Capa técnica
└── main.py          # God Object (598 líneas)
```

**Problemas principales:**
- ❌ **No es Screaming Architecture**: Estructura grita "FastAPI + LangGraph", no el dominio
- ❌ **Violaciones SOLID**:
  - SRP: main.py tiene 10+ responsabilidades
  - DIP: Dependencias directas a frameworks
  - OCP: Hard-coded Ollama, no extensible
- ❌ **Sin capa de dominio**: Lógica de negocio esparcida
- ❌ **No testeable**: Acoplamiento directo a DB y frameworks
- ❌ **God Object**: main.py con routing + lógica + persistencia

### Estado Objetivo

**Nueva organización (Screaming Architecture):**
```
backend/src/
├── domain/                    # ❤️ Corazón del negocio
│   ├── conversation/          # 🗣️ GRITA: Sistema de conversación
│   ├── planning/              # 📋 GRITA: Sistema de planificación
│   ├── memory/                # 🧠 GRITA: Sistema de memoria
│   └── agent_orchestration/   # 🤖 GRITA: Orquestación de agentes
├── application/               # Casos de uso
├── infrastructure/            # Detalles técnicos (DB, LLM, etc)
└── presentation/              # API REST
```

**Beneficios:**
- ✅ **Screaming Architecture**: Estructura muestra las capacidades del sistema
- ✅ **SOLID completo**: Cada principio implementado correctamente
- ✅ **Testable**: Capas desacopladas, inyección de dependencias
- ✅ **Mantenible**: Lógica organizada por dominio
- ✅ **Extensible**: Agregar features sin modificar código existente

---

## Tasks

### Task 1: Capa de Dominio (Domain Layer)

**Objetivo:** Crear entidades, value objects e interfaces del dominio (lógica de negocio pura, sin dependencias externas).

- [ ] **Backend: Dominio de Conversation**
  - Crear `domain/conversation/entities/thread.py` (Thread entity)
  - Crear `domain/conversation/entities/message.py` (Message entity)
  - Crear `domain/conversation/value_objects/thread_id.py` (ThreadId value object)
  - Crear `domain/conversation/value_objects/message_role.py` (MessageRole enum)
  - Crear `domain/conversation/repositories/thread_repository.py` (Protocol/ABC)

- [ ] **Backend: Dominio de Planning**
  - Crear `domain/planning/entities/plan.py` (Plan entity con validaciones)
  - Crear `domain/planning/entities/step.py` (Step entity)
  - Crear `domain/planning/value_objects/plan_status.py` (PlanStatus enum)
  - Crear `domain/planning/repositories/plan_repository.py` (Protocol/ABC)

- [ ] **Backend: Dominio de Memory**
  - Crear `domain/memory/entities/note.py` (Note entity)
  - Crear `domain/memory/repositories/note_repository.py` (Protocol/ABC)

- [ ] **Backend: Dominio de Agent Orchestration**
  - Crear `domain/agent_orchestration/services/agent_service.py` (Protocol para LLM)
  - Crear `domain/agent_orchestration/value_objects/tool_call.py`
  - Crear `domain/agent_orchestration/value_objects/agent_response.py`

- [ ] **Testing Task 1:**
  - Tests unitarios para entidades (reglas de negocio)
  - Tests unitarios para value objects (validaciones)
  - Verificar que domain/ no tiene imports de frameworks externos

**Principios SOLID verificados:**
- SRP: Cada entity/value object tiene una responsabilidad
- OCP: Domain abierto a extensión (nuevos value objects)
- DIP: Domain define abstracciones (Protocols), no depende de implementaciones

---

### Task 2: Capa de Aplicación (Application Layer)

**Objetivo:** Crear DTOs y casos de uso que orquestan la lógica de dominio.

- [ ] **Backend: Use Cases de Conversation**
  - Crear `application/conversation/use_cases/send_message.py` (SendMessageUseCase)
  - Crear `application/conversation/use_cases/get_thread_history.py`
  - Crear `application/conversation/use_cases/stream_chat.py`
  - Crear `application/conversation/dtos/chat_request.py` (DTO entrada)
  - Crear `application/conversation/dtos/chat_response.py` (DTO salida)

- [ ] **Backend: Use Cases de Planning**
  - Crear `application/planning/use_cases/create_plan.py`
  - Crear `application/planning/use_cases/update_step.py`
  - Crear `application/planning/use_cases/get_active_plan.py`
  - Crear `application/planning/use_cases/complete_plan.py`
  - Crear `application/planning/dtos/{plan_request,plan_response}.py`

- [ ] **Backend: Use Cases de Memory**
  - Crear `application/memory/use_cases/save_note.py`
  - Crear `application/memory/use_cases/retrieve_notes.py`
  - Crear `application/memory/dtos/{note_request,note_response}.py`

- [ ] **Testing Task 2:**
  - Tests unitarios para use cases (mockear repositorios)
  - Verificar flujos completos (happy path + error cases)
  - Test de integración domain ↔ application

**Principios SOLID verificados:**
- SRP: Un use case = una operación de negocio
- DIP: Use cases dependen de abstracciones (repositorios Protocol)
- ISP: Interfaces segregadas (solo métodos necesarios por use case)

---

### Task 3: Capa de Infraestructura (Infrastructure Layer)

**Objetivo:** Implementar detalles técnicos (persistencia, LLM providers, tools).

- [ ] **Backend: Persistencia SQLAlchemy**
  - Crear `infrastructure/persistence/sqlalchemy/models/thread_model.py`
  - Crear `infrastructure/persistence/sqlalchemy/models/message_model.py`
  - Crear `infrastructure/persistence/sqlalchemy/models/plan_model.py`
  - Crear `infrastructure/persistence/sqlalchemy/models/note_model.py`
  - Mappers entre ORM models ↔ Domain entities

- [ ] **Backend: Implementación de Repositorios**
  - Crear `infrastructure/persistence/repositories/thread_repository_impl.py`
  - Crear `infrastructure/persistence/repositories/plan_repository_impl.py`
  - Crear `infrastructure/persistence/repositories/note_repository_impl.py`
  - Configurar database.py unificado (async para FastAPI)

- [ ] **Backend: LLM Provider**
  - Crear `infrastructure/llm/providers/ollama_provider.py` (implementa AgentService)
  - Adaptar configuración de Ollama desde agents/config.py
  - Implementar streaming y checkpoint management

- [ ] **Backend: Tools Adaptation**
  - Refactorizar `tools/planning_tools.py` → `infrastructure/tools/planning_tools.py`
  - Refactorizar `tools/file_tools.py` → `infrastructure/tools/file_tools.py`
  - Inyectar repositorios en lugar de acceso directo a DB

- [ ] **Testing Task 3:**
  - Tests de integración para repositorios (con DB real/in-memory)
  - Tests de integración para LLM provider
  - Verificar implementaciones cumplen contratos del domain

**Principios SOLID verificados:**
- DIP: Infrastructure implementa interfaces del domain
- OCP: Nuevos providers (OpenAI, Anthropic) sin modificar domain
- LSP: Repositorios intercambiables sin romper contratos

---

### Task 4: Capa de Presentación (Presentation Layer)

**Objetivo:** Nueva API REST con mejores prácticas y dependency injection.

- [ ] **Backend: Rutas de Conversation**
  - Crear `presentation/api/v1/routes/conversation.py`
  - Endpoint: `POST /api/v1/conversations/send`
  - Endpoint: `POST /api/v1/conversations/stream`
  - Endpoint: `GET /api/v1/conversations/{thread_id}/messages`

- [ ] **Backend: Rutas de Planning**
  - Crear `presentation/api/v1/routes/planning.py`
  - Endpoint: `POST /api/v1/plans`
  - Endpoint: `PUT /api/v1/plans/{plan_id}/steps/{step_number}`
  - Endpoint: `GET /api/v1/plans/active`

- [ ] **Backend: Rutas de Memory**
  - Crear `presentation/api/v1/routes/memory.py`
  - Endpoint: `POST /api/v1/memory/notes`
  - Endpoint: `GET /api/v1/memory/notes`

- [ ] **Backend: Dependency Injection**
  - Crear `presentation/api/v1/dependencies.py`
  - Factory functions para use cases
  - FastAPI Dependencies para inyectar repositorios
  - Session management con async context managers

- [ ] **Backend: Main App**
  - Crear `presentation/api/main.py` (nueva app FastAPI)
  - Configurar CORS
  - Registrar routers
  - Configurar lifespan events (startup/shutdown)

- [ ] **Testing Task 4:**
  - Tests e2e para endpoints (TestClient FastAPI)
  - Verificar responses y status codes
  - Test de streaming endpoint

**Principios SOLID verificados:**
- DIP: Presentation depende de abstracciones (use cases)
- SRP: Cada route handler tiene una responsabilidad
- OCP: Agregar nuevos endpoints sin modificar existentes

---

### Task 5: Migración y Testing Final

**Objetivo:** Migrar datos existentes y crear suite de tests completa.

- [ ] **Backend: Script de Migración**
  - Crear `scripts/migrate_to_new_structure.py`
  - Migrar datos de workspace/checkpoints.db a nueva estructura
  - Migrar notes/ y context/ existentes
  - Backup automático antes de migración

- [ ] **Backend: Testing Suite**
  - Suite de tests unitarios (domain + application)
  - Suite de tests de integración (infrastructure)
  - Suite de tests e2e (presentation)
  - Coverage report (objetivo: >80%)

- [ ] **Backend: Limpieza de Código Antiguo**
  - Eliminar `main.py` (598 líneas)
  - Eliminar `models.py` (movido a infrastructure)
  - Eliminar `database.py` (refactorizado)
  - Eliminar `agents/` (refactorizado en domain + infrastructure)
  - Eliminar `tools/` (movido a infrastructure)
  - Actualizar `pyproject.toml` con nuevas dependencies (si aplica)

- [ ] **Frontend: Actualización (si existe)**
  - Actualizar URLs de endpoints a `/api/v1/*`
  - Verificar que frontend sigue funcionando

- [ ] **Testing Task 5:**
  - Ejecutar suite completa de tests
  - Verificar que API funciona con Postman/curl
  - Test de regresión (features antiguas siguen funcionando)
  - Performance test (comparar con versión antigua)

**Verificación final:**
- ✅ Todos los tests pasan
- ✅ Migración de datos exitosa
- ✅ API responde correctamente
- ✅ No hay código legacy en codebase

---

## Acceptance Criteria

### Criterios Arquitecturales

1. **Screaming Architecture:**
   - [ ] La estructura de carpetas refleja el dominio del negocio
   - [ ] Un nuevo desarrollador puede entender qué hace el sistema solo viendo carpetas
   - [ ] No se menciona "FastAPI" o "LangGraph" en nombres de carpetas principales

2. **Principios SOLID:**
   - [ ] **SRP**: Cada clase/módulo tiene una única razón para cambiar
   - [ ] **OCP**: Sistema abierto a extensión (nuevos providers/tools) sin modificar código existente
   - [ ] **LSP**: Todas las implementaciones de repositorios son intercambiables
   - [ ] **ISP**: No hay interfaces "gordas" con métodos no usados
   - [ ] **DIP**: Domain no depende de frameworks, frameworks dependen de domain

3. **Capas Limpias:**
   - [ ] Domain layer: Sin imports externos (solo stdlib + typing)
   - [ ] Application layer: Solo depende de domain
   - [ ] Infrastructure layer: Implementa interfaces del domain
   - [ ] Presentation layer: Solo depende de application y domain

4. **Testabilidad:**
   - [ ] Suite de tests unitarios (domain + application)
   - [ ] Suite de tests de integración (infrastructure)
   - [ ] Suite de tests e2e (presentation)
   - [ ] Coverage > 80%
   - [ ] Tests ejecutan en < 10 segundos (unitarios)

5. **Funcionalidad:**
   - [ ] Todas las features antiguas funcionan (chat, streaming, planning, notes)
   - [ ] Migración de datos exitosa sin pérdida
   - [ ] Performance igual o mejor que versión anterior
   - [ ] API responde correctamente a todos los endpoints

6. **Documentación:**
   - [ ] Cada capa tiene README explicando su propósito
   - [ ] Domain entities tienen docstrings completos
   - [ ] API tiene documentación OpenAPI actualizada
   - [ ] Diagrama de arquitectura (capas + flujo de dependencias)

---

## Referencias

- **Análisis Arquitectural**: Ver reporte completo de análisis del código actual
- **Clean Architecture Book**: Robert C. Martin (Uncle Bob)
- **Screaming Architecture**: https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html
- **SOLID Principles**: https://en.wikipedia.org/wiki/SOLID

---

## Notas de Implementación

### Enfoque: Big Bang (Reescritura Completa)
- Nueva estructura en paralelo al código actual
- Migración de datos al final
- Código antiguo eliminado después de validación completa

### Prioridades
1. **SOLID**: Implementación estricta de todos los principios
2. **Screaming Architecture**: Estructura que grita el dominio

### Riesgos Identificados
- **Riesgo**: Pérdida de datos durante migración
  - **Mitigación**: Backup automático antes de migrar
- **Riesgo**: Incompatibilidad con frontend existente
  - **Mitigación**: Versionar API (`/api/v1/`), mantener endpoints similares
- **Riesgo**: Bugs introducidos por reescritura
  - **Mitigación**: Suite de tests completa + test de regresión

### Estimación de Esfuerzo
- **Archivos nuevos**: ~40 archivos
- **Líneas de código**: ~3000-4000 LOC
- **Tiempo estimado**: 3-5 días (desarrollo completo + testing)
