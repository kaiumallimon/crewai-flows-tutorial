from crewai.flow.flow import Flow, listen, start


class UnstructuredFlow(Flow):

    @start()
    def method1(self):
        print("Starting flow...")
        print(f"State before executing of any state updates: {self.state}")
        self.state["message"] = "Initial message"
        self.state["counter"] = 0

    @listen(method1)
    def method2(self):
        print(f"State before updating state in method2: {self.state}")
        self.state["message"] += " -- First update"
        self.state["counter"] += 1

    @listen(method2)
    def method3(self):
        print(f"State before updating state in method3: {self.state}")
        self.state["message"] += " -- Second update"
        self.state["counter"] += 1


flow = UnstructuredFlow()
# flow.plot("unstructured_flow_plot")
flow.kickoff()

print(f"State after executing all the flows: {flow.state}")
