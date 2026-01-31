from orchestrationengine import OrchestrationEngine
from inputengine import InputEngine

orchestrator = OrchestrationEngine(tick_rate=10, strict=False)
orchestrator.register_engine(InputEngine())

orchestrator.start()