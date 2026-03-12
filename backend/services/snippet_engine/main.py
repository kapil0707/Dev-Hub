"""
=============================================================================
Snippet Engine — gRPC Code Snippet Service
=============================================================================
Port: 8002  (gRPC port, not HTTP)

RESPONSIBILITY:
    High-performance CRUD for code snippets via gRPC (Protocol Buffers).
    This is the service where you learn gRPC — the binary alternative to REST.

WHY gRPC HERE (not REST)?
    Code snippets can be large (500-1000 lines). Protobuf binary encoding is
    2-3x smaller than JSON. For frequent read operations, this matters.
    Also: gRPC gives us automatic client code generation — define the contract
    in snippet.proto, generate Python client and server stubs automatically.

COMPARISON TO C++ (for your mental model):
    .proto file  ≈  C++ header file (.h) — defines the interface contract
    Generated stub ≈ compiled object file — the implementation machinery
    gRPC call    ≈  function call across network — feels like a local function

DATABASE: PostgreSQL → schema: snippets → table: snippets.snippets

RUN: python main.py  (starts a gRPC server, not uvicorn)
=============================================================================
"""
import asyncio

from dotenv import load_dotenv

from devhub_shared.logging.logger import get_logger

load_dotenv("../../../.env")

logger = get_logger(__name__, service_name="snippet_engine")


async def serve():
    """
    Entry point for the gRPC server.
    In Phase 3, this will start the gRPC ServicerBase implementation.
    """
    logger.info("Snippet Engine gRPC server starting", extra={"port": 8002})
    # TODO (Phase 3): Initialize gRPC server
    # server = grpc.aio.server()
    # snippet_pb2_grpc.add_SnippetServiceServicer_to_server(SnippetServiceServicer(), server)
    # server.add_insecure_port("[::]:8002")
    # await server.start()
    # await server.wait_for_termination()

    # Placeholder: keep alive until Phase 3
    logger.info("Snippet Engine placeholder running. Full gRPC implementation in Phase 3.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(serve())
