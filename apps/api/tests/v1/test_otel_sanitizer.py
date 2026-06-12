import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from app.core.telemetry import PIISanitizingSpanProcessor


def test_pii_sanitization_in_span_attributes():
    # 1. Setup in-memory exporter and span processor
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    
    provider.add_span_processor(PIISanitizingSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    
    tracer = provider.get_tracer(__name__)
    
    # 2. Executar e registrar span com múltiplos atributos contendo PII
    with tracer.start_as_current_span("test-span") as span:
        # Atributos com nomes sensíveis
        span.set_attribute("password", "minha_senha_secreta_123")
        span.set_attribute("user.password", "outra_senha")
        span.set_attribute("token", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        span.set_attribute("jwt_token", "jwt123")
        span.set_attribute("auth_key", "secret-key")
        span.set_attribute("authorization", "Bearer token_valido")
        span.set_attribute("user.email", "admin@servicoja.com.br")
        span.set_attribute("client.name", "João da Silva")
        
        # PII nos valores de string
        span.set_attribute("some_text_cpf", "Meu CPF é 123.456.789-00 e é secreto.")
        span.set_attribute("some_text_cnpj", "Empresa CNPJ: 12.345.678/0001-99.")
        span.set_attribute("some_text_email", "Contato em suporte@servicoja.com")
        span.set_attribute("raw_cpf", "12345678901")
        span.set_attribute("raw_cnpj", "12345678000199")
        
        # Atributos não sensíveis (happy path)
        span.set_attribute("http.status_code", 200)
        span.set_attribute("http.method", "GET")
        span.set_attribute("service.version", "1.0.0")
        
        # Arrays/Sequences com PII
        span.set_attribute("emails_list", ["teste@gmail.com", "outro@yahoo.com"])
        span.set_attribute("numbers_list", [123, 456])

    # 3. Validar se os spans exportados foram sanitizados
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    exported_span = spans[0]
    attrs = exported_span.attributes
    
    # Validar redação de chaves sensíveis
    assert attrs["password"] == "[REDACTED]"
    assert attrs["user.password"] == "[REDACTED]"
    assert attrs["token"] == "[REDACTED]"
    assert attrs["jwt_token"] == "[REDACTED]"
    assert attrs["auth_key"] == "[REDACTED]"
    assert attrs["authorization"] == "Bearer [REDACTED]"
    assert attrs["user.email"] == "[REDACTED_EMAIL]"
    assert attrs["client.name"] == "[REDACTED_NAME]"
    
    # Validar substituições de padrões no texto das strings
    assert "123.456.789-00" not in attrs["some_text_cpf"]
    assert "***.***.***-00" in attrs["some_text_cpf"]
    
    assert "12.345.678/0001-99" not in attrs["some_text_cnpj"]
    assert "**.***.****/****-99" in attrs["some_text_cnpj"]
    
    assert "suporte@servicoja.com" not in attrs["some_text_email"]
    assert "[REDACTED_EMAIL]" in attrs["some_text_email"]
    
    assert attrs["raw_cpf"] == "***.***.***-01"
    assert attrs["raw_cnpj"] == "**.***.****/****-99"
    
    # Validar preservação de atributos normais
    assert attrs["http.status_code"] == 200
    assert attrs["http.method"] == "GET"
    assert attrs["service.version"] == "1.0.0"
    
    # Validar listas
    assert attrs["emails_list"] == ("[REDACTED_EMAIL]", "[REDACTED_EMAIL]")
    assert attrs["numbers_list"] == (123, 456)


def test_pii_sanitization_in_span_name():
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(PIISanitizingSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)
    
    # Span name contendo e-mail e CPF
    with tracer.start_as_current_span("login-for-user-test@example.com-cpf-12345678901"):
        pass
        
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    exported_span = spans[0]
    
    # Deve mascarar o nome do span
    assert "test@example.com" not in exported_span.name
    assert "12345678901" not in exported_span.name
    assert "[REDACTED_EMAIL]" in exported_span.name
    assert "*********01" in exported_span.name
