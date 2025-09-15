from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

class StudentRequirements(BaseModel):
    max_students: int
    min_age: int
    max_age: int
    prerequisites: List[str]

class CourseContent(BaseModel):
    syllabus: str
    equipment_required: List[str]

class MediaResources(BaseModel):
    course_image_url: Optional[str] = None
    promo_video_url: Optional[str] = None

class Pricing(BaseModel):
    currency: str
    amount: float
    branch_specific_pricing: bool

class Settings(BaseModel):
    offers_certification: bool
    active: bool

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    code: str
    description: str
    martial_art_style_id: str
    difficulty_level: str
    category_id: str
    instructor_id: str
    student_requirements: StudentRequirements
    course_content: CourseContent
    media_resources: MediaResources
    pricing: Pricing
    settings: Settings
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CourseCreate(BaseModel):
    title: str
    code: str
    description: str
    martial_art_style_id: str
    difficulty_level: str
    category_id: str
    instructor_id: str
    student_requirements: StudentRequirements
    course_content: CourseContent
    media_resources: MediaResources
    pricing: Pricing
    settings: Settings

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    martial_art_style_id: Optional[str] = None
    difficulty_level: Optional[str] = None
    category_id: Optional[str] = None
    instructor_id: Optional[str] = None
    student_requirements: Optional[StudentRequirements] = None
    course_content: Optional[CourseContent] = None
    media_resources: Optional[MediaResources] = None
    pricing: Optional[Pricing] = None
    settings: Optional[Settings] = None
