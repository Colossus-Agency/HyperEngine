from orchestrationengine import BaseEngine


class InputEngine(BaseEngine):
    name = "InputEngine"
    priority = 10  # input runs early

    def on_register(self, world_state):
        world_state["input"] = {
            "keys": set(),
            "mouse": None,
            "raw_events": []
        }

    def step(self, world_state, delta_time):
        """
        For now this is a stub.
        Later this will read from real devices or network.
        """

        # Example: fake key press every 60 ticks
        if world_state["tick"] % 60 == 0:
            event = {
                "type": "key_press",
                "key": "SPACE",
                "time": world_state["time"]
            }

            world_state["events"].append(event)
            world_state["input"]["raw_events"].append(event)

    def on_shutdown(self, world_state):
        pass