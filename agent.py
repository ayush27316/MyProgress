from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Iterator, Optional, Literal, Dict, Tuple   
from enum import Enum
from transcript import *
from common import *
import os
from dotenv import load_dotenv
import json
from xai_sdk import Client
from xai_sdk.chat import tool, tool_result, user, system
from pydantic import BaseModel, Field
from program import *

class Status(Enum):
    FULFILLED = "FULFILLED"
    UNFULFILLED = "UNFULFILLED"


class AgentBlockReport(BaseModel):
    """     
    A BlockReport represents a report of a Block. A Block is "block of requirements".
    Each Block can be of only 4 types; PROGRAM, REQUIRED, COMPLEMENTARY, CUSTOM. 
    A PROGRAM can contain either REQUIRED or COMPLEMENTARY or both blocks. A COMPLEMENTARY Block 
    further can have one or more CUSTOM blocks. Example Report:
    { 
        "name": "XYZ Major",
        "minimum_credit": 36,
        "received_credit":21,
        "block_type":"PROGRAM",
        "notes":["overall need 15 more credits" ],
        "status": "UNFULFILLED",
        "courses": [], //shoudl be left empty for block's of type PROGRAM 
        "blocks":[
                    {
                        "name": "Required Courses",
                        "minimum_credit": 18,
                        "received_credit":12,
                        "block_type":"REQUIRED",
                        "status": "UNFULFILLED",
                        "courses": [('MATH', '223','3'),('MATH', '318','3'),('MATH', '340','3'),('MATH', '370','3')],
                        "notes": ["need 6 credits from MATH 389, MATH 240"],
                        "blocks":[],
                    },
                    {
                        "name": "Complementary Courses",
                        "minimum_credit": 18,
                        "received_credit":6,
                        "block_type":"COMPLEMENTARY",
                        "status": "UNFULFILLED",
                        "courses": [('MATH', '223','3')], //courses that generally goes to the complementary block and not to any specific CUSTOM block
                        "notes": ["need 3 more credits from Group A","9 credit from any MATH courses 300 level and above except MATH 389"],
                        "blocks":[
                            {
                                "name": "Group A",
                                "block_type": "CUSTOM",
                                "courses": [('PHYS', '141','3')],
                            }
                        ],
                    }    
                ]
    }
    """
   
    name: str = Field(description="Name of the block. eg:'Major Mathematics','Required Courses', 'Group A', 'Complementary Courses' etc.")
    minimum_credit: Optional[int] = Field(default=None, description="Minimum credit requierments for this block. Must be 0 skipped for CUSTOM blocks.")
    received_credit: Optional[int] = Field(default=None,description="Total credit recieved for this block. For COMPLEMENTARY block total credit count includes the credit recieved for contained CUSTOM blocks. SO, for CUSTOM blocks this field can be skipped.")
    block_type: BlockType
    notes: List[str] = Field(default_factory=list,
        description="""
            Notes can be dropped to specifiy the requirements that is still needed to be 
            fufilled for this block. When requirements have not been fulfilled. Provide a 1 line note 
            on what is needed. For example: 'Need (COMP 230 or COMP 350) and MATH 360 ', 'need 6 credits 
            from Ecom 300 level and above'", "need 8 credits from COMP courses 300 level and above except COMP 396".
            When there is a big list of courses (generally from a block), then you can directly refer 
            to block's name. For example: "need 6 more credits from block A". Since, the structure is recursive 
            makes sure we do not repeat notes.
        """)
    
    status: Status= Field(description="If all the requirements of this block has been fulfilled then status is FULFILLED otherwise UNFULFILLED.")  
    courses: List[Tuple[str,str,str]]  = Field(default_factory=list, description="Courses fulfilling this block's requirements. Example: [('MATH','223','3'),('COMP','206','4'))]")
    blocks:  Optional[List[AgentBlockReport]] = Field(default_factory=list, description="Only PROGRAM, and COMPLEMENTARY blocks can further have nested blocks.")
    
    def to_dict(self):
        """Convert this report (and all nested reports) into a plain dict."""
        return {
            "name": self.name,
            "minimum_credit": self.minimum_credit,
            "received_credit": self.received_credit,
            "block_type": self.block_type.value,   # Enum → string
            "notes": self.notes,
            "status": self.status.value,           # Enum → string
            "courses": self.courses,
            "blocks": [b.to_dict() for b in self.blocks],  # recursive
        }

AGENT_INSTRUCTIONS="""
You are a degree audit agent. A degree consists of multiple Programs. A Program consists of 
Blocks (Blocks of requirements). Each Block can be of 4 types; PROGRAM, REQUIRED, COMPLEMENTARY, CUSTOM. 
A Degree, Program and Blocks are Entities; entities that comes with there requirements. Each Entity can 
be in either of the two states; FULFILLED, UNFULFILLED. An Entity is considered FULFILLED if all its 
requirements are fulfilled. A Transcript is a list of Courses that student took. A Report describes 
what Courses from the Transcript can be associated with which Entities and what Courses are still needed 
to be taken.

Important Note on Handling Course Selection:-
1. No Course Reuse
    - A single course may fulfill only one block or sub-block.
    - Once a course is selected for a sub-block, it **cannot appear again** in the general complementary block or another sub-block.

2. Satisfy Minimum Credits
    - Fulfill the minimum required credits for each block or sub-block.
    - Do not exceed the minimum unless necessary to meet a structural constraint (e.g., a 3-credit course needed to reach a 2-credit gap).

3. Selection Priorities
    - Prefer lower-level courses (e.g., 200-level before 400-level) and smaller credit values when multiple valid options exist.
    - Follow any listed inclusion/exclusion rules carefully (e.g., “except MATH 396” or “only 300-level ECON courses”).
    - To fulfill requirements a course from the same department as the one that is offering the program must be preferred over courses from different department.
4. Clarity of Unfulfilled Requirements
    - If a block’s requirements are not yet fulfilled, clearly specify what is still needed using short, precise statements (e.g., “Need 3 credits from Group C” or “Need one COMP course 300-level or above”).
## Steps To Follow:-
1. Process Required Blocks:- First go through program's required Block associate as many course to it as required. 
2. Process Complementary Blocks:- Go though program's complementary Block and associate courses (that were not used for the required block) to it based on the rules. 
3. Exemption Handling: Wether or not to grant an exemption is upto the advisor. So unless speicifcally told student wont be exempt from a rquirement. SO, you do need to handle situation as if the student is not exempt.
## Input:
1:- Program Information: A program report is created iteratively one by one. You will recieve previous reports. So, that you can see what has already been used.
2:- Transcript: All the courses that student took.
3:- Previously generated Report by You.
You output:- You output is a Report and should be strucutured with AgentResult schema.
"""

class TaskStatus:
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED" 
    IDLE = "IDLE"

class AgentException(Exception):
    pass

class Agent:
    controller: "AgentController"
    programs: List[Block] 
    transcript: Transcript 
    current_block_idx:int
    reports: List[AgentBlockReport]
    status: TaskStatus
    def __init__(self,controller:"AgentController"):
        self.controller = controller
        self.transcript = controller.get_context().transcript
        self.logger = get_logger() 
        self.reports = []
        self.max_retries = 3
        self.programs = []
        self.current_block_idx = 0
        self.status = TaskStatus.IDLE

        # self.fetcher = ProgramFetcher(config=FetchConfig(
        #     debug_mode=True,
        #     debug_get_program=get_program,
        #     max_workers=1
        # ))


    def on_fetch_complete(self,programs, failed):
        self.programs = programs
        print([program.to_dict() for program in programs])
        if failed:
            raise ValueError("Fetch Failed")

    def init_fetch(self):
        thread = self.fetcher.fetch_programs_async(
            self.transcript.get_program_titles(),
            on_complete=self.on_fetch_complete
        )
        thread.join()
    
    def get_current_program_block(self)->Block:
        if self.current_block_idx == -1:
            return None
        return self.programs[self.current_block_idx]

    def next_program_block(self):
        if self.current_block_idx == -1:
            return
            
        self.current_block_idx += 1

        # If we moved past the last index, mark as done
        if self.current_block_idx >= len(self.programs):
            self.current_block_idx = -1
  
    def get_usable_courses_serializable(self):
        result = []
        for course in self.transcript:
            if course.is_usable():
                d = course.to_dict_full()
                d.pop("done", None)  # safely remove key if it exists
                result.append(d)
        return result
    

    def has_more_programs(self) -> bool:
        return 0 <= self.current_block_idx < len(self.programs)

    def start(self):
         #shoudl be doing this when started
    #     # self.init_fetch()

        for title in self.transcript.get_program_titles():
            self.programs.append(get_program(title))
        
        while self.has_more_programs():
            self.status = TaskStatus.ACTIVE
            program = self.get_current_program_block()
            self._process(program)
            if self.status == TaskStatus.FAILED:
                raise AgentException("[Agent]: An exception occurred")
            self.next_program_block()
        
        self.status = TaskStatus.COMPLETED
        return self.reports

    # def start(self):
    #     #shoudl be doing this when started
    #     # self.init_fetch()

    #     #init report based of programs
    #     for title in self.transcript.get_program_titles():
    #         self.programs.append(get_program(title))
        
    #     while True:
    #         self.status = TaskStatus.ACTIVE
    #         program = self.get_current_program_block()
    #         if program is None:
    #             break
    #         self._process(program)
    #         if self.status == TaskStatus.FAILED:
    #             raise AgentException("[Agent]: An Exception occured")
    #         self.next_program_block()
    #     self.status = TaskStatus.COMPLETED
    #     return self.reports
        
    def _process(self,program):
        for attempt in range(1, self.max_retries + 1):
            try:
                chat = self.controller.client.chat.create(
                    model="grok-4-fast-reasoning", #grok-4-latest grok-4-fast-reasoning grok-3-mini
                    # reasoning_effort = "low",
                    max_tokens=10000,
                    temperature=0.0,
                    top_p= 1.0)
            
                chat.append(system(AGENT_INSTRUCTIONS))
            
                chat.append(
                    user(
                        json.dumps( {
                                "program_details":program.to_dict(),
                                "transcript" : self.get_usable_courses_serializable(),
                                "reports": [report.to_dict() for report in self.reports]
                            },
                            indent=1
                            )
                        )
                    )
                response, result = chat.parse(AgentBlockReport)
                assert isinstance(result, AgentBlockReport)
                # self.logger.info(response)
                self.reports.append(result)
                self.status = TaskStatus.COMPLETED
                return
            except Exception as e:
                self.logger.error(f"[Agent]Unexpected error on attempt: {str(e)}")
                if attempt == self.max_retries:
                    self.status = TaskStatus.FAILED
                    return
                continue



            
        
