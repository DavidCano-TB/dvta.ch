---
inclusion: always
---

# Regla: Unit Tests Obligatorios

## Política

A cada nuevo desarrollo y/o implementación, crear nuevos unit tests que cubran la funcionalidad añadida o modificada.

## Cuándo aplicar

- Al añadir un nuevo endpoint API
- Al añadir una nueva función/clase de negocio
- Al añadir un nuevo módulo
- Al modificar comportamiento existente que cambie contratos públicos
- Al corregir bugs (test de regresión que reproduzca el bug)

## Cómo aplicar

1. Tests en `tests/test_<modulo>.py`
2. Seguir el patrón AAA (Arrange, Act, Assert)
3. Usar fixtures de `tests/conftest.py` cuando sea posible
4. Mockear dependencias externas (SMTP, HTTP, DB externa)
5. Cubrir caminos: éxito, errores de validación, edge cases, autenticación
6. Marcar con `pytest.mark.unit` por defecto
7. Para endpoints FastAPI usar `TestClient`

## Estructura recomendada

```python
class TestFeatureName:
    """Test suite for FeatureName"""

    def test_success_case(self):
        """Happy path"""
        # Arrange / Act / Assert

    def test_validation_error(self):
        """Invalid input rejected"""

    def test_edge_case(self):
        """Boundary conditions"""

    def test_with_mock(self):
        """External dependency mocked"""
```

## Comandos

- Ejecutar todos los tests: `python -m pytest tests/ -v`
- Ejecutar un archivo: `python -m pytest tests/test_X.py -v`
- Por marker: `python -m pytest -m unit -v`

## Excepciones

- Cambios sólo de documentación (`.md`, `.txt`) no requieren tests
- Cambios sólo de estilo/formato no requieren tests
- Scripts `.bat` de utilidad pueden documentarse en lugar de testearse
