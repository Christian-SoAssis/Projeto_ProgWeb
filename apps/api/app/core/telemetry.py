import os
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


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
