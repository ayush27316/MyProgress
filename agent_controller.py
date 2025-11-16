import os
import json
from transcript import *
from dotenv import load_dotenv
from xai_sdk import Client
from agent import *
from common import *


load_dotenv()
@dataclass
class Context:
    transcript: Transcript

class AgentController:
    client : Client
    agent: Agent
    context: Context

    def __init__(self, transcript: Transcript):
        self.client = Client(    
            api_key=os.getenv("XAI_API_KEY"),
            timeout=3600, # Override default timeout with longer timeout for reasoning models
        )
        self.logger = get_logger(__name__)  
        self.reports = []
        self.context = Context(transcript)

        self.agent = Agent(self)

    def get_context(self):
        return self.context

    def start(self):
        self.reports = self.agent.start() 

    def get_report_serializable(self):
        self.logger.info(json.dumps([report.to_dict() for report in self.reports],indent=2))
        return [report.to_dict() for report in self.reports]
    
_TEST_TRANSCRIPT = (
    Transcript()
    .add_program("Computer Science Major Concentration (B.A.)")
    #.add_program("Mathematics - Major Concentration (B.A. & Sc.)")
    .add_program("Economics Major Concentration (B.A.)")
    .add_course(subject_code="COMP", course_code="206", grade="B+", credit=3)
    .add_course(subject_code="MATH", course_code="133", grade="A", credit=3)
    .add_course(subject_code="MATH", course_code="140", grade="A", credit=3)
    .add_course(subject_code="PHYS", course_code="142", grade="A", credit=4)
#    .add_course(subject_code="COMP", course_code="202", grade="A-", credit=3)
    .add_course(subject_code="COMP", course_code="360", grade="C+", credit=3)
    .add_course(subject_code="MATH", course_code="204", grade="B-", credit=3)
    .add_course(subject_code="MATH", course_code="243", grade="A", credit=3)
    .add_course(subject_code="MATH", course_code="315", grade="C+", credit=3)
    .add_course(subject_code="MATH", course_code="447", grade="C", credit=3)
    .add_course(subject_code="COMP", course_code="250", grade="B-", credit=3)
    .add_course(subject_code="MATH", course_code="141", grade="A", credit=4)
    .add_course(subject_code="MATH", course_code="223", grade="A-", credit=3)
    .add_course(subject_code="MATH", course_code="240", grade="B-", credit=3)
    .add_course(subject_code="COMP", course_code="273", grade="C", credit=3)
    .add_course(subject_code="COMP", course_code="302", grade="C+", credit=3)
    .add_course(subject_code="MATH", course_code="222", grade="C", credit=3)
    .add_course(subject_code="MATH", course_code="356", grade="C", credit=3)
    .add_course(subject_code="COMP", course_code="251", grade="C", credit=3)
    .add_course(subject_code="FRSL", course_code="105", grade="A", credit=6)
    .add_course(subject_code="MATH", course_code="242", grade="B", credit=3)
    .add_course(subject_code="MATH", course_code="323", grade="B", credit=3)
    .add_course(subject_code="MATH", course_code="324", grade="B", credit=3)
    .add_course(subject_code="MATH", course_code="314", grade="F", credit=0)
    .add_course(subject_code="FRSL", course_code="215", grade="A", credit=6)
    .add_course(subject_code="FRSL", course_code="101", grade="A", credit=3)
    # .add_course(subject_code="SOCI", course_code="210", grade="A", credit=3)
    # .add_course(subject_code="SOCI", course_code="211", grade="A", credit=3)
    # .add_course(subject_code="PHIL", course_code="200", grade="A", credit=3)
    # .add_course(subject_code="PHIL", course_code="201", grade="A", credit=3)
    .add_course(subject_code="COMP", course_code="350", grade="B+", credit=3)
    .add_course(subject_code="COMP", course_code="409", grade="B+", credit=3)
    .add_course(subject_code="COMP", course_code="553", grade="B+", credit=4)
    
    .add_course(subject_code="ECON", course_code="332", grade="B+", credit=3)
    .add_course(subject_code="ECON", course_code="333", grade="B+", credit=3)

     .add_course(subject_code="ECON", course_code="119", grade="B+", credit=3)
    .add_course(subject_code="ECON", course_code="219", grade="B+", credit=3)
    .add_course(subject_code="ECON", course_code="221", grade="B+", credit=3)

    .add_course(subject_code="ECON", course_code="223", grade="B+", credit=3)
    .add_course(subject_code="ECON", course_code="225", grade="B+", credit=3)

    .add_course(subject_code="COMP", course_code="421", grade="B+", credit=3)

)

if __name__ == "__main__":
    controller = AgentController(_TEST_TRANSCRIPT)
    controller.start()
    controller.get_report_serializable()

    