from uuid import UUID

from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.pinterpreter import InterpreterContext
from openpectus.lang.exec.tags import TagCollection


class EngineInterpreterContext(InterpreterContext):
    def __init__(self, engine: 'Engine') -> None:
        super().__init__()
        self.engine = engine
        self._tags = engine.uod.system_tags.merge_with(engine.uod.tags)

    @property
    def tags(self) -> TagCollection:
        return self._tags

    def schedule_execution(self, name: str, args: str | None = None, exec_id: UUID | None = None) -> CommandRequest:
        return self.engine.schedule_execution(name, args, exec_id)
