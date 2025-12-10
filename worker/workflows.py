from temporalio import workflow
from datetime import timedelta

with workflow.unsafe.imports_passed_through():
    from worker.activities import process_csv

@workflow.defn
class CsvIngestWorkflow:
    @workflow.run
    async def run(self, file_name: str):
        await workflow.execute_activity(
            process_csv,
            file_name,
            schedule_to_close_timeout=timedelta(seconds=10),
        )
