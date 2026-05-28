# Testing Quick Reference Card

## 🚀 Comandos Rápidos

### Ejecutar Todos los Tests

```bash
# Con script (Recomendado)
RUN_TESTS.bat

# Manual
pytest tests/ -v --cov=modules --cov-report=html --cov-fail-under=100
```

### Tests Específicos

```bash
# Un archivo
pytest tests/test_db_helper.py -v

# Una clase
pytest tests/test_jwt_helper.py::TestJWTHelper -v

# Una función
pytest tests/test_email_service.py::TestEmailService::test_send_email_disabled -v

# Por marker
pytest tests/ -m unit
pytest tests/ -m "not slow"
```

### Coverage

```bash
# Reporte en terminal
pytest tests/ --cov=modules --cov-report=term-missing

# Reporte HTML
pytest tests/ --cov=modules --cov-report=html
start htmlcov\index.html

# Solo coverage sin tests
coverage report
coverage html
```

### Debugging

```bash
# Output detallado
pytest tests/ -v -s

# Solo tests fallidos
pytest tests/ --lf

# Modo debug (breakpoint)
pytest tests/ --pdb

# Ver warnings
pytest tests/ -v -W all
```

### Información

```bash
# Listar todos los tests
pytest --collect-only

# Ver fixtures disponibles
pytest --fixtures

# Ayuda
pytest --help
```

## 📝 Escribir Tests

### Estructura Básica

```python
import pytest

class TestMyFeature:
    def test_something(self):
        # Arrange
        input_value = "test"
        
        # Act
        result = my_function(input_value)
        
        # Assert
        assert result == expected_value
```

### Fixtures

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = my_function()
        assert result == "mocked"
```

### Excepciones

```python
def test_raises_error():
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

### Tests Asíncronos

```python
@pytest.mark.asyncio
async def test_async():
    result = await my_async_function()
    assert result is not None
```

## 🎯 Markers

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skip(reason="Not implemented")
@pytest.mark.skipif(condition, reason="...")
@pytest.mark.parametrize("input,expected", [
    ("a", 1),
    ("b", 2),
])
```

## 📊 Coverage

### Ver Coverage

```bash
# Terminal
pytest --cov=modules --cov-report=term

# HTML (detallado)
pytest --cov=modules --cov-report=html
start htmlcov\index.html

# XML (para CI)
pytest --cov=modules --cov-report=xml
```

### Excluir del Coverage

```python
# En el código
if __name__ == "__main__":  # pragma: no cover
    main()
```

## 🔧 Configuración

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --cov=modules --cov-fail-under=100
```

### .coveragerc

```ini
[run]
source = modules
omit = */tests/*

[report]
fail_under = 100
```

## 🐛 Troubleshooting

### Tests Fallan

```bash
# Limpiar cache
pytest --cache-clear

# Reinstalar dependencias
pip install --force-reinstall -r requirements-dev.txt

# Ver output completo
pytest tests/ -v -s --tb=long
```

### Coverage Bajo

```bash
# Ver líneas no cubiertas
pytest --cov=modules --cov-report=term-missing

# Ver reporte HTML detallado
pytest --cov=modules --cov-report=html
start htmlcov\index.html
```

### Import Errors

```bash
# Verificar PYTHONPATH
echo %PYTHONPATH%

# Instalar en modo editable
pip install -e .
```

## ✅ Checklist Pre-Commit

- [ ] `pytest tests/ -v` → Todos pasan
- [ ] Coverage = 100%
- [ ] No warnings críticos
- [ ] Tests documentados
- [ ] Casos edge cubiertos
- [ ] Mocks configurados
- [ ] Fixtures limpias

## 📚 Recursos Rápidos

- **Documentación Completa**: `TESTING_GUIDE.md`
- **Template de Tests**: `tests/TEST_TEMPLATE.py`
- **Ejecutar Tests**: `RUN_TESTS.bat`
- **Ver Coverage**: `start htmlcov\index.html`

## 🎨 Patrones Comunes

### Test de API Endpoint

```python
def test_endpoint(client):
    response = client.get("/api/endpoint")
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

### Test de Database

```python
def test_db_operation(temp_db):
    db = Database(temp_db)
    record_id = db.insert({"name": "test"})
    record = db.get(record_id)
    assert record["name"] == "test"
```

### Test de Autenticación

```python
def test_auth_required(client):
    response = client.get("/api/protected")
    assert response.status_code == 401
```

### Test con Mock

```python
@patch('module.external_api')
def test_with_mock(mock_api):
    mock_api.return_value = {"data": "mocked"}
    result = my_function()
    assert result["data"] == "mocked"
```

## 🚨 Errores Comunes

### ImportError

```bash
# Solución: Agregar al path
sys.path.insert(0, str(BASE_DIR / "modules"))
```

### Fixture Not Found

```bash
# Solución: Definir en conftest.py o en el mismo archivo
@pytest.fixture
def my_fixture():
    return "value"
```

### Coverage No Alcanza 100%

```bash
# Solución: Ver líneas no cubiertas
pytest --cov-report=term-missing
# Escribir tests para esas líneas
```

### Tests Lentos

```bash
# Solución: Ejecutar en paralelo
pip install pytest-xdist
pytest tests/ -n auto
```

---

**Tip**: Guarda este archivo como referencia rápida mientras desarrollas tests.
