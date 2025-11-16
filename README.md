# myProgress-ultra-pro-max

myProgress is an AI degree audit tool. 

## API Documentation

### POST `/audit`

Generates a comprehensive degree audit report by analyzing a student's transcript against specified program requirements. The endpoint uses AI to intelligently match courses to program blocks, determine fulfillment status, and provide detailed notes on remaining requirements.

#### Endpoint Details

- **URL**: `/audit`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Response Format**: JSON

#### Request Body

The request body must be a JSON object with the following structure:

```json
{
  "program_titles": ["string"],
  "courses": [
    {
      "subject_code": "string",
      "course_code": "string",
      "grade": "string",
      "credit": integer
    }
  ]
}
```

##### Request Fields

**`program_titles`** (required, array of strings)
- List of program names to audit against
- Must match exact program names as they appear in the system
- Examples:
  - `"Computer Science Major Concentration (B.A.)"`
  - `"Economics Major Concentration (B.A.)"`
  - `"Mathematics Major Concentration (B.A.)"`
- Multiple programs can be audited in a single request
- Each program will generate a separate report in the response

**`courses`** (required, array of objects)
- List of all courses the student has taken
- Each course object contains:

  **`subject_code`** (required, string)
  - Department or subject code (e.g., `"COMP"`, `"MATH"`, `"ECON"`, `"PHYS"`, `"FRSL"`)
  - Typically 3-4 uppercase letters representing the department

  **`course_code`** (required, string)
  - Course number as a string (must be numeric)
  - Examples: `"206"`, `"133"`, `"350"`, `"227D1"`
  - Can include suffixes like `"D1"` or `"D2"` for multi-part courses
  - Must be convertible to an integer (validation error if not numeric)

  **`grade`** (required, string)
  - Letter grade received
  - Valid grades: `"A"`, `"A-"`, `"B+"`, `"B"`, `"B-"`, `"C+"`, `"C"`, `"F"`
  - Failed courses (grade `"F"`) should have `credit` set to `0`

  **`credit`** (required, integer)
  - Number of credits earned for the course
  - Must be `0` for failed courses (grade `"F"`)
  - Typically ranges from 1-6 credits per course
  - Common values: `3`, `4`, `6`

#### Response Body

The response is a JSON object containing an array of program reports:

```json
{
  "reports": [
    {
      "name": "string",
      "minimum_credit": integer | null,
      "received_credit": integer | null,
      "block_type": "PROGRAM" | "REQUIRED" | "COMPLEMENTARY" | "CUSTOM",
      "status": "FULFILLED" | "UNFULFILLED",
      "notes": ["string"],
      "courses": [["string", "string", "string"]],
      "blocks": [/* nested AgentBlockReport objects */]
    }
  ]
}
```

##### Response Fields

**`reports`** (array of objects)
- One report per program specified in `program_titles`
- Each report is a hierarchical `AgentBlockReport` structure
- Reports are ordered to match the order of `program_titles` in the request

**Report Object Structure:**

Each report object represents a block of requirements and contains:

**`name`** (string)
- Name of the block
- Examples:
  - Program level: `"Computer Science Major Concentration (B.A.)"`
  - Required block: `"Required Courses"`
  - Complementary block: `"Complementary Courses"`
  - Custom block: `"Group A"`, `"Group B"`, etc.

**`minimum_credit`** (integer | null)
- Minimum credit requirements for this block
- `null` for `CUSTOM` blocks (credit requirements are specified in parent blocks)
- Always present for `PROGRAM`, `REQUIRED`, and `COMPLEMENTARY` blocks

**`received_credit`** (integer | null)
- Total credits received/fulfilled for this block
- For `COMPLEMENTARY` blocks, includes credits from nested `CUSTOM` blocks
- `null` for `CUSTOM` blocks (credits are counted at parent level)
- Can be less than, equal to, or greater than `minimum_credit`

**`block_type`** (string, enum)
- Type of requirement block
- Possible values:
  - `"PROGRAM"`: Top-level program block (contains other blocks)
  - `"REQUIRED"`: Required courses block
  - `"COMPLEMENTARY"`: Complementary/elective courses block
  - `"CUSTOM"`: Custom sub-block within complementary courses (e.g., "Group A", "Group B")

**`status`** (string, enum)
- Fulfillment status of the block
- Possible values:
  - `"FULFILLED"`: All requirements for this block are met
  - `"UNFULFILLED"`: Some requirements are still missing

**`notes`** (array of strings)
- Human-readable notes describing remaining requirements
- Empty array `[]` if block is `FULFILLED`
- Contains specific guidance when `UNFULFILLED`
- Examples:
  - `"need 6 credits from MATH 389, MATH 240"`
  - `"need 3 more credits from Group A"`
  - `"need 9 credits from any MATH courses 300 level and above except MATH 389"`
  - `"Need (COMP 230 or COMP 350) and MATH 360"`
- Notes avoid repetition across nested blocks

**`courses`** (array of tuples)
- List of courses fulfilling this block's requirements
- Each course is represented as `[subject_code, course_code, credit]`
- Example: `[["MATH", "223", "3"], ["COMP", "206", "4"]]`
- Empty array `[]` for `PROGRAM` blocks (courses are assigned to nested blocks)
- Courses are never reused across blocks (each course appears only once)

**`blocks`** (array of objects, optional)
- Nested blocks (recursive structure)
- Only `PROGRAM` and `COMPLEMENTARY` blocks contain nested blocks
- `REQUIRED` and `CUSTOM` blocks have empty `blocks` arrays
- Each nested block follows the same structure as the parent

#### Block Hierarchy

The report structure follows a hierarchical model:

```
PROGRAM (top-level)
├── REQUIRED (required courses block)
│   └── courses: [list of required courses]
└── COMPLEMENTARY (complementary courses block)
    ├── courses: [courses not assigned to specific groups]
    └── CUSTOM (sub-groups like "Group A", "Group B")
        └── courses: [courses specific to this group]
```

**Important Notes:**
- A course can only fulfill one block (no course reuse)
- Courses are first assigned to `REQUIRED` blocks, then to `COMPLEMENTARY` blocks
- Within `COMPLEMENTARY` blocks, courses are assigned to specific `CUSTOM` blocks when applicable
- `COMPLEMENTARY` block's `received_credit` includes credits from all nested `CUSTOM` blocks

#### Example Request

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
      {"subject_code": "ECON", "course_code": "332", "grade": "B+", "credit": 3},
      {"subject_code": "ECON", "course_code": "333", "grade": "B+", "credit": 3},
      {"subject_code": "MATH", "course_code": "314", "grade": "F", "credit": 0}
    ]
  }'
```

#### Example Response

```json
{
  "reports": [
    {
      "name": "Computer Science Major Concentration (B.A.)",
      "minimum_credit": 54,
      "received_credit": 42,
      "block_type": "PROGRAM",
      "status": "UNFULFILLED",
      "notes": ["overall need 12 more credits"],
      "courses": [],
      "blocks": [
        {
          "name": "Required Courses",
          "minimum_credit": 36,
          "received_credit": 30,
          "block_type": "REQUIRED",
          "status": "UNFULFILLED",
          "notes": ["need 6 credits from COMP 250, COMP 251"],
          "courses": [
            ["COMP", "206", "3"],
            ["COMP", "360", "3"],
            ["MATH", "133", "3"],
            ["MATH", "140", "3"],
            ["MATH", "204", "3"]
          ],
          "blocks": []
        },
        {
          "name": "Complementary Courses",
          "minimum_credit": 18,
          "received_credit": 12,
          "block_type": "COMPLEMENTARY",
          "status": "UNFULFILLED",
          "notes": ["need 6 more credits from Group A"],
          "courses": [
            ["PHYS", "142", "4"]
          ],
          "blocks": [
            {
              "name": "Group A",
              "minimum_credit": null,
              "received_credit": null,
              "block_type": "CUSTOM",
              "status": "UNFULFILLED",
              "notes": ["need 6 more credits"],
              "courses": [],
              "blocks": []
            }
          ]
        }
      ]
    },
    {
      "name": "Economics Major Concentration (B.A.)",
      "minimum_credit": 36,
      "received_credit": 6,
      "block_type": "PROGRAM",
      "status": "UNFULFILLED",
      "notes": ["overall need 30 more credits"],
      "courses": [],
      "blocks": [
        {
          "name": "Required Courses",
          "minimum_credit": 18,
          "received_credit": 0,
          "block_type": "REQUIRED",
          "status": "UNFULFILLED",
          "notes": ["need all 18 credits from required courses"],
          "courses": [],
          "blocks": []
        },
        {
          "name": "Complementary Courses",
          "minimum_credit": 18,
          "received_credit": 6,
          "block_type": "COMPLEMENTARY",
          "status": "UNFULFILLED",
          "notes": ["need 12 more credits from 200-500 level ECON courses"],
          "courses": [
            ["ECON", "332", "3"],
            ["ECON", "333", "3"]
          ],
          "blocks": []
        }
      ]
    }
  ]
}
```

#### Error Responses

**400 Bad Request**
- Invalid request format or validation errors
- Example: Non-numeric `course_code`
```json
{
  "detail": "Invalid course_code 'ABC'. Course codes must be numeric."
}
```

**500 Internal Server Error**
- Server-side errors during report generation
- Example: Program not found, AI processing failure
```json
{
  "detail": "Error generating audit report: [error message]"
}
```

