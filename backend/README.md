# Deep Agent Chatbot

Un chatbot avanzado construido con LangGraph y FastAPI que implementa la arquitectura "Deep Agent" para razonamiento complejo, planificación multi-paso y ejecución de tareas con memoria persistente.

## Características Principales

### Arquitectura Deep Agent

Siguiendo las mejores prácticas de LangChain, este sistema implementa los 4 componentes esenciales de un deep agent:

1. **System Prompt Detallado**: Instrucciones comprehensivas con ejemplos específicos
2. **Herramienta de Planificación**: Sistema de TODO list para gestionar tareas complejas
3. **Sub-Agentes**: Agentes especializados para diferentes tipos de tareas
4. **Acceso al Sistema de Archivos**: Persistencia de contexto y notas

### Capacidades

- Planificación automática de tareas complejas
- Memoria persistente entre conversaciones
- Almacenamiento de notas y contexto
- API RESTful con soporte para streaming
- Integración con Ollama para inferencia local

## Requisitos Previos

- Python 3.12+
- Poetry (gestor de dependencias)
- Ollama (para el LLM local)

## Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd deep-chatbot
```

2. **Instalar dependencias**
```bash
poetry install
```

3. **Instalar y configurar Ollama**
```bash
# Instalar Ollama desde https://ollama.ai
# Descargar el modelo
ollama pull llama3.2
```

4. **Iniciar Ollama**
```bash
ollama serve
```

## Uso

### Iniciar el Servidor

```bash
poetry run uvicorn main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`

### Documentación de la API

Accede a la documentación interactiva en:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Ejemplos de Uso

#### 1. Chat Simple

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What time is it?",
    "thread_id": "user123"
  }'
```

#### 2. Tarea Compleja con Planificación

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze the sentiment of customer feedback and create a detailed report",
    "thread_id": "analysis_session"
  }'
```

El agente automáticamente:
1. Creará un plan con pasos específicos
2. Ejecutará cada paso
3. Guardará los resultados en notas
4. Marcará los pasos como completados

#### 3. Ver el Plan Actual

```bash
curl -X GET "http://127.0.0.1:8000/plan"
```

#### 4. Listar Notas Guardadas

```bash
curl -X GET "http://127.0.0.1:8000/notes"
```

#### 5. Leer una Nota Específica

```bash
curl -X GET "http://127.0.0.1:8000/notes/20241109_140523_analysis_report.txt"
```

#### 6. Streaming de Respuestas

```bash
curl -X POST "http://127.0.0.1:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate 15% of 1000 and explain",
    "thread_id": "calc_session"
  }'
```

## Arquitectura del Proyecto

```
deep-chatbot/
├── agents/
│   ├── __init__.py
│   ├── config.py           # Configuración del agente
│   ├── deep_agent.py       # Agente principal
│   └── sub_agents.py       # Sub-agentes especializados
├── tools/
│   ├── __init__.py
│   ├── custom_tools.py     # Herramientas generales
│   ├── file_tools.py       # Operaciones de archivos
│   ├── planning_tools.py   # Planificación de tareas
│   └── handoff_tools.py    # Comunicación entre agentes
├── workspace/              # Workspace del agente (auto-generado)
│   ├── notes/             # Notas guardadas
│   ├── context/           # Contexto persistente
│   └── current_plan.json  # Plan activo
├── main.py                # Aplicación FastAPI
├── pyproject.toml         # Configuración de Poetry
└── README.md
```

## Herramientas Disponibles

### Planificación
- `create_plan`: Crear un plan multi-paso
- `view_plan`: Ver el plan actual
- `update_plan_step`: Marcar pasos como completados
- `add_plan_step`: Añadir nuevos pasos

### Sistema de Archivos
- `save_note`: Guardar notas
- `read_note`: Leer notas
- `list_notes`: Listar todas las notas
- `save_context`: Guardar contexto estructurado
- `load_context`: Cargar contexto
- `list_context_keys`: Listar claves de contexto

### Herramientas Especializadas
- `get_current_time`: Obtener fecha/hora
- `calculate`: Calcular expresiones matemáticas
- `search_knowledge_base`: Buscar en la base de conocimiento
- `analyze_sentiment`: Analizar sentimiento de texto

## Configuración

### Modelo de Ollama

Edita `agents/config.py` para cambiar el modelo:

```python
OLLAMA_MODEL = "llama3.2"  # Cambia a otro modelo
```

Modelos recomendados:
- `llama3.2` - Rápido y eficiente
- `mixtral` - Mejor razonamiento
- `codellama` - Especializado en código

### Base URL de Ollama

Si Ollama está en otro servidor:

```python
OLLAMA_BASE_URL = "http://otro-servidor:11434"
```

## Ejemplos de Casos de Uso

### 1. Investigación y Análisis

```python
{
  "message": "Research Python web frameworks, analyze their pros and cons, and save a detailed comparison report",
  "thread_id": "research_001"
}
```

El agente:
1. Creará un plan de investigación
2. Buscará información sobre frameworks
3. Analizará ventajas/desventajas
4. Guardará un informe detallado
5. Marcará todos los pasos como completados

### 2. Cálculos Complejos

```python
{
  "message": "Calculate the compound interest for $10,000 at 5% over 10 years and explain the formula",
  "thread_id": "finance_001"
}
```

### 3. Análisis de Sentimiento

```python
{
  "message": "Analyze the sentiment of these reviews and save a summary: 'Great product!', 'Terrible service', 'Amazing quality'",
  "thread_id": "sentiment_001"
}
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/health` | Health check |
| POST | `/chat` | Enviar mensaje al agente |
| POST | `/chat/stream` | Stream de respuestas |
| GET | `/plan` | Ver plan actual |
| GET | `/notes` | Listar notas |
| GET | `/notes/{filename}` | Leer nota específica |
| DELETE | `/plan` | Limpiar plan actual |

## Desarrollo

### Ejecutar Tests

```bash
# TODO: Implementar tests
poetry run pytest
```

### Formato de Código

```bash
poetry run black .
poetry run isort .
```

## Solución de Problemas

### Ollama no está disponible

```bash
# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags

# Si no responde, iniciar Ollama
ollama serve
```

### Error de modelo no encontrado

```bash
# Descargar el modelo
ollama pull llama3.2
```

### Problemas de memoria

Si el agente usa mucha memoria, considera:
- Usar un modelo más pequeño
- Reducir el tamaño del contexto
- Limpiar el workspace periódicamente

## Recursos

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Deep Agents Blog Post](https://blog.langchain.com/deep-agents/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://ollama.ai/docs)

## Licencia

MIT

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios propuestos.
