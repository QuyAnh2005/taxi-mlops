"""OpenTelemetry tracing setup for Jaeger"""

import os
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = None
    TracerProvider = None


def setup_tracing(service_name: str = "taxi-mlops") -> None:
    """
    Set up OpenTelemetry tracing with Jaeger

    Args:
        service_name: Name of the service for tracing
    """
    if not OPENTELEMETRY_AVAILABLE:
        print("Warning: opentelemetry not installed. Tracing disabled.")
        return

    jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")

    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))

    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_AGENT_HOST", "localhost"),
        agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
        endpoint=jaeger_endpoint,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)


def get_tracer(name: str = "taxi-mlops"):
    """
    Get a tracer instance

    Args:
        name: Tracer name

    Returns:
        Tracer instance or None if OpenTelemetry not available
    """
    if not OPENTELEMETRY_AVAILABLE:
        return None

    return trace.get_tracer(name)

