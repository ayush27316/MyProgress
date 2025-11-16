import { useState, useEffect } from 'react'
import { ChevronDown, ChevronRight, Edit2, Plus, Trash2, Download, Upload, X } from 'lucide-react'
import './ReportViewer.css'

const VALID_GRADES = ["A", "A-", "B+", "B", "B-", "C+", "C", "F"]

function ReportViewer({ reports: initialReports }) {
  const [reports, setReports] = useState(initialReports)
  const [expandedBlocks, setExpandedBlocks] = useState(new Set())
  const [editingBlock, setEditingBlock] = useState(null)
  const [newBlockPaths, setNewBlockPaths] = useState(new Set())

  // Normalize courses from array format to object format for backward compatibility
  const normalizeCourses = (courses) => {
    if (!courses) return []
    return courses.map(course => {
      if (Array.isArray(course)) {
        // Old format: [subject_code, course_code, credit]
        return {
          subject_code: course[0] || '',
          course_code: course[1] || '',
          grade: 'A',
          credit: course[2] || '0'
        }
      }
      // Already in object format
      return {
        subject_code: course.subject_code || '',
        course_code: course.course_code || '',
        grade: course.grade || 'A',
        credit: course.credit || '0'
      }
    })
  }

  // Normalize reports on mount and when initialReports change
  useEffect(() => {
    const normalizeReports = (reports) => {
      return reports.map(report => {
        const normalizeBlock = (block) => {
          const normalized = {
            ...block,
            courses: normalizeCourses(block.courses)
          }
          if (block.blocks && block.blocks.length > 0) {
            normalized.blocks = block.blocks.map(normalizeBlock)
          }
          return normalized
        }
        return normalizeBlock(report)
      })
    }
    setReports(normalizeReports(initialReports))
  }, [initialReports])

  const toggleBlock = (path) => {
    const newExpanded = new Set(expandedBlocks)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedBlocks(newExpanded)
  }

  const updateReport = (reportIndex, path, updates) => {
    const newReports = [...reports]
    
    if (path.length === 0) {
      newReports[reportIndex] = { ...newReports[reportIndex], ...updates }
    } else {
      const updateNested = (block, pathIndex) => {
        if (pathIndex === path.length) {
          return { ...block, ...updates }
        }
        const blockIndex = path[pathIndex]
        return {
          ...block,
          blocks: block.blocks.map((b, i) => 
            i === blockIndex ? updateNested(b, pathIndex + 1) : b
          )
        }
      }
      newReports[reportIndex] = updateNested(newReports[reportIndex], 0)
    }
    
    setReports(newReports)
  }

  const addNote = (reportIndex, path) => {
    const block = getBlock(reports[reportIndex], path)
    const newNotes = [...(block.notes || []), '']
    updateReport(reportIndex, path, { notes: newNotes })
  }

  const updateNote = (reportIndex, path, noteIndex, value) => {
    const block = getBlock(reports[reportIndex], path)
    const newNotes = [...block.notes]
    newNotes[noteIndex] = value
    updateReport(reportIndex, path, { notes: newNotes })
  }

  const removeNote = (reportIndex, path, noteIndex) => {
    const block = getBlock(reports[reportIndex], path)
    const newNotes = block.notes.filter((_, i) => i !== noteIndex)
    updateReport(reportIndex, path, { notes: newNotes })
  }

  const addCourse = (reportIndex, path) => {
    const block = getBlock(reports[reportIndex], path)
    const newCourses = [...(block.courses || []), {
      subject_code: '',
      course_code: '',
      grade: 'A',
      credit: '0'
    }]
    updateReport(reportIndex, path, { courses: newCourses })
  }

  const updateCourse = (reportIndex, path, courseIndex, field, value) => {
    const block = getBlock(reports[reportIndex], path)
    const newCourses = [...block.courses]
    newCourses[courseIndex] = {
      ...newCourses[courseIndex],
      [field]: value
    }
    // If grade is F, set credit to 0
    if (field === 'grade' && value === 'F') {
      newCourses[courseIndex].credit = '0'
    }
    updateReport(reportIndex, path, { courses: newCourses })
  }

  const removeCourse = (reportIndex, path, courseIndex) => {
    const block = getBlock(reports[reportIndex], path)
    const newCourses = block.courses.filter((_, i) => i !== courseIndex)
    updateReport(reportIndex, path, { courses: newCourses })
  }

  const addBlock = (reportIndex, path) => {
    const block = getBlock(reports[reportIndex], path)
    const newBlock = {
      name: 'New Block',
      minimum_credit: null,
      received_credit: null,
      block_type: 'CUSTOM',
      status: 'UNFULFILLED',
      notes: [],
      courses: [],
      blocks: []
    }
    const newBlocks = [...(block.blocks || []), newBlock]
    const newBlockIndex = newBlocks.length - 1
    const newBlockPath = [...path, newBlockIndex].join('-')
    setNewBlockPaths(new Set([...newBlockPaths, newBlockPath]))
    updateReport(reportIndex, path, { blocks: newBlocks })
  }

  const removeBlock = (reportIndex, path, blockIndex) => {
    const block = getBlock(reports[reportIndex], path)
    const newBlocks = block.blocks.filter((_, i) => i !== blockIndex)
    updateReport(reportIndex, path, { blocks: newBlocks })
  }

  const getBlock = (block, path) => {
    if (path.length === 0) return block
    if (!block.blocks || path[0] >= block.blocks.length) return block
    return getBlock(block.blocks[path[0]], path.slice(1))
  }

  const exportReport = () => {
    const dataStr = JSON.stringify(reports, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'audit-report.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  const importReport = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const imported = JSON.parse(e.target.result)
          // Normalize imported reports
          const normalizeReports = (reports) => {
            return reports.map(report => {
              const normalizeBlock = (block) => {
                const normalized = {
                  ...block,
                  courses: normalizeCourses(block.courses)
                }
                if (block.blocks && block.blocks.length > 0) {
                  normalized.blocks = block.blocks.map(normalizeBlock)
                }
                return normalized
              }
              return normalizeBlock(report)
            })
          }
          setReports(normalizeReports(imported))
        } catch (err) {
          alert('Invalid JSON file')
        }
      }
      reader.readAsText(file)
    }
  }

  const BlockComponent = ({ block, reportIndex, path, level = 0 }) => {
    const blockPath = path.join('-')
    const isExpanded = expandedBlocks.has(blockPath)
    const isEditing = editingBlock === blockPath
    const hasNestedBlocks = block.blocks && block.blocks.length > 0
    const isNewBlock = newBlockPaths.has(blockPath)
    const isCustomBlock = block.block_type === 'CUSTOM'
    const showCredits = !isCustomBlock && block.minimum_credit !== null

    return (
      <div className={`block block-level-${level} block-type-${block.block_type?.toLowerCase()}`}>
        <div className="block-header-compact">
          <div className="block-header-left">
            {hasNestedBlocks && (
              <button
                className="btn-icon btn-icon-small"
                onClick={() => toggleBlock(blockPath)}
                title={isExpanded ? "Collapse" : "Expand"}
              >
                {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </button>
            )}
            <div className="block-title-section">
              {isEditing ? (
                <input
                  type="text"
                  value={block.name}
                  onChange={(e) => updateReport(reportIndex, path, { name: e.target.value })}
                  className="block-name-input"
                  onBlur={() => {
                    setEditingBlock(null)
                    // Remove from new blocks once edited
                    if (isNewBlock) {
                      const newPaths = new Set(newBlockPaths)
                      newPaths.delete(blockPath)
                      setNewBlockPaths(newPaths)
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      setEditingBlock(null)
                      // Remove from new blocks once edited
                      if (isNewBlock) {
                        const newPaths = new Set(newBlockPaths)
                        newPaths.delete(blockPath)
                        setNewBlockPaths(newPaths)
                      }
                    }
                  }}
                  autoFocus
                />
              ) : (
                <h4 
                  className="block-name"
                  onClick={() => setEditingBlock(blockPath)}
                  title="Click to edit"
                >
                  {block.name}
                </h4>
              )}
            </div>
          </div>
          <div className="block-header-right">
            {showCredits && (
              <div className="block-credits-compact">
                <span className="credit-received">{block.received_credit ?? 0}</span>
                <span className="credit-separator">/</span>
                <span className="credit-minimum">{block.minimum_credit}</span>
              </div>
            )}
            <span className={`status-badge status-${block.status?.toLowerCase()}`}>
              {block.status}
            </span>
          </div>
        </div>

        <div className="block-content-compact">
          <div className="block-fields-grid">
            <div className="field-group">
              <label>Status</label>
              <select
                value={block.status}
                onChange={(e) => updateReport(reportIndex, path, { status: e.target.value })}
                className="input-compact"
              >
                <option value="FULFILLED">FULFILLED</option>
                <option value="UNFULFILLED">UNFULFILLED</option>
              </select>
            </div>

            {!isCustomBlock && (
              <>
                <div className="field-group">
                  <label>Min Credit</label>
                  <input
                    type="number"
                    value={block.minimum_credit ?? ''}
                    onChange={(e) => updateReport(reportIndex, path, { 
                      minimum_credit: e.target.value === '' ? null : parseInt(e.target.value) 
                    })}
                    placeholder="—"
                    className="input-compact"
                  />
                </div>

                <div className="field-group">
                  <label>Received Credit</label>
                  <input
                    type="number"
                    value={block.received_credit ?? ''}
                    onChange={(e) => updateReport(reportIndex, path, { 
                      received_credit: e.target.value === '' ? null : parseInt(e.target.value) 
                    })}
                    placeholder="—"
                    className="input-compact"
                  />
                </div>
              </>
            )}

          </div>

          <div className="block-section-compact">
            <div className="section-header-compact">
              <label>Notes</label>
              <button className="btn-icon btn-icon-small" onClick={() => addNote(reportIndex, path)} title="Add note">
                <Plus size={14} />
              </button>
            </div>
            <div className="notes-list-compact">
              {block.notes && block.notes.length > 0 ? (
                block.notes.map((note, noteIndex) => (
                  <div key={noteIndex} className="note-item-compact">
                    <input
                      type="text"
                      value={note}
                      onChange={(e) => updateNote(reportIndex, path, noteIndex, e.target.value)}
                      className="input-compact"
                      placeholder="Add a note..."
                    />
                    <button
                      className="btn-icon btn-icon-small btn-danger"
                      onClick={() => removeNote(reportIndex, path, noteIndex)}
                      title="Remove note"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))
              ) : (
                <div className="empty-state">No notes</div>
              )}
            </div>
          </div>

          <div className="block-section-compact">
            <div className="section-header-compact">
              <label>Courses</label>
              <button className="btn-icon btn-icon-small" onClick={() => addCourse(reportIndex, path)} title="Add course">
                <Plus size={14} />
              </button>
            </div>
            <div className="courses-list-compact">
              {block.courses && block.courses.length > 0 ? (
                block.courses.map((course, courseIndex) => {
                  // Normalize course to object format if it's still an array
                  const courseObj = Array.isArray(course) 
                    ? {
                        subject_code: course[0] || '',
                        course_code: course[1] || '',
                        grade: 'A',
                        credit: course[2] || '0'
                      }
                    : {
                        subject_code: course.subject_code || '',
                        course_code: course.course_code || '',
                        grade: course.grade || 'A',
                        credit: course.credit || '0'
                      }

                  return (
                    <div key={courseIndex} className="course-item-block">
                      <div className="course-fields-grid">
                        <div className="course-field-group">
                          <label>Subject Code</label>
                          <input
                            type="text"
                            value={courseObj.subject_code}
                            onChange={(e) => updateCourse(reportIndex, path, courseIndex, 'subject_code', e.target.value.toUpperCase())}
                            placeholder="COMP"
                            className="input-compact input-course-field"
                            maxLength={4}
                          />
                        </div>
                        <div className="course-field-group">
                          <label>Course Code</label>
                          <input
                            type="text"
                            value={courseObj.course_code}
                            onChange={(e) => updateCourse(reportIndex, path, courseIndex, 'course_code', e.target.value)}
                            placeholder="206"
                            className="input-compact input-course-field"
                          />
                        </div>
                        <div className="course-field-group">
                          <label>Grade</label>
                          <select
                            value={courseObj.grade}
                            onChange={(e) => updateCourse(reportIndex, path, courseIndex, 'grade', e.target.value)}
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
                            value={courseObj.credit}
                            onChange={(e) => updateCourse(reportIndex, path, courseIndex, 'credit', e.target.value)}
                            placeholder="3"
                            className="input-compact input-course-field"
                            disabled={courseObj.grade === 'F'}
                          />
                        </div>
                      </div>
                      <button
                        className="btn-icon btn-icon-small btn-danger btn-remove-course"
                        onClick={() => removeCourse(reportIndex, path, courseIndex)}
                        title="Remove course"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  )
                })
              ) : (
                <div className="empty-state">No courses</div>
              )}
            </div>
          </div>

          {isExpanded && hasNestedBlocks && (
            <div className="block-section-compact">
              <div className="section-header-compact">
                <label>Nested Blocks</label>
                <button className="btn-icon btn-icon-small" onClick={() => addBlock(reportIndex, path)} title="Add block">
                  <Plus size={14} />
                </button>
              </div>
              <div className="nested-blocks-compact">
                {block.blocks.map((nestedBlock, blockIndex) => (
                  <div key={blockIndex} className="nested-block-wrapper">
                    <BlockComponent
                      block={nestedBlock}
                      reportIndex={reportIndex}
                      path={[...path, blockIndex]}
                      level={level + 1}
                    />
                    <button
                      className="btn-icon btn-icon-small btn-danger btn-remove-block"
                      onClick={() => removeBlock(reportIndex, path, blockIndex)}
                      title="Remove block"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="report-viewer">
      <div className="viewer-header-compact">
        <h2>Audit Report</h2>
        <div className="viewer-actions">
          <label className="btn-icon" title="Import JSON">
            <Upload size={18} />
            <input
              type="file"
              accept=".json"
              onChange={importReport}
              style={{ display: 'none' }}
            />
          </label>
          <button className="btn-icon" onClick={exportReport} title="Export JSON">
            <Download size={18} />
          </button>
        </div>
      </div>

      <div className="reports-list-compact">
        {reports.map((report, reportIndex) => (
          <div key={reportIndex} className="report-item-compact">
            <BlockComponent
              block={report}
              reportIndex={reportIndex}
              path={[]}
              level={0}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

export default ReportViewer
