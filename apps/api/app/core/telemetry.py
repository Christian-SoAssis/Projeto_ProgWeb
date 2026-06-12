import os
import re
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


CPF_PATTERN = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CNPJ_PATTERN = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")
EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b")
RAW_CPF_PATTERN = re.compile(r"\b\d{11}\b")
RAW_CNPJ_PATTERN = re.compile(r"\b\d{14}\b")


def sanitize_string_value(val: str, key_name: str = "") -> str:
    if not val:
        return val

    key_lower = key_name.lower()
    
    # 1. Redação completa para chaves de autenticação/credenciais/chaves
    if any(k in key_lower for k in ["password", "token", "secret", "jwt", "auth", "credential"]):
        if "bearer" in val.lower():
            return "Bearer [REDACTED]"
        return "[REDACTED]"
        
    # 2. Redação para e-mail na chave
    if "email" in key_lower:
        return "[REDACTED_EMAIL]"
        
    # 3. Redação para nome na chave
    if "name" in key_lower:
        return "[REDACTED_NAME]"

    # 4. Redação especial para chaves de CPF/CNPJ/documentos
    if any(k in key_lower for k in ["cpf", "cnpj", "document"]):
        clean_digits = "".join(c for c in val if c.isdigit())
        if len(clean_digits) == 11:
            return "***.***.***-" + clean_digits[-2:]
        elif len(clean_digits) == 14:
            return "**.***.****/****-" + clean_digits[-2:]

    # 5. Substituição genérica de padrões no valor da string
    # Formatos estruturados de CPF/CNPJ
    val = CPF_PATTERN.sub(lambda m: "***.***.***-" + m.group()[-2:], val)
    val = CNPJ_PATTERN.sub(lambda m: "**.***.****/****-" + m.group()[-2:], val)
    
    # Raw CPF/CNPJ
    val = RAW_CPF_PATTERN.sub(lambda m: "*********" + m.group()[-2:], val)
    val = RAW_CNPJ_PATTERN.sub(lambda m: "************" + m.group()[-2:], val)
    
    # E-mail
    val = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", val)
    
    return val


def sanitize_value(val, key_name: str = ""):
    if isinstance(val, str):
        return sanitize_string_value(val, key_name)
    elif isinstance(val, (list, tuple)):
        return type(val)(sanitize_value(x, key_name) for x in val)
    return val


class PIISanitizingSpanProcessor(SpanProcessor):
    """
    SpanProcessor customizado para sanitização de PII (CPF, CNPJ, E-mail, Nomes, Senhas e Tokens)
    antes de exportar para o OpenTelemetry Collector.
    """
    def on_start(self, span, parent_context=None):
        pass

    def on_end(self, span) -> None:
        # 1. Sanitizar o nome do span
        if span.name:
            span._name = sanitize_string_value(span.name)

        # 2. Sanitizar os atributos do span
        if span._attributes:
            for key in list(span._attributes.keys()):
                val = span._attributes[key]
                span._attributes[key] = sanitize_value(val, key)


def setup_telemetry(app: FastAPI):
    """
    Configura o OpenTelemetry (Tracing) para a aplicação FastAPI.
    Lê variáveis de ambiente OTEL_SERVICE_NAME e OTEL_EXPORTER_OTLP_ENDPOINT.
    """
    service_name = os.getenv("OTEL_SERVICE_NAME", "servicoja-api")
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

    # Se não houver endpoint configurado, não inicializamos o exporter
    if not otlp_endpoint:
        print("⚠️ Telemetria: OTEL_EXPORTER_OTLP_ENDPOINT não definido, tracing desabilitado.")
        return

    # Definir o recurso (Resource)
    resource = Resource.create(attributes={
        "service.name": service_name
    })

    # Configurar o Provider de Tracing
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Adicionar o processador de sanitização de PII
    provider.add_span_processor(PIISanitizingSpanProcessor())

    # Configurar o exportador OTLP
    otlp_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        insecure=True  # Localmente, geralmente não usamos TLS
    )
    
    # Processador em lote para enviar spans
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)

    # Instrumentar a aplicação FastAPI
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    print(f"📡 Telemetria: OpenTelemetry configurado com endpoint {otlp_endpoint}")
