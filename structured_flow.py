from crewai.flow.flow import Flow, start, listen
from pydantic import BaseModel


'''
This example demonstrates a structured flow using CrewAI's Flow framework.
The flow consists of two methods:
1. `method1`: This is the starting point of the flow. It initializes the flow state and performs some updates.  
2. `method2`: This method listens to the output of `method1` and performs further updates to the flow state.  

The flow state is defined using a Pydantic model, `ExampleState`, which contains two fields: `message` and `counter`. 
The flow state is updated in both methods, and the updates are printed to the console.
'''

# Define the flow state using Pydantic model
class ExampleState(BaseModel):
  message:str = 'Initial Message'
  counter:int = 0

# Define the structured flow  
class StructuredFlow(Flow[ExampleState]):
  # Define the flow state
  # state = ExampleState()
  
  # start method to initialize the flow
  @start()
  def method1(self):
    print("Starting flow...")
    print(f'LOGGER :: Before updating State: {self.state}')
    
    # Update the flow state
    self.state.message += ' -- Update (1)'
    self.state.counter = self.state.counter+1
    
    print(f"LOGGER :: After updating State inside method1: {self.state}")
   
  # listen to the output of method1 
  @listen(method1)
  def method2(self):
    print("Inside method2:")
    
    # Update the flow state
    self.state.message += ' -- Update (2)'
    self.state.counter = self.state.counter+1
    
    print(f"LOGGER :: After updating State inside method2: {self.state}")
  

# Create an instance of the structured flow and kickoff the flow
# (start the execution)
flow = StructuredFlow()
flow.kickoff()