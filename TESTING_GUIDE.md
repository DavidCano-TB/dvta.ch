# DVDcoin Platform - Testing Guide

## 📋 Resumen

Este proyecto implementa un sistema de testing unitario completo con **100% de code coverage obligatorio** antes de cada despliegue.

## 🎯 Objetivos

- ✅ **100% Code Coverage**: Todo el código debe estar cubierto por tests
- ✅ **Tests Automáticos**: Los tests se ejecutan automáticamente en cada push
- ✅ **Bloqueo de Deploy**: Si los tests fallan o coverage < 100%, el deploy se bloquea
- ✅ **Calidad Garantizada**: Solo código testeado llega a producción

## 📁 Estructura de Tests

```
tests/
├── __init__.py                 # Package marker
├── conftest.py                 # Fixtures compartidas
├── test_db_helper.py          # Tests para DatabaseHelper
├── test_jwt_helper.py         # Tests para JWTHelper
├── test_email_service.py      # Tests para EmailService
└── test_exams_app.py          # Tests para Exams Application
```

## 🚀 Ejecutar Tests Localmente

### Opción 1: Script Batch (Recomendado)

```batch
RUN_TESTS.bat
```

Este script:
1. Verifica Python
2. Instala dependencias de testing
3. Ejecuta todos los tests con coverage
4. Genera reporte HTML
5. Requiere 100% coverage para pasar

### Opción 2: Comando Manual

```bash
# Instalar dependencias
pip install -r requirements-dev.txt

# Ejecutar tests con coverage
pytest tests/ -v --cov=modules --cov=main --cov-report=html --cov-report=term-missing --cov-fail-under=100
```

### Opción 3: Tests Específicos

```bash
# Test de un módulo específico
pytest tests/test_db_helper.py -v

# Test de una clase específica
pytest tests/test_jwt_helper.py::TestJWTHelper -v

# Test de una función específica
pytest tests/test_email_service.py::TestEmailService::test_send_email_disabled -v
```

## 📊 Ver Reportes de Coverage

### Reporte en Terminal

```bash
pytest tests/ --cov=modules --cov-report=term-missing
```

### Reporte HTML (Detallado)

```bash
pytest tests/ --cov=modules --cov-report=html
start htmlcov/index.html
```

El reporte HTML muestra:
- Porcentaje de coverage por archivo
- Líneas cubiertas vs no cubiertas
- Código con highlighting de coverage
- Estadísticas detalladas

## 🔧 Configuración

### pytest.ini

Configuración principal de pytest:
- Test discovery patterns
- Coverage settings
- Output options
- Markers para categorizar tests

### .coveragerc

Configuración de coverage:
- Archivos a incluir/excluir
- Threshold de 100%
- Formato de reportes
- Líneas a excluir del coverage

### requirements-dev.txt

Dependencias de testing:
- `pytest` - Framework de testing
- `pytest-asyncio` - Tests asíncronos
- `pytest-cov` - Coverage integration
- `pytest-mock` - Mocking utilities
- `httpx` - HTTP testing
- `faker` - Datos de prueba
- `coverage` - Code coverage

## 🎨 Escribir Tests

### Estructura Básica

```python
import pytest

class TestMyFeature:
    """Test suite for MyFeature"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        result = my_function()
        assert result == expected_value
    
    def test_edge_case(self):
        """Test edge case"""
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

### Usar Fixtures

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests"""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """Test using fixture"""
    assert sample_data["key"] == "value"
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked dependency"""
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = my_function()
        assert result == "mocked"
```

### Tests Asíncronos

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await my_async_function()
    assert result is not None
```

## 🔄 Integración con GitHub Actions

### Workflow Automático

El archivo `.github/workflows/deploy.yml` ejecuta automáticamente:

1. **Install Dependencies**: Instala todas las dependencias
2. **Run Tests**: Ejecuta tests con coverage
3. **Check Coverage**: Verifica 100% coverage
4. **Block Deploy**: Si falla, bloquea el deploy
5. **Upload Reports**: Sube reportes como artifacts

### Ver Resultados en GitHub

1. Ve a tu repositorio en GitHub
2. Click en "Actions"
3. Selecciona el workflow run
4. Ve los resultados de tests
5. Descarga coverage reports si es necesario

## 📈 Métricas de Coverage

### Coverage Actual

```
Module                          Coverage
─────────────────────────────────────────
modules/shared/db_helper.py     100%
modules/shared/jwt_helper.py    100%
modules/shared/email_service.py 100%
modules/exams/app_exams.py      100%
─────────────────────────────────────────
TOTAL                           100%
```

### Mantener 100% Coverage

Para mantener 100% coverage:

1. **Escribe tests primero** (TDD)
2. **Cubre todos los casos**:
   - Happy path
   - Edge cases
   - Error cases
   - Boundary conditions
3. **Usa coverage report** para encontrar líneas no cubiertas
4. **No hagas commit** sin 100% coverage

## 🐛 Debugging Tests

### Ver Output Detallado

```bash
pytest tests/ -v -s
```

### Ver Solo Tests Fallidos

```bash
pytest tests/ --lf
```

### Modo Debug

```bash
pytest tests/ --pdb
```

### Ver Warnings

```bash
pytest tests/ -v -W all
```

## 📝 Markers de Tests

Los tests están categorizados con markers:

```python
@pytest.mark.unit
def test_unit():
    """Unit test"""
    pass

@pytest.mark.integration
def test_integration():
    """Integration test"""
    pass

@pytest.mark.slow
def test_slow():
    """Slow test"""
    pass
```

Ejecutar tests por marker:

```bash
# Solo unit tests
pytest tests/ -m unit

# Excluir slow tests
pytest tests/ -m "not slow"
```

## 🔒 Pre-commit Hooks (Opcional)

Para ejecutar tests antes de cada commit:

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hook
pre-commit install
```

Crear `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: [tests/, --cov=modules, --cov-fail-under=100]
```

## 📚 Recursos

### Documentación

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

### Comandos Útiles

```bash
# Ver ayuda de pytest
pytest --help

# Listar todos los tests
pytest --collect-only

# Ver fixtures disponibles
pytest --fixtures

# Generar reporte JUnit (para CI)
pytest tests/ --junitxml=junit.xml

# Ejecutar en paralelo (más rápido)
pip install pytest-xdist
pytest tests/ -n auto
```

## ✅ Checklist de Testing

Antes de hacer commit:

- [ ] Todos los tests pasan localmente
- [ ] Coverage es 100%
- [ ] No hay warnings
- [ ] Tests son claros y bien documentados
- [ ] Se cubren casos edge
- [ ] Se cubren casos de error
- [ ] Mocks están bien configurados
- [ ] Fixtures son reutilizables

## 🎯 Mejores Prácticas

1. **Un test, una cosa**: Cada test debe verificar una sola cosa
2. **Nombres descriptivos**: `test_login_with_invalid_credentials`
3. **AAA Pattern**: Arrange, Act, Assert
4. **No dependencias**: Tests deben ser independientes
5. **Fast tests**: Tests deben ser rápidos
6. **Deterministic**: Mismo input = mismo output
7. **Clean fixtures**: Limpiar después de cada test
8. **Mock external**: Mockear APIs externas, DB, etc.

## 🚨 Troubleshooting

### Tests Fallan Localmente

1. Verifica que tienes todas las dependencias: `pip install -r requirements-dev.txt`
2. Verifica Python version: `python --version` (debe ser 3.11+)
3. Limpia cache: `pytest --cache-clear`
4. Reinstala dependencias: `pip install --force-reinstall -r requirements-dev.txt`

### Coverage < 100%

1. Ejecuta con reporte detallado: `pytest --cov-report=term-missing`
2. Identifica líneas no cubiertas
3. Escribe tests para esas líneas
4. Verifica que los tests realmente ejecutan esas líneas

### Tests Lentos

1. Usa markers para separar tests lentos
2. Ejecuta en paralelo: `pytest -n auto`
3. Optimiza fixtures
4. Mockea operaciones lentas (DB, API calls)

## 📞 Soporte

Si tienes problemas con los tests:

1. Revisa esta guía
2. Revisa los logs de GitHub Actions
3. Ejecuta tests localmente con `-v -s` para más detalles
4. Verifica que todas las dependencias están instaladas

---

**Recuerda**: ¡No hay deploy sin 100% coverage! 🎯
