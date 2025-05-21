from worker_agents.search_agent import flight_search_agent

print(flight_search_agent.invoke({"messages": [("user", "Find me a flight from Ahmedabad to Hyderabad on 2023-09-10")]}))