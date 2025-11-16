from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from agent_controller import AgentController
from transcript import Transcript
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="Degree Audit API",
    description="REST API for generating degree audit reports from transcripts",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # or ["http://localhost:3000"] for specific origins
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # Authorization, Content-Type, etc.
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


