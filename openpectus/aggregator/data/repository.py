from sqlalchemy import select
from sqlalchemy.orm import Session

from openpectus.aggregator.data.models import BatchJobData


class RepositoryBase():
    def __init__(self, session: Session) -> None:
        self.session = session


class BatchJobDataRepository(RepositoryBase):

    # def upsert(self, process_unit: BatchJobData):
    #     self.session.
    #     process_unit.save()

    def get_by_id(self, id: int) -> BatchJobData | None:
        return self.session.get(BatchJobData, id)

    def get_by_engine_id(self, engine_id: str) -> BatchJobData | None:
        q = select(BatchJobData).where(BatchJobData.engine_id == engine_id)
        result = self.session.execute(q).first()
        if result is None:
            return None
        return result.tuple()[0]
