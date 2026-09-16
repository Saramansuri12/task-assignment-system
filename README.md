# AI-Powered Intelligent Task Assignment System

An AI-powered full-stack application that recommends suitable employees for tasks based on skills, experience, availability, and reliability.

## Features

- Employee and task management
- Skill-based employee matching
- AI/ML-based recommendations
- Employee ranking with match scores
- Explainable recommendations
- Task assignment and status management
- Dashboard for workforce and assignment overview
- REST APIs using FastAPI

## Tech Stack

**Frontend:** React  
**Backend:** Python, FastAPI, SQLAlchemy  
**ML:** Python, Machine Learning  
**Database:** SQL  
**Testing:** Postman, Swagger/OpenAPI  

## Workflow

```text
Task Requirements
       ↓
Employee Data
       ↓
Skill + Experience + Availability + Reliability
       ↓
ML / Recommendation Engine
       ↓
Ranked Employees
       ↓
Task Assignment


## Dataset

The project uses a structured workforce task-assignment dataset containing information about:

- Employees and their derived attributes
- Employee skills and proficiency levels
- Tasks and projects
- Required skills for each task
- Skill reference information
- Historical task assignments

### Dataset Details

| Item | Details |
|---|---|
| **Dataset Name** | Task Assignment Dataset |
| **Format** | CSV |
| **Main Files** | `task_assignments.csv`, `projects_tasks.csv`, `task_required_skills.csv`, `employee_skill_profiles.csv`, `employee_derived_attributes.csv`, `esco_skill_reference.csv` |
| **Purpose** | Employee-task matching and recommendation |
| **Source / Author** | Add the original dataset author/source here |
| **Download Source** | Add the original dataset URL here |

### Download

The dataset can be downloaded from the original source:

**Dataset Source:** `ADD_DATASET_SOURCE_URL_HERE`

After downloading, place the CSV files in the project's data directory:

```text
task-assignment-system/
└── backend/
    └── data/
        ├── task_assignments.csv
        ├── projects_tasks.csv
        ├── task_required_skills.csv
        ├── employee_skill_profiles.csv
        ├── employee_derived_attributes.csv
        └── esco_skill_reference.csv
### Authors

**Sara Mansuri**  
Machine Learning & Frontend

**Divya Kansara**  
Backend & Integration
