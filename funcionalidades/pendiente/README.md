# Funcionalidades Pendientes

Esta carpeta contiene las especificaciones de funcionalidades planificadas que aún no se han iniciado.

## Cómo usar

1. Crea un archivo markdown para cada funcionalidad nueva
2. Usa un nombre descriptivo en kebab-case: `nombre-funcionalidad.md`
3. Sigue la plantilla definida en CLAUDE.md
4. Cuando inicies el desarrollo, mueve el archivo a `../activas/`

## Plantilla

```markdown
# [Nombre de la Funcionalidad]

## Description
Breve descripción de la funcionalidad

## Tasks
Dividir en bloques testables (normalmente front + back juntos):

### Task 1: [Nombre]
- [ ] Backend: endpoint/lógica de API
- [ ] Frontend: componente UI/integración
- [ ] Testing: Cómo verificar que funciona

### Task 2: [Nombre]
- [ ] Backend: ...
- [ ] Frontend: ...
- [ ] Testing: ...

## Acceptance Criteria
- La funcionalidad funciona end-to-end
- Todos los tests pasan
- El código está documentado
```
