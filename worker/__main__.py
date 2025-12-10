import asyncio
from temporalio.worker import Worker
from temporalio.client import Client
from worker.workflows import CsvIngestWorkflow
from worker.activities import process_csv

async def main():
    client = await Client.connect("temporal:7233")

    worker = Worker(
        client,
        task_queue="csv-task-queue",
        workflows=[CsvIngestWorkflow],
        activities=[process_csv],
    )

    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
