# Gestión de Threads

**Completado:** 9 de Noviembre de 2025

## Description
Sistema completo de gestión de conversaciones (threads) con persistencia en base de datos SQLite, títulos auto-generados, y una interfaz de usuario con sidebar para crear, listar, cambiar y eliminar conversaciones.

## Tasks

### Task 1: Backend - Database Setup & Persistence
- [ ] Backend: Añadir dependencias (SQLAlchemy, Alembic, aiosqlite) a `pyproject.toml`
- [ ] Backend: Crear `backend/database.py` con configuración de SQLite y gestión de sesiones
- [ ] Backend: Crear `backend/models.py` con modelos Thread y Message (SQLAlchemy)
- [ ] Backend: Inicializar Alembic y crear migración inicial
- [ ] Backend: Reemplazar `MemorySaver` con `SqliteSaver` en `backend/agents/deep_agent.py`
- [ ] Testing: Verificar que la base de datos se crea correctamente y que el estado de conversación persiste tras reiniciar el servidor

### Task 2: Backend - Thread Management API
- [ ] Backend: Crear endpoint `POST /threads` - Crear nuevo thread
- [ ] Backend: Crear endpoint `GET /threads` - Listar todos los threads (ordenados por fecha de actualización)
- [ ] Backend: Crear endpoint `GET /threads/{thread_id}` - Obtener thread específico con sus mensajes
- [ ] Backend: Crear endpoint `PUT /threads/{thread_id}` - Actualizar título del thread
- [ ] Backend: Crear endpoint `DELETE /threads/{thread_id}` - Eliminar thread y sus mensajes
- [ ] Backend: Actualizar `POST /chat` y `POST /chat/stream` para guardar mensajes en base de datos
- [ ] Backend: Crear función de auto-generación de títulos usando LLM (3-5 palabras desde el primer mensaje del usuario)
- [ ] Testing: Probar todos los endpoints y verificar que los mensajes se persisten correctamente

### Task 3: Frontend - Thread Sidebar Component
- [ ] Frontend: Crear componente `ThreadSidebar.jsx` con lista de threads
- [ ] Frontend: Añadir botón "New Thread" que llama a `POST /threads`
- [ ] Frontend: Mostrar título del thread, timestamp y preview del último mensaje
- [ ] Frontend: Implementar click en thread para cambiar conversación activa
- [ ] Frontend: Añadir botón de eliminar thread con confirmación
- [ ] Frontend: Crear funciones API en `utils/api.js` para llamadas a endpoints de threads
- [ ] Testing: Verificar que el sidebar muestra threads correctamente y se actualiza

### Task 4: Frontend - Thread Switching & Integration
- [ ] Frontend: Actualizar `ChatInterface.jsx` para cargar mensajes del thread seleccionado
- [ ] Frontend: Guardar thread_id actual en localStorage
- [ ] Frontend: Cargar thread_id desde localStorage al iniciar la app
- [ ] Frontend: Limpiar mensajes al cambiar de thread
- [ ] Frontend: Crear layout responsive con sidebar (colapsable en móvil)
- [ ] Frontend: Actualizar `App.jsx` para incluir sidebar y chat interface
- [ ] Frontend: Añadir estilos CSS/Tailwind para sidebar y thread items
- [ ] Testing: Verificar que cambiar de thread carga el contexto correcto y el diseño es responsive

### Task 5: Polish & Refinements
- [ ] Backend: (Opcional) Modificar herramientas de archivos para namespace por thread_id
- [ ] Backend: (Opcional) Actualizar almacenamiento de planes a `workspace/threads/{thread_id}/current_plan.json`
- [ ] Backend: (Opcional) Actualizar notas a `workspace/threads/{thread_id}/notes/`
- [ ] Frontend: Añadir estados de carga para operaciones de threads
- [ ] Frontend: Añadir manejo de errores y feedback al usuario (toasts/notificaciones)
- [ ] Frontend: Añadir funcionalidad de renombrar thread (doble-click para editar)
- [ ] Frontend: Añadir atajos de teclado (Ctrl+N para nuevo thread, etc.)
- [ ] Backend: Actualizar README.md con instrucciones de setup de base de datos
- [ ] Backend: Documentar nuevos endpoints API
- [ ] Testing: Prueba completa del flujo end-to-end desde cero

## Technical Details

### Backend Architecture
- **Database**: SQLite con SQLAlchemy ORM
- **Persistence**: LangGraph SqliteSaver para estado de conversaciones
- **Models**:
  - Thread (id, title, created_at, updated_at, metadata)
  - Message (id, thread_id, role, content, timestamp, tool_calls)

### Frontend Architecture
- **Components**: ThreadSidebar, ThreadItem, enhanced ChatInterface
- **State**: Thread list from API, current thread ID in React state + localStorage
- **Storage**: localStorage para thread_id actual

### File Structure After Implementation
```
backend/
├── workspace/
│   ├── checkpoints.db          # LangGraph state
│   ├── threads.db              # Thread/Message data
│   └── threads/                # Per-thread files (optional)
├── database.py                 # NEW
├── models.py                   # NEW
├── main.py                     # Updated with new endpoints
└── alembic/                    # NEW

frontend/src/
├── components/
│   ├── ChatInterface.jsx       # Updated
│   ├── ThreadSidebar.jsx       # NEW
│   └── ThreadItem.jsx          # NEW
└── utils/
    └── api.js                  # NEW
```

## Acceptance Criteria
- Las conversaciones persisten tras reiniciar el servidor
- Los usuarios pueden crear, ver, cambiar y eliminar threads
- Los títulos de threads se generan automáticamente desde el primer mensaje
- El sidebar muestra todos los threads con cambio rápido entre ellos
- Los mensajes se cargan correctamente al cambiar de thread
- La API backend funciona correctamente con manejo de errores apropiado
- La UI frontend es responsive y user-friendly
- La documentación está actualizada con instrucciones de setup

## Notes
- Sistema single-user (sin autenticación por ahora)
- SQLite es adecuado para desarrollo y uso single-user
- Los títulos auto-generados pueden ser editados manualmente posteriormente
- El workspace puede ser opcional thread-específico (planes y notas)