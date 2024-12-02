from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from starlette.responses import Response
from prometheus_client import Counter, generate_latest

# Initialize FastAPI app
app = FastAPI()

# Configure OpenTelemetry
resource = Resource(attributes={
    "service.name": "my-fastapi-app",
})

tracer_provider = TracerProvider(resource=resource)
span_processor = BatchSpanProcessor(OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True,
))
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

# Instrument FastAPI app
FastAPIInstrumentor.instrument_app(app)

@app.get("/")
async def read_root():
    return {"message": "Hello, SigNoz!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
def metrics():
    # Expose metrics in Prometheus format
    return Response(content=generate_latest(), media_type="text/plain")