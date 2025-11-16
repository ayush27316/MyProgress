# myProgress - Degree Audit System

A degree audit system that analyzes student transcripts against academic programs and generates detailed audit reports showing which requirements are fulfilled and which are still needed. The system uses an AI agent to intelligently match courses to program requirements.

## Overview

**Input**: A transcript (list of programs and courses taken)  
**Output**: Detailed audit reports for each program showing requirement fulfillment status

## Features

- Multi-program audit support
- Intelligent course-to-requirement matching using AI
- Hierarchical requirement block structure (PROGRAM → REQUIRED/COMPLEMENTARY → CUSTOM)
- No course reuse policy enforcement
- Detailed notes on remaining requirements
- RESTful API interface

## Setup

### Prerequisites

- Python 3.8+
- XAI API key (set in `.env` file as `XAI_API_KEY`)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your XAI API key:
```
XAI_API_KEY=your_api_key_here
```

## Running the API Server

### Start the server:
```bash
python api.py
```

Or using uvicorn directly:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## API Endpoints

### `POST /audit`

Generate a degree audit report from a transcript.

#### Request Body

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
    }
  ]
}
```

#### Request Fields

- **program_titles** (array of strings, required): List of program names to audit against. Must match exact program names as they appear in the system.
  - Example: `["Computer Science Major Concentration (B.A.)", "Economics Major Concentration (B.A.)"]`

- **courses** (array of objects, required): List of all courses the student has taken. Each course object contains:
  - **subject_code** (string, required): Department/subject code (e.g., "COMP", "MATH", "ECON", "PHYS")
  - **course_code** (string, required): Course number as a string (must be numeric, e.g., "206", "133", "350")
  - **grade** (string, required): Letter grade received (e.g., "A", "A-", "B+", "B", "B-", "C+", "C", "F")
  - **credit** (integer, required): Number of credits earned. Use `0` for failed courses (grade "F")

#### Response Structure

The response contains a list of program reports, one for each program in the request:

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

#### Response Fields

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
  - Examples: "need 6 credits from MATH 389, MATH 240", "need 3 more credits from Group A"
- **courses** (array of arrays): List of courses fulfilling this block's requirements.
  - Each course is a tuple: `[subject_code, course_code, credit]`
  - Example: `[["MATH", "223", "3"], ["COMP", "206", "3"]]`
  - Note: For PROGRAM blocks, this is typically empty.
- **blocks** (array): Nested sub-blocks (recursive structure)

#### Block Hierarchy

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

#### Important Notes

1. **Course Format**: Courses in the response are tuples `[subject_code, course_code, credit]` where credit is a string representation of the credit value.


#### Error Responses

- **400 Bad Request**: Invalid input (e.g., non-numeric course_code, missing required fields)
  ```json
  {
    "detail": "Invalid course_code 'ABC'. Course codes must be numeric."
  }
  ```

- **500 Internal Server Error**: Server error during report generation
  ```json
  {
    "detail": "Error generating audit report: [error message]"
  }
  ```

#### Processing Time

**Note**: This endpoint may take significant time to process (potentially minutes) as it uses an AI agent to analyze and match courses to requirements. The timeout is set to 3600 seconds (1 hour).

### `GET /`

Health check endpoint.

**Response**:
```json
{
  "message": "Degree Audit API is running"
}
```

### `GET /health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

## Example Usage

### Using curl

```bash
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "program_titles": [
      "Computer Science Major Concentration (B.A.)",
      "Economics Major Concentration (B.A.)"
    ],
    "courses": [
      {"subject_code": "COMP", "course_code": "206", "grade": "B+", "credit": 3},
      {"subject_code": "MATH", "course_code": "133", "grade": "A", "credit": 3},
      {"subject_code": "MATH", "course_code": "140", "grade": "A", "credit": 3},
      {"subject_code": "PHYS", "course_code": "142", "grade": "A", "credit": 4},
      {"subject_code": "COMP", "course_code": "360", "grade": "C+", "credit": 3},
      {"subject_code": "MATH", "course_code": "204", "grade": "B-", "credit": 3},
      {"subject_code": "MATH", "course_code": "243", "grade": "A", "credit": 3},
      {"subject_code": "MATH", "course_code": "315", "grade": "C+", "credit": 3},
      {"subject_code": "MATH", "course_code": "447", "grade": "C", "credit": 3},
      {"subject_code": "COMP", "course_code": "250", "grade": "B-", "credit": 3},
      {"subject_code": "MATH", "course_code": "141", "grade": "A", "credit": 4},
      {"subject_code": "MATH", "course_code": "223", "grade": "A-", "credit": 3},
      {"subject_code": "MATH", "course_code": "240", "grade": "B-", "credit": 3},
      {"subject_code": "COMP", "course_code": "273", "grade": "C", "credit": 3},
      {"subject_code": "COMP", "course_code": "302", "grade": "C+", "credit": 3},
      {"subject_code": "MATH", "course_code": "222", "grade": "C", "credit": 3},
      {"subject_code": "MATH", "course_code": "356", "grade": "C", "credit": 3},
      {"subject_code": "COMP", "course_code": "251", "grade": "C", "credit": 3},
      {"subject_code": "FRSL", "course_code": "105", "grade": "A", "credit": 6},
      {"subject_code": "MATH", "course_code": "242", "grade": "B", "credit": 3},
      {"subject_code": "MATH", "course_code": "323", "grade": "B", "credit": 3},
      {"subject_code": "MATH", "course_code": "324", "grade": "B", "credit": 3},
      {"subject_code": "MATH", "course_code": "314", "grade": "F", "credit": 0},
      {"subject_code": "FRSL", "course_code": "215", "grade": "A", "credit": 6},
      {"subject_code": "FRSL", "course_code": "101", "grade": "A", "credit": 3},
      {"subject_code": "COMP", "course_code": "350", "grade": "B+", "credit": 3},
      {"subject_code": "COMP", "course_code": "409", "grade": "B+", "credit": 3},
      {"subject_code": "COMP", "course_code": "553", "grade": "B+", "credit": 4},
      {"subject_code": "ECON", "course_code": "332", "grade": "B+", "credit": 3},
      {"subject_code": "ECON", "course_code": "333", "grade": "B+", "credit": 3},
      {"subject_code": "ECON", "course_code": "119", "grade": "B+", "credit": 3},
      {"subject_code": "ECON", "course_code": "219", "grade": "B+", "credit": 3},
      {"subject_code": "ECON", "course_code": "221", "grade": "B+", "credit": 3},
      {"subject_code": "ECON", "course_code": "223", "grade": "B+", "credit": 3},
      {"subject_code": "ECON", "course_code": "225", "grade": "B+", "credit": 3},
      {"subject_code": "COMP", "course_code": "421", "grade": "B+", "credit": 3}
    ]
  }'
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/audit"
payload = {
    "program_titles": [
        "Computer Science Major Concentration (B.A.)",
        "Economics Major Concentration (B.A.)"
    ],
    "courses": [
        {"subject_code": "COMP", "course_code": "206", "grade": "B+", "credit": 3},
        {"subject_code": "MATH", "course_code": "223", "grade": "A-", "credit": 3},
        {"subject_code": "ECON", "course_code": "332", "grade": "B+", "credit": 3}
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

### Using the test script

A test script is provided for convenience:

```bash
bash test_curl.sh
```

Or make it executable and run directly:

```bash
chmod +x test_curl.sh
./test_curl.sh
```

## Project Structure

```
myprogress/
├── api.py                 # FastAPI application and endpoints
├── agent_controller.py    # Main controller for orchestrating the audit process
├── agent.py              # AI agent for course-to-requirement matching
├── transcript.py         # Transcript and Course data models
├── report.py             # Report data structures
├── program.py            # Program and Block data models
├── fetcher.py            # Program data fetcher
├── common.py             # Common utilities (logging)
├── requirements.txt      # Python dependencies
├── test_curl.sh          # Test script with example curl command
└── README.md             # This file
```

## Dependencies

See `requirements.txt` for the complete list. Key dependencies include:

- `fastapi`: Web framework for building the API
- `uvicorn`: ASGI server for running FastAPI
- `pydantic`: Data validation using Python type annotations
- `xai-sdk`: XAI SDK for AI agent functionality
- `python-dotenv`: Environment variable management
- `requests`: HTTP library

## Development

### Running Tests

The project includes test scripts in the `test/` directory. You can also use the provided `test_curl.sh` script to test the API endpoint.

### Logging

Logs are written to `app.log` in the project root directory.

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
