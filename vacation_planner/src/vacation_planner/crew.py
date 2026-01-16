from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List
import boto3
from datetime import datetime
import uuid
from bedrock_agentcore.runtime import BedrockAgentCoreApp
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

tool = SerperDevTool()

app = BedrockAgentCoreApp()
client = boto3.client("bedrock-agentcore", region_name='ap-south-1')

@CrewBase
class VacationPlanner():
    """VacationPlanner crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def vacation_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['vacation_researcher'], # type: ignore[index]
            tools=[tool],
            verbose=True
        )

    @agent
    def itinerary_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_planner'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the VacationPlanner crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )


@app.entrypoint
def agent_invocation(payload, context):
    """
    Invoke the crew with a payload
    """
    try:
        user_input = payload.get("topic")
        crew = VacationPlanner().crew()
        
        # Retrieve Past Memory
        session_id = getattr(context, "sessionId", "default_session")
        history = client.list_events(
            memoryId="",
            sessionId=session_id,
            actorId="user",
            maxResults=10
        )
        
        #Format the date to iso format (Crew AI requirement)
        events = history.get("events", [])
        formatted_history = []
        for event in events:
            formatted_event = {}
            for key, value in event.items():
                if isinstance(value, datetime):
                    formatted_event[key] = value.isoformat()
                else:
                    formatted_event[key] = value
            formatted_history.append(formatted_event)
        
        # Run the crew
        result = crew.kickoff(inputs={"topic": user_input, "previous_conversations": formatted_history})
        
        client.create_event(
            memoryId="",
            actorId="user",
            sessionId=session_id,
            eventTimestamp=datetime.utcnow(),
            payload=[
                {
                    "conversational": {
                        "content": {"text": user_input},
                        "role": "USER"
                    }
                },
                {
                    "conversational": {
                        "content": {"text": result.raw},
                        "role": "ASSISTANT"
                    }
                }
            ],
            clientToken=str(uuid.uuid4())
        )
        
        print(f"Result :: {result.raw}")
        # Return the result
        return {"result": result.raw}
    except Exception as e:
        print(f"Exception Occurred: {e}")
        return {"error": f"An error occurred: str(e)"}


def test_agent():
    try:
        print("Started", datetime.now())
        user_input = "Bangalore"
        crew = VacationPlanner().crew()
        result = crew.kickoff(inputs={"topic": user_input})
        print("Ended", datetime.now())
        print(f"Result :: {result.raw}")
        return {"result": result.raw}
    except Exception as e:
        print(f"Exception Occurred: {e}")
        return {"error": f"An error occurred: str(e)"}

if __name__ == "__main__":
    # app.run()
    test_agent()