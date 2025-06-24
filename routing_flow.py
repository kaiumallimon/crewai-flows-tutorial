from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
import random
import uuid

class ExampleState(BaseModel):
  isAuthenticated: bool = False
  userId: str = None


class RouterExampleFlow(Flow[ExampleState]):
  
  @start()
  def start_method(self):
    print("Starting the router flow ...")
    
    random_value = random.choice([True,False])
    self.state.isAuthenticated = random_value
    
  @router(start_method)
  def authenticate(self):
    if self.state.isAuthenticated:
      self.state.userId = uuid.uuid4()
      return "dashboard"
    else:
      return "login"
    
  @listen("dashboard")
  def dashboard_method(self):
    print(f"Login Successful, user id: {self.state.userId}")
    
  @listen("login")
  def login_method(self):
    print("Wrong credentials, authentication failed")
    

flow = RouterExampleFlow()
flow.plot("my_test_flow_plot")
flow.kickoff()