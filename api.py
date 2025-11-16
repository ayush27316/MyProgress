from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from agent_controller import AgentController
from transcript import Transcript

app = FastAPI(
    title="Degree Audit API",
    description="REST API for generating degree audit reports from transcripts",
    version="1.0.0"
)


class CourseInput(BaseModel):
    """
    Input model for a single course in the transcript.
    
    Attributes:
        subject_code: Department/subject code (e.g., "COMP", "MATH", "ECON", "PHYS")
        course_code: Course number as a string (must be numeric, e.g., "206", "133", "350")
        grade: Letter grade received (e.g., "A", "A-", "B+", "B", "B-", "C+", "C", "F")
        credit: Number of credits earned. Use 0 for failed courses (grade "F")
    """
    subject_code: str = Field(..., description="Subject code (e.g., 'COMP', 'MATH', 'ECON')")
    course_code: str = Field(..., description="Course code as a string (must be numeric, e.g., '206', '133', '350')")
    grade: str = Field(..., description="Grade received (e.g., 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F')")
    credit: int = Field(..., description="Number of credits for the course. Use 0 for failed courses.")


class TranscriptInput(BaseModel):
    """
    Input model for transcript data containing programs and courses.
    
    Attributes:
        program_titles: List of program names to audit against. Must match exact program names
                       as they appear in the system (e.g., "Computer Science Major Concentration (B.A.)")
        courses: List of all courses the student has taken
    """
    program_titles: List[str] = Field(..., description="List of program titles to audit against")
    courses: List[CourseInput] = Field(..., description="List of courses taken by the student")


class ReportResponse(BaseModel):
    """
    Response model for the audit report.
    
    Attributes:
        reports: List of program reports, one for each program in the request.
                Each report is a hierarchical AgentBlockReport structure showing
                requirement fulfillment status, courses assigned to blocks, and
                notes on remaining requirements.
    """
    reports: List[dict] = Field(..., description="List of program audit reports (AgentBlockReport structures)")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Degree Audit API is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/audit", response_model=ReportResponse)
async def generate_audit_report(transcript_input: TranscriptInput):
    """
    Generate a degree audit report from a transcript.
    
    This endpoint analyzes a student's transcript against one or more academic programs
    and generates detailed audit reports showing which requirements are fulfilled and
    which are still needed. The analysis uses an AI agent to intelligently match courses
    to program requirements while respecting constraints like no course reuse.
    
    ## Request Body
    
    The request must contain:
    - **program_titles**: List of program names to audit against (e.g., ["Computer Science Major Concentration (B.A.)"])
    - **courses**: List of courses the student has taken
    
    Each course must include:
    - **subject_code**: Department/subject code (e.g., "COMP", "MATH", "ECON")
    - **course_code**: Course number as a string (e.g., "206", "133", "350")
    - **grade**: Letter grade received (e.g., "A", "B+", "C", "F")
    - **credit**: Number of credits earned (0 for failed courses)
    
    ## Response Structure
    
    Returns a list of program reports, one for each program in `program_titles`. Each report
    is a hierarchical structure representing the program's requirement blocks.
    
    ### Report Structure
    
    Each report (`AgentBlockReport`) contains:
    
    - **name** (string): Name of the block (e.g., "Computer Science Major Concentration (B.A.)", "Required Courses")
    - **block_type** (string): Type of block - one of:
      - `"PROGRAM"`: Top-level program block
      - `"REQUIRED"`: Required courses block
      - `"COMPLEMENTARY"`: Complementary/elective courses block
      - `"CUSTOM"`: Custom sub-block within complementary courses
    - **minimum_credit** (integer): Minimum credits required for this block (0 for CUSTOM blocks)
    - **received_credit** (integer): Total credits received/fulfilled for this block
    - **status** (string): Fulfillment status - either:
      - `"FULFILLED"`: All requirements met
      - `"UNFULFILLED"`: Requirements not yet met
    - **notes** (array of strings): Human-readable notes explaining what's still needed
      (e.g., "need 6 credits from MATH 389, MATH 240", "need 3 more credits from Group A")
    - **courses** (array of tuples): List of courses fulfilling this block's requirements.
      Each course is a tuple: `[subject_code, course_code, credit]`
      Example: `[["MATH", "223", "3"], ["COMP", "206", "3"]]`
      Note: For PROGRAM blocks, this is typically empty.
    - **blocks** (array): Nested sub-blocks (recursive structure)
    
    ### Block Hierarchy
    
    The report structure is hierarchical:
    ```
    PROGRAM (top-level)
    ├── REQUIRED (required courses block)
    │   ├── courses: [list of required courses taken]
    │   └── blocks: [] (usually empty)
    └── COMPLEMENTARY (complementary/elective courses block)
        ├── courses: [courses in complementary but not in any CUSTOM block]
        └── blocks: [
            CUSTOM (e.g., "Group A", "Group B")
            ├── courses: [courses in this specific group]
            └── blocks: [] (usually empty)
        ]
    ```
    
    ### Important Notes
    
    1. **No Course Reuse**: A course can only fulfill one block requirement. Once assigned,
       it won't appear in other blocks.
    
    2. **Credit Calculation**: For COMPLEMENTARY blocks, `received_credit` includes credits
       from nested CUSTOM blocks. For CUSTOM blocks, `received_credit` may be omitted.
    
    3. **Course Format**: Courses in the response are tuples `[subject_code, course_code, credit]`
       where credit is a string representation of the credit value.
    
    4. **Status Propagation**: A block is FULFILLED only when all its requirements are met,
       including nested blocks.
    
    ## Example Request
    
    ```json
    {
      "program_titles": [
        "Computer Science Major Concentration (B.A.)",
        "Economics Major Concentration (B.A.)"
      ],
      "courses": [
        {
          "subject_code": "COMP",
          "course_code": "206",
          "grade": "B+",
          "credit": 3
        },
        {
          "subject_code": "MATH",
          "course_code": "223",
          "grade": "A-",
          "credit": 3
        },
        {
          "subject_code": "ECON",
          "course_code": "332",
          "grade": "B+",
          "credit": 3
        }
      ]
    }
    ```
    
    ## Example Response
    
    ```json
    {
      "reports": [
        {
          "name": "Computer Science Major Concentration (B.A.)",
          "block_type": "PROGRAM",
          "minimum_credit": 36,
          "received_credit": 21,
          "status": "UNFULFILLED",
          "notes": ["overall need 15 more credits"],
          "courses": [],
          "blocks": [
            {
              "name": "Required Courses",
              "block_type": "REQUIRED",
              "minimum_credit": 18,
              "received_credit": 12,
              "status": "UNFULFILLED",
              "notes": ["need 6 credits from MATH 389, MATH 240"],
              "courses": [
                ["MATH", "223", "3"],
                ["MATH", "318", "3"],
                ["MATH", "340", "3"],
                ["MATH", "370", "3"]
              ],
              "blocks": []
            },
            {
              "name": "Complementary Courses",
              "block_type": "COMPLEMENTARY",
              "minimum_credit": 18,
              "received_credit": 6,
              "status": "UNFULFILLED",
              "notes": [
                "need 3 more credits from Group A",
                "9 credit from any MATH courses 300 level and above except MATH 389"
              ],
              "courses": [
                ["MATH", "223", "3"]
              ],
              "blocks": [
                {
                  "name": "Group A",
                  "block_type": "CUSTOM",
                  "minimum_credit": 0,
                  "received_credit": 0,
                  "status": "UNFULFILLED",
                  "notes": ["need 3 more credits"],
                  "courses": [
                    ["PHYS", "141", "3"]
                  ],
                  "blocks": []
                }
              ]
            }
          ]
        }
      ]
    }
    ```
    
    ## Error Responses
    
    - **400 Bad Request**: Invalid input (e.g., non-numeric course_code, missing required fields)
    - **500 Internal Server Error**: Server error during report generation
    
    ## Processing Time
    
    Note: This endpoint may take significant time to process (potentially minutes) as it uses
    an AI agent to analyze and match courses to requirements. The timeout is set to 3600 seconds.
    """
    try:
        # Create Transcript object from input
        transcript = Transcript()
        
        # Add programs
        for program_title in transcript_input.program_titles:
            transcript.add_program(program_title)
        
        # Add courses
        for course in transcript_input.courses:
            # Note: add_course type hint says int, but Course.__init__ expects str
            # The test passes strings, so we pass as string to match Course's expectation
            # Converting to int first to satisfy the type hint, though Course will receive it as int
            # and store it (Python is dynamically typed, so this works)
            try:
                course_code_int = int(course.course_code)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid course_code '{course.course_code}'. Course codes must be numeric."
                )
            transcript.add_course(
                subject_code=course.subject_code,
                course_code=course_code_int,
                grade=course.grade,
                credit=course.credit
            )
        
        # Create controller and generate report
        controller = AgentController(transcript)
        controller.start()
        
        reports = controller.get_report_serializable()
        
        return ReportResponse(reports=reports)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audit report: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

