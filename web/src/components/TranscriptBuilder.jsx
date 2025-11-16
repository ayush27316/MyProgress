import { useState } from 'react'
import { Plus, Trash2, FileText, Send, ChevronDown } from 'lucide-react'
import './TranscriptBuilder.css'

const TEST_TRANSCRIPT = {
  program_titles: [
    "Computer Science Major Concentration (B.A.)",
    "Economics Major Concentration (B.A.)"
  ],
  courses: [
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
}

const VALID_GRADES = ["A", "A-", "B+", "B", "B-", "C+", "C", "F"]

function TranscriptBuilder({ onAudit, loading, onCollapse }) {
  const [programTitles, setProgramTitles] = useState([""])
  const [courses, setCourses] = useState([])

  const loadTestTranscript = () => {
    setProgramTitles([...TEST_TRANSCRIPT.program_titles])
    setCourses([...TEST_TRANSCRIPT.courses])
  }

  const addProgram = () => {
    setProgramTitles([...programTitles, ""])
  }

  const updateProgram = (index, value) => {
    const newPrograms = [...programTitles]
    newPrograms[index] = value
    setProgramTitles(newPrograms)
  }

  const removeProgram = (index) => {
    if (programTitles.length > 1) {
      setProgramTitles(programTitles.filter((_, i) => i !== index))
    }
  }

  const addCourse = () => {
    setCourses([...courses, { subject_code: "", course_code: "", grade: "A", credit: 3 }])
  }

  const updateCourse = (index, field, value) => {
    const newCourses = [...courses]
    if (field === 'credit') {
      newCourses[index][field] = parseInt(value) || 0
    } else {
      newCourses[index][field] = value
    }
    if (field === 'grade' && value === 'F') {
      newCourses[index].credit = 0
    }
    setCourses(newCourses)
  }

  const removeCourse = (index) => {
    setCourses(courses.filter((_, i) => i !== index))
  }

  const handleSubmit = () => {
    const filteredPrograms = programTitles.filter(p => p.trim() !== "")
    if (filteredPrograms.length === 0) {
      alert("Please add at least one program title")
      return
    }
    if (courses.length === 0) {
      alert("Please add at least one course")
      return
    }

    const transcriptData = {
      program_titles: filteredPrograms,
      courses: courses
    }

    onAudit(transcriptData)
  }

  return (
    <div className="transcript-builder">
      <div className="builder-header">
        <h2>Transcript Builder</h2>
        <div className="builder-header-actions">
          <button 
            className="btn-icon" 
            onClick={loadTestTranscript}
            disabled={loading}
            title="Load test transcript"
          >
            <FileText size={18} />
          </button>
          {onCollapse && (
            <button 
              className="btn-icon" 
              onClick={onCollapse}
              disabled={loading}
              title="Collapse transcript builder"
            >
              <ChevronDown size={18} />
            </button>
          )}
        </div>
      </div>

      <div className="builder-section compact">
        <div className="section-header-compact">
          <span className="section-label">Programs</span>
          <button className="btn-icon btn-icon-small" onClick={addProgram} disabled={loading} title="Add program">
            <Plus size={16} />
          </button>
        </div>
        <div className="programs-list-compact">
          {programTitles.map((program, index) => (
            <div key={index} className="program-item-compact">
              <input
                type="text"
                value={program}
                onChange={(e) => updateProgram(index, e.target.value)}
                placeholder="Program title..."
                disabled={loading}
                className="input-compact"
              />
              {programTitles.length > 1 && (
                <button
                  className="btn-icon btn-icon-small btn-danger"
                  onClick={() => removeProgram(index)}
                  disabled={loading}
                  title="Remove program"
                >
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="builder-section compact">
        <div className="section-header-compact">
          <span className="section-label">Courses</span>
          <button className="btn-icon btn-icon-small" onClick={addCourse} disabled={loading} title="Add course">
            <Plus size={16} />
          </button>
        </div>
        <div className="courses-list-compact">
          {courses.map((course, index) => {
            return (
              <div key={index} className="course-item-block">
                <div className="course-fields-grid">
                  <div className="course-field-group">
                    <label>Subject Code</label>
                    <input
                      type="text"
                      value={course.subject_code || ''}
                      onChange={(e) => updateCourse(index, 'subject_code', e.target.value.toUpperCase())}
                      placeholder="COMP"
                      disabled={loading}
                      className="input-compact input-course-field"
                      maxLength={4}
                    />
                  </div>
                  <div className="course-field-group">
                    <label>Course Code</label>
                    <input
                      type="text"
                      value={course.course_code || ''}
                      onChange={(e) => updateCourse(index, 'course_code', e.target.value)}
                      placeholder="206"
                      disabled={loading}
                      className="input-compact input-course-field"
                    />
                  </div>
                  <div className="course-field-group">
                    <label>Grade</label>
                    <select
                      value={course.grade || 'A'}
                      onChange={(e) => updateCourse(index, 'grade', e.target.value)}
                      disabled={loading}
                      className="input-compact input-course-field"
                    >
                      {VALID_GRADES.map(grade => (
                        <option key={grade} value={grade}>{grade}</option>
                      ))}
                    </select>
                  </div>
                  <div className="course-field-group">
                    <label>Credit</label>
                    <input
                      type="text"
                      value={course.credit || ''}
                      onChange={(e) => updateCourse(index, 'credit', parseInt(e.target.value) || 0)}
                      placeholder="3"
                      disabled={loading || course.grade === 'F'}
                      className="input-compact input-course-field"
                    />
                  </div>
                </div>
                <button
                  className="btn-icon btn-icon-small btn-danger btn-remove-course"
                  onClick={() => removeCourse(index)}
                  disabled={loading}
                  title="Remove course"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )
          })}
        </div>
      </div>

      <div className="builder-actions">
        <button
          className="btn-primary"
          onClick={handleSubmit}
          disabled={loading || programTitles.filter(p => p.trim()).length === 0 || courses.length === 0}
        >
          <Send size={18} />
          Generate Audit
        </button>
      </div>
    </div>
  )
}

export default TranscriptBuilder
