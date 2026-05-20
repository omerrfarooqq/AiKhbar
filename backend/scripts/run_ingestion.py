"""CLI: run the news ingestion pipeline once.

Usage (from backend/):
    python -m scripts.run_ingestion
"""
import asyncio

from app.core.logging import configure_logging
from app.services.ingestion_pipeline import run_ingestion


async def _main() -> None:
    configure_logging()
    report = await run_ingestion()
    print("\n=== Ingestion Report ===")
    print(f"  scraped         : {report.scraped}")
    print(f"  new             : {report.new}")
    print(f"  classified      : {report.classified}")
    print(f"  indexed         : {report.indexed}")
    print(f"  clusters_created: {report.clusters_created}")
    if report.errors:
        print(f"  errors          : {report.errors}")


if __name__ == "__main__":
    asyncio.run(_main())
