from dataclasses import dataclass, field, asdict
from typing import List, Iterator, Optional, Literal, Dict, Tuple
from enum import Enum
from pydantic import BaseModel, ValidationError, Field

PROGRAMS = [
  {
  "minimum_credit": 36,
  "block_type": "PROGRAM",
  "name": "Computer Science Major Concentration (B.A.)",
  "details": [],
  "courses":[],
  "blocks": [
    {
      "name": "Required Courses",
      "minimum_credit": 18,
      "block_type": "REQUIRED",
      "details": [
        "Students who have sufficient knowledge in programming do not need to take COMP 202 Foundations of Programming and should replace it with an additional course from the complementary block."
      ],
      "courses":[('COMP','202','3'),('COMP','206','3'),('COMP','250','3'),('COMP','251','3'),('COMP','273','3'),('MATH','240','3')],
      "blocks": []
    },
    {
      "name": "Complementary Courses",
      "minimum_credit": 18,
      "block_type": "COMPLEMENTARY",
      "details": [
        "18 credits selected as follows: 3 credits from each of the groups A, B, C, and D.",
        "An additional 3 credits may be selected from Group A or B.",
        "The remaining complementary credits must be selected from COMP 230 Logic and Computability and COMP courses at the 300 level or above (except COMP 396 Undergraduate Research Project)."
      ],
      "courses": [],
      "blocks": [
        {
          "name": "Group A",
          "minimum_credit": 3,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [('MATH', '222','3'),('MATH', '323','3'),('MATH', '324','3')],
          "blocks": []
        },
        {
          "name": "Group B",
          "minimum_credit": 3,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [('MATH', '223','3'),('MATH', '318','3'),('MATH', '340','3')],
          "blocks": []
        },
        {
          "name": "Group C",
          "minimum_credit": 3,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [('COMP', '330','3'),('COMP', '350','3'),('COMP', '360','3')],
          "blocks": []
        },
        {
          "name": "Group D",
          "minimum_credit": 3,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [('COMP', '302','3'),('COMP', '303','3')],
          "blocks": []
        }
      ]
    }
  ]
},
{
  "minimum_credit": 36,
  "block_type": "PROGRAM",
  "name": "Sociology - Major Concentration (B.A.)",
  "details": [
    "Offered by: Sociology (Faculty of Arts)",
    "Degree: Bachelor of Arts; Bachelor of Arts and Science",
    "Program credit weight: 36"
  ],
  "description": "The purpose of the Major Concentration in Sociology is to give the student a comprehensive understanding of the field of sociology.",
  "degree": "Bachelor of Arts",
  "faculty": "Faculty of Arts",
  "department": "Sociology",
  "blocks": [
    {
      "name": "Required Courses",
      "minimum_credit": 12,
      "block_type": "REQUIRED",
      "details": [
          "Students may replace SOCI 350 with another 300-level or higher sociology course."
      ],
      "courses": [
        ["SOCI", "210"],
        ["SOCI", "211"],
        ["SOCI", "330"],
        ["SOCI", "350"]
      ],
      "blocks": []
    },
    {
      "name": "Complementary Courses",
      "minimum_credit": 24,
      "block_type": "COMPLEMENTARY",
      "details": [
        "3 credits minimum at the 400 level or higher.",
        "9 credits maximum at the 200 level.",
        "No more than 6 credits of the current problems, independent study and/or reading courses may count toward the Major concentration."
      ],
      "courses": [
        ["SOCI", "341"],
        ["SOCI", "342"],
        ["SOCI", "343"],
        ["SOCI", "441"],
        ["SOCI", "442"],
        ["SOCI", "443"]
      ],
      "blocks": [
        {
          "name": "Institutions, Deviance, and Culture",
          "minimum_credit": 0,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [
            ["SOCI", "213"],
            ["SOCI", "225"],
            ["SOCI", "247"],
            ["SOCI", "250"],
            ["SOCI", "305"],
            ["SOCI", "309"],
            ["SOCI", "310"],
            ["SOCI", "318"],
            ["SOCI", "322"],
            ["SOCI", "325"],
            ["SOCI", "388"],
            ["SOCI", "430"],
            ["SOCI", "488"],
            ["SOCI", "489"],
            ["SOCI", "495"],
            ["SOCI", "503"],
            ["SOCI", "515"],
            ["SOCI", "525"],
            ["SOCI", "535"],
            ["SOCI", "538"],
            ["SOCI", "571"],
            ["SOCI", "595"]
          ],
          "blocks": []
        },
        {
          "name": "Politics and Social Change",
          "minimum_credit": 0,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [
            ["SOCI", "212"],
            ["SOCI", "222"],
            ["SOCI", "234"],
            ["SOCI", "245"],
            ["SOCI", "254"],
            ["SOCI", "255"],
            ["SOCI", "307"],
            ["SOCI", "326"],
            ["SOCI", "345"],
            ["SOCI", "354"],
            ["SOCI", "365"],
            ["SOCI", "370"],
            ["SOCI", "386"],
            ["SOCI", "400"],
            ["SOCI", "424"],
            ["SOCI", "430"],
            ["SOCI", "446"],
            ["SOCI", "455"],
            ["SOCI", "484"],
            ["SOCI", "495"],
            ["SOCI", "507"],
            ["SOCI", "519"],
            ["SOCI", "545"],
            ["SOCI", "550"],
            ["SOCI", "595"]
          ],
          "blocks": []
        },
        {
          "name": "Social Stratification: Class, Ethnicity, and Gender",
          "minimum_credit": 0,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [
            ["SOCI", "227"],
            ["SOCI", "230"],
            ["SOCI", "255"],
            ["SOCI", "270"],
            ["SOCI", "300"],
            ["SOCI", "321"],
            ["SOCI", "333"],
            ["SOCI", "335"],
            ["SOCI", "355"],
            ["SOCI", "366"],
            ["SOCI", "375"],
            ["SOCI", "410"],
            ["SOCI", "415"],
            ["SOCI", "430"],
            ["SOCI", "475"],
            ["SOCI", "505"],
            ["SOCI", "520"],
            ["SOCI", "526"],
            ["SOCI", "530"],
            ["SOCI", "595"]
          ],
          "blocks": []
        },
        {
          "name": "Work, Organizations, and the Economy",
          "minimum_credit": 0,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [
            ["SOCI", "235"],
            ["SOCI", "301"],
            ["SOCI", "304"],
            ["SOCI", "312"],
            ["SOCI", "325"],
            ["SOCI", "420"],
            ["SOCI", "470"]
          ],
          "blocks": []
        }
      ]
    }
  ]
},
{
  "minimum_credit": 46,
  "block_type": "PROGRAM",
  "name": "Mathematics - Major Concentration (B.A. & Sc.)",
  "details": ["An honours equivalent of a course can also be used to fulfill requirements instead of the originally listed selections."],
  "description": "The B.A.; Major Concentration in Mathematics aims to provide an overview of the foundations of mathematics.",
  "degree": "Bachelor of Arts and Science",
  "faculty": "Faculty of Science",
  "department": "Mathematics and Statistics",
  "blocks": [
    {
      "name": "Required Courses",
      "minimum_credit": 28,
      "block_type": "REQUIRED",
      "details": [],
      "courses":"(('MATH','133') AND ('MATH','140') AND ('MATH','141') AND ('MATH','222') AND ('MATH','235') AND ('MATH','236') AND ('MATH','242') AND ('MATH','243') AND (('MATH','323') OR ('MATH','356')))",
      "blocks": []
    },
    {
      "name": "Complementary Courses",
      "minimum_credit": 18,
      "block_type": "COMPLEMENTARY",
      "details": [
        "9-18 credits selected from Group A.",
        "0-3 credits selected from Group B.",
        "0-9 credits selected from Group C.",
        "Either MATH 249 or MATH 316 may be taken, but not both."
      ],
      "courses": [],
      "blocks": [
        {
          "name": "Group A",
          "minimum_credit": 9,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [
            ["MATH", "249"],
            ["MATH", "314"],
            ["MATH", "315"],
            ["MATH", "316"],
            ["MATH", "317"],
            ["MATH", "318"],
            ["MATH", "324"],
            ["MATH", "340"],
            ["MATH", "346"],
            ["MATH", "378"],
            ["MATH", "417"],
            ["MATH", "451"]
          ],
          "blocks": []
        },
        {
          "name": "Group B",
          "minimum_credit": 0,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [
            ["MATH", "329"],
            ["MATH", "338"]
          ],
          "blocks": []
        },
        {
          "name": "Group C",
          "minimum_credit": 0,
          "block_type": "CUSTOM",
          "details": [],
          "courses": [
            ["MATH", "208"],
            ["MATH", "308"],
            ["MATH", "319"],
            ["MATH", "326"],
            ["MATH", "327"],
            ["MATH", "335"],
            ["MATH", "348"],
            ["MATH", "352"],
            ["MATH", "410"],
            ["MATH", "420"],
            ["MATH", "423"],
            ["MATH", "427"],
            ["MATH", "430"],
            ["MATH", "447"],
            ["MATH", "463"],
            ["MATH", "478"]
          ],
          "blocks": []
        }
      ]
    }
  ]
},
{
  "minimum_credit": 36,
  "block_type": "PROGRAM",
  "name": "Economics Major Concentration (B.A.)",
  "details": [],
  "courses":[],
  "blocks": [
    {
      "name": "Required Courses",
      "minimum_credit": 18,
      "block_type": "REQUIRED",
      "details": [
        "All students must take 6 credits of approved statistics courses.",
        "Students who have completed (MATH 203 and 204) or  (MATH 323 and MATH 324) or (MGCR 271 and MGSC 372), do not have to complete ECON 227D1 and ECON 227D2. They will be exempted. (a) If the students do not count the credits for the above Math, Management or other equivalent statistics courses as part of another program, the six credits for these courses will count towards their program requirements in economics. [That is, they will not have to substitute for them 6 credits in other economics courses]. (b) If the students count the credits for the above Math, Management or other equivalent statistics courses as part of another program, they will need to replace their corresponding number of credits with other economics courses above ECON '210' to fulfill the economics program requirements."
      ],
      "courses" : [('ECON','227D1','3'),('ECON','227D2','3'),('ECON','230D1','3'),('ECON','230D2','3'),('ECON','332','3'),('ECON','333','3')],
      "blocks": []
    },
    {
      "name": "Complementary Courses",
      "minimum_credit": 18,
      "block_type": "COMPLEMENTARY",
      "details": [
        "18 credits in Economics selected from other 200- (with numbers above 209), 300-, 400- and 500-level courses.",
        "At least 6 of these credits must be in 400- or 500-level courses.",
        "No more than 6 credits may be at the 200 level."
      ],
      "courses": [],
      "blocks": []
    }
  ]
}
]

class BlockType(Enum):
    PROGRAM="PROGRAM"
    REQUIRED = "REQUIRED"
    COMPLEMENTARY = "COMPLEMENTARY"
    CUSTOM = "CUSTOM"


class Block(BaseModel):
    """     
    A Block represents a "block of requirements".Each Block can be of only 
    3 types; PROGRAM, REQUIRED, COMPLEMENTARY, CUSTOM. A PROGRAM can contain either 
    REQUIRED or COMPLEMENTARY or both blocks. A COMPLEMENTARY Block further can have one or 
    more CUSTOM blocks.
    """
    name: str
    minimum_credit: int = Field(description="minimum credit requirments for this block. Should be 0 for CUSTOM blocks" )
    block_type: BlockType
    details: List[str]=Field(description="Details includes all rules and restrictions that applies to this block. For CUSTOM blocks details can be left empty. All the details must be in the parent COMPLEMENTARY Block ")
    courses: List[Tuple[str,str,str]] = Field(description="List of courses. A course is a triplet of subject_code,course_code, and credit. Example list: [('COMP','206','3'),('MATH','208','4'),('COMP','361D1','3')]")
    blocks: List["Block"]  
    
    def to_dict(self) -> Dict[str, any]:
        result = {}
        result["name"] = self.name
        result["block_type"] = self.block_type.name

        if self.block_type and self.block_type != BlockType.CUSTOM:
            result["minimum_credit"] = self.minimum_credit
        
        if self.details:
            result["details"] = self.details

        if self.blocks:
            result["blocks"] = [block.to_dict() for block in self.blocks]

        result["courses"] = [str(course) for course in self.courses]
    
        return result


'''
used for testing agent. so that we do not have to use the browser agent again and again
'''
def get_program(program_name: str) -> Optional[Block]:
    for program in PROGRAMS:
        if program.get("name") == program_name:
            program["block_type"] = BlockType(program["block_type"])

            def convert_block(data: dict) -> Block:
                data = data.copy()
                data["block_type"] = BlockType(data["block_type"])
                data["blocks"] = [convert_block(b) for b in data.get("blocks", [])]

                return Block(**data)

            return convert_block(program)

    raise ValueError("Program not found")  



# program = get_program("Computer Science Major Concentration (B.A.)")
# print(program.to_dict())

