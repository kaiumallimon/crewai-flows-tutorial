from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from litellm import completion
import requests
import os

# Load environment variables
load_dotenv()

open_weather_map_apikey = os.getenv("OPENWEATHER_MAP_API_KEY")
open_weather_map_url = os.getenv("OPENWEATHER_MAP_URL")

'''
This example demonstrates a basic flow that generates a random city from Europe,
fetches the weather data for that city using the OpenWeatherMap API, and summarizes the weather data.

The flow consists of three steps:
1. Generate a random city from Europe.
2. Fetch the weather data for the generated city.
3. Summarize the fetched weather data.

'''

class ExampleFlow(Flow):
    model = "gemini/gemini-2.0-flash"  

    '''
    Step 1: Generate a random city from Europe.
    
    Start the flow with an initial state.
    The following function is the entry point of the flow.
    It generates a random city from the European continent.
    The `@start` decorator indicates that this function is the starting point of the flow.
      '''
    @start()
    def generate_city(self):
        print("Starting flow")
        print(f"Flow State ID: {self.state['id']}")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": "Return the name of a random city from european continent.",
                },
            ],
        )

        random_city = response["choices"][0]["message"]["content"]
        self.state["city"] = random_city
        print(f"Random City: {random_city}")
        return random_city


    '''
    Step 2: Fetch the weather data for the generated city.
    
    This function listens for the output of the `generate_city` function.
    It uses the OpenWeatherMap API to fetch the weather data for the city.
    The `@listen` decorator indicates that this function will be triggered when the `generate_city` function completes.
    '''
    @listen(generate_city)
    def get_weather_data(self, random_city):
        print(f"Getting weather data for {random_city}")

        params = {
            'q': random_city,
            'appid': open_weather_map_apikey,
            'units': 'metric'  # Use metric for Celsius
        }

        try:
            response = requests.get(open_weather_map_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            self.state["weather_data"] = weather_data
            return weather_data
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

    
    '''
    Step 3: Summarize the fetched weather data.
    
    This function listens for the output of the `get_weather_data` function.
    It uses the Gemini model to summarize the weather data.
    The `@listen` decorator indicates that this function will be triggered when the `get_weather_data` function completes.
    ''' 
    @listen(get_weather_data)
    def summarize_weather(self, weather_data):
        if not weather_data:
            return "Failed to fetch weather data."

        print(f"Weather data: {weather_data}")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following weather data: {weather_data}",
                },
            ],
        )

        summary = response["choices"][0]["message"]["content"]
        self.state["summary"] = summary
        return summary


# Run the flow
flow = ExampleFlow()
flow.plot()
result = flow.kickoff()
print(f"Generated Weather Summary: {result}")
