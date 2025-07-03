from crewai.flow.flow import Flow, listen, start, router
from crewai import Agent, Crew, Task, Process, TaskOutput, LLM
from crewai.tools import tool
from pydantic import BaseModel
from configs.llm_config import generative_model, LLM_PROVIDER
from dotenv import load_dotenv
import os
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource


llm = LLM(
    model=LLM_PROVIDER,
    api_key=os.getenv("GEMINI_API_KEY"),
)

KNOWLEDGEBASE_FILE = "knowledgebase.txt"


@tool("update knowledgebase")
def update_knowledgebase(content: str):
    """Update the knowledgebase with new content.

    Args:
        content (str): The content to be added to the knowledgebase.
    Returns: None
    Raises: None
    """
    with open(KNOWLEDGEBASE_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip())
    print(f"[KnowledgeBaseTool] Appended new content to knowledgebase file.")


def load_knowledgebase():
    if os.path.exists(KNOWLEDGEBASE_FILE):
        with open(KNOWLEDGEBASE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return content
    return ""

def course_classifier(question: str, course_labels: list[str]) -> str:
    prompt = (
        f"You are an intelligent course classifier. Given a student's query and a list of available subjects, "
        f"your job is to return the most appropriate subject from the list below.\n\n"
        f"### Available Subjects: {', '.join(course_labels)}\n\n"
        f"### Student Query:\n{question}\n\n"
        f"### Instructions:\n"
        f"- Analyze the query and match it to the most appropriate subject from the available list.\n"
        f"- Consider the query content and match it to the most relevant course/subject.\n"
        f"- Your response MUST be exactly one of the subject names listed above.\n"
        f"- Do NOT add any explanation, context, or commentary.\n"
        f"- If the query does NOT clearly match any subject, return: None\n"
        f"- Capitalization must match exactly.\n\n"
        f"### Output Format:\nJust return the exact subject label, or 'None'.\n"
    )

    response = generative_model.invoke(prompt)
    print(f"[CourseClassifierTool] Response: {response.content}")

    return response.content.strip()


class FlowState(BaseModel):
    course_labels: list[str] = [
        "Structured Programming Language",
        "Database Management Systems",
        "Object Oriented Programming",
        "Physics",
    ]
    course: str = "None"
    latest_question: str = ""


class CentralizedFlow(Flow[FlowState]):

    @start()
    def init(self, user_input: str):
        print("Initializing Centralized Flow...")
        self.state.latest_question = user_input
        self.state.course = course_classifier(user_input, self.state.course_labels)

    @router("init")
    def course_router(self):
        if self.state.course == "None":
            print(
                f"[CentralizedFlow] No course matched for query: {self.state.latest_question}"
            )
            return "fallback"
        else:
            print(f"[CentralizedFlow] Course matched: {self.state.course}")
            # return self.state.course
            return "fallback"


from crewai.flow.flow import Flow, listen, start, router
from crewai import Agent, Crew, Task, Process
from crewai.tools import tool
from pydantic import BaseModel
from configs.llm_config import generative_model, LLM_PROVIDER


def course_classifier(question: str, course_labels: list[str]) -> str:
    prompt = (
        f"You are an intelligent course classifier. Given a student's query and a list of available subjects, "
        f"your job is to return the most appropriate subject from the list below.\n\n"
        f"### Available Subjects: {', '.join(course_labels)}\n\n"
        f"### Student Query:\n{question}\n\n"
        f"### Instructions:\n"
        f"- Analyze the query and match it to the most appropriate subject from the available list.\n"
        f"- Consider the query content and match it to the most relevant course/subject.\n"
        f"- Your response MUST be exactly one of the subject names listed above.\n"
        f"- Do NOT add any explanation, context, or commentary.\n"
        f"- If the query does NOT clearly match any subject, return: None\n"
        f"- Capitalization must match exactly.\n\n"
        f"### Output Format:\nJust return the exact subject label, or 'None'.\n"
    )

    response = generative_model.invoke(prompt)
    print(f"[CourseClassifierTool] Response: {response.content}")

    return response.content.strip()


class FlowState(BaseModel):
    course_labels: list[str] = [
        "Structured Programming Language",
        "Database Management Systems",
        "Object Oriented Programming",
        "Physics",
    ]
    course: str = "None"
    latest_question: str = ""


class CentralizedFlow(Flow[FlowState]):

    @start()
    async def init(self):
        if not self.state.latest_question:
            raise ValueError("No question found in state!")
        print("Initializing with:", self.state.latest_question)
        self.state.course = course_classifier(
            self.state.latest_question, self.state.course_labels
        )
        return "initialized"

    @router("init")
    def course_router(self):
        if self.state.course == "None":
            print(
                f"[CentralizedFlow] No course matched for query: {self.state.latest_question}"
            )
            return "fallback"
        else:
            print(f"[CentralizedFlow] Course matched: {self.state.course}")
            return "fallback"

    @listen("fallback")
    def fallback_method(self):
        print(
            f"[CentralizedFlow] Fallback triggered for query: {self.state.latest_question}"
        )
        
        knowledgebase_content = load_knowledgebase()

        role = "General Academic Support Tutor"

        backstory = (
            "You are a helpful academic support tutor who provides general assistance across a wide range of standard academic subjects "
            "at University level. "
            "You are NOT a subject matter expert and do not provide deep or specialized explanations. "
            "Your role is to assist students in understanding basic academic concepts in a simplified and accessible way. "
            "You must never provide any information, advice, or opinions on non-academic topics, including personal, medical, legal, financial, or mental health matters. "
            "If a query falls outside of your permitted scope, politely decline and direct the student to a qualified professional."
        )

        goal = (
            "Provide general academic guidance on common educational topics, ensuring that your explanations are simple, accurate, and beginner-friendly. "
            "Avoid going into expert-level detail or using complex terminology. "
            "Do not answer questions outside the academic domain. "
            "If the student's question is about personal issues, health, law, or other sensitive areas, state clearly that you cannot help with such topics. "
            "Always keep responses educational and relevant to standard academic learning only.\n\n"
            "- If the student mentions anything about their personal learning style, name, preferences, struggles, or goals, "
            "store it using the `update_knowledgebase` tool.\n"
            "If user's question is about their preferences/stored data, response that.\n"
            f"Student's query: {self.state.latest_question}"
        )

        # Only use knowledge if there's something in the knowledgebase
        knowledge_sources = []
        if knowledgebase_content.strip():
            string_source = StringKnowledgeSource(content=knowledgebase_content)
            knowledge_sources.append(string_source)

        base_agent = Agent(
            role=role,
            backstory=backstory,
            goal=goal,
            verbose=True,
            llm=llm,
            tools=[update_knowledgebase],
            knowledge_sources=knowledge_sources,  # only pass if not empty
        )

        fallback_task = Task(
            name="Fallback Task",
            description="Handle general fallback queries",
            agent=base_agent,
            expected_output="Provide general academic assistance based on the student's query.",
        )

        crew = Crew(
            agents=[base_agent],
            verbose=True,
            tasks=[fallback_task],
            knowledge_sources=knowledge_sources,
            embedder={
                "provider": "google",
                "config": {
                    "api_key": os.getenv("GEMINI_API_KEY"),
                    "model": "text-embedding-004",
                },
            },
        )

        result = crew.kickoff()

        return result
