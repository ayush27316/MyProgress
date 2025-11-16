from typing import List, Iterator, Optional, Literal, Dict, Tuple

class Course:
    title:str
    subject_code: str 
    course_code: str 
    credit: int
    grade: str
    done: bool
    associated_with_program: bool
    associated_program_title: str 
    associated_program_block_name: str 
    notes: List[str]
    
    def __init__(self,subject_code:str,course_code:str, credit:int = None, grade:str=None):
        self.subject_code = subject_code
        self.course_code = course_code    
        self.grade = grade
        self.associated_with_program = False
        self.associated_program_title = "" 
        self.associated_program_block_name = "" 
        self.notes = [] 
        self.title = ""
        self.credit = credit
        self.done = False
                   
    def is_usable(self):
        return self.credit != 0

    def add_note(self,note:str):
        self.notes.append(note)
    
    def change_note(self,note:str):
        self.notes=[]
        self.notes.append(note)

    def is_done(self):
        return self.done

    def mark_as_done(self):
        return self.done

    def not_associated(self)->bool:
        return self.associated_with_program==False

    def associate_with_program(self,program_title:str,block_name:str):
        self.mark_as_done()
        self.associated_with_program = True
        self.associated_program_title = program_title
        self.associated_program_block_name = block_name

    def to_dict(self) -> dict:
        return {
            "subject_code": self.subject_code,
            "course_code": self.course_code,
            "credit": self.credit,
            "grade": self.grade, 
            "done": self.done
        }

    def to_dict_full(self) -> Dict[str, any]:
        result = {
            "title": self.title,
            "subject_code": self.subject_code,
            "course_code": self.course_code,
            "credit": self.credit,
            "grade": self.grade,
            "done": self.done,
            "associated_with_program": self.associated_with_program,
        }
        # Only include these if associated_with_program is True
        if self.associated_with_program:
            result["associated_program_title"] = self.associated_program_title
            result["associated_program_block_name"] = self.associated_program_block_name

        return result

    

class Transcript:
    courses: List[Course]
    program_titles : List[str]

    def __init__(self):
        self.courses = []
        self.program_titles = []
          
    def add_program(self,title:str) -> "Transcript":
        self.program_titles.append(title)
        return self
    
    def get_program_titles(self):
        return self.program_titles

    def add_course(self, subject_code: str, course_code: int, grade: str, credit: int,) -> "Transcript":
        self.courses.append(Course(
            subject_code=subject_code,
            course_code=course_code,
            grade=grade,
            credit=credit,
        ))
        return self
                
    def __iter__(self) -> Iterator[Course]:
        for course in self.courses:
            yield course
