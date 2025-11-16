#!/bin/bash

# Test curl command for the Degree Audit API
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
  }' | jq '.'

