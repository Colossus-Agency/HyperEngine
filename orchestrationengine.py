"""
Orchestration Engine
--------------------
The authority layer that coordinates all other engines.

This engine:
- Owns time
- Owns execution order
- Owns shared world state
- Enforces engine contracts
- Handles conflicts & failures
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import time
import traceback


# =========================
# Engine Interface (Contract)
# =========================

class BaseEngine(ABC):
    """
    All engines must inherit from this.
    """

    name: str = "UnnamedEngine"
    priority: int = 100  # lower = runs earlier

    @abstractmethod
    def on_register(self, world_state: Dict[str, Any]) -> None:
        """Called once when the engine is registered."""
        pass

    @abstractmethod
    def step(self, world_state: Dict[str, Any], delta_time: float) -> None:
        """Called every tick."""
        pass

    @abstractmethod
    def on_shutdown(self, world_state: Dict[str, Any]) -> None:
        """Called when orchestration engine shuts down."""
        pass


# =========================
# Orchestration Engine
# =========================

class OrchestrationEngine:
    def __init__(self, tick_rate: float = 60.0, strict: bool = True):
        """
        :param tick_rate: ticks per second
        :param strict: if True, crash engine on failure. If False, isolate it.
        """
        self.tick_rate = tick_rate
        self.tick_duration = 1.0 / tick_rate
        self.strict = strict

        self.engines: List[BaseEngine] = []
        self.running = False

        self.world_state: Dict[str, Any] = {
            "time": 0.0,
            "tick": 0,
            "entities": {},
            "events": [],
            "meta": {}
        }

    # =========================
    # Engine Management
    # =========================

    def register_engine(self, engine: BaseEngine):
        if not isinstance(engine, BaseEngine):
            raise TypeError("Engine must inherit from BaseEngine")

        print(f"[Orchestrator] Registering engine: {engine.name}")
        self.engines.append(engine)

        # Sort by priority
        self.engines.sort(key=lambda e: e.priority)

        try:
            engine.on_register(self.world_state)
        except Exception as e:
            self._handle_engine_error(engine, e)

    def unregister_engine(self, engine_name: str):
        self.engines = [e for e in self.engines if e.name != engine_name]
        print(f"[Orchestrator] Unregistered engine: {engine_name}")

    # =========================
    # Execution Control
    # =========================

    def start(self):
        print("[Orchestrator] Starting")
        self.running = True
        self._run_loop()

    def stop(self):
        print("[Orchestrator] Stopping")
        self.running = False
        for engine in self.engines:
            try:
                engine.on_shutdown(self.world_state)
            except Exception as e:
                self._handle_engine_error(engine, e)

    def step_once(self):
        """Run a single tick (useful for testing or external control)."""
        self._tick()

    # =========================
    # Core Loop
    # =========================

    def _run_loop(self):
        last_time = time.time()

        while self.running:
            now = time.time()
            delta_time = now - last_time

            if delta_time >= self.tick_duration:
                last_time = now
                self._tick()
            else:
                time.sleep(self.tick_duration - delta_time)

    def _tick(self):
        self.world_state["tick"] += 1
        self.world_state["time"] += self.tick_duration

        # Clear transient events each tick
        self.world_state["events"].clear()

        for engine in list(self.engines):
            try:
                engine.step(self.world_state, self.tick_duration)
            except Exception as e:
                self._handle_engine_error(engine, e)

    # =========================
    # Error Handling & Policy
    # =========================

    def _handle_engine_error(self, engine: BaseEngine, error: Exception):
        print(f"[Orchestrator] ERROR in engine '{engine.name}'")
        traceback.print_exception(type(error), error, error.__traceback__)

        if self.strict:
            print("[Orchestrator] Strict mode enabled. Shutting down.")
            self.stop()
            raise error
        else:
            print(f"[Orchestrator] Isolating engine '{engine.name}'")
            self.unregister_engine(engine.name)

    # =========================
    # Introspection
    # =========================

    def list_engines(self) -> List[str]:
        return [engine.name for engine in self.engines]

    def get_world_state(self) -> Dict[str, Any]:
        return self.world_state