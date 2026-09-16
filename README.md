# AI-Powered Intelligent Task Assignment System

An AI-powered full-stack application that recommends suitable employees for tasks based on **skills, experience, availability, workload, and reliability**.

The system helps organizations intelligently match tasks with employees, rank suitable candidates, and manage assignments through a centralized workforce management platform.

---

## Features

* Employee management
* Task and project management
* Skill-based employee matching
* AI/ML-powered employee recommendations
* Employee ranking with match scores
* Explainable recommendations
* Skill, experience, availability, and reliability analysis
* Task assignment and status management
* Assignment approval and validation
* Workforce dashboard
* REST APIs using FastAPI
* Interactive API documentation using Swagger/OpenAPI

---

## System Workflow

```text
Task Requirements
       ↓
Task & Required Skills
       ↓
Employee Data
       ↓
Skills + Experience + Availability + Workload + Reliability
       ↓
Recommendation / ML Engine
       ↓
Employee Ranking
       ↓
Explainable Match Scores
       ↓
Task Assignment
       ↓
Assignment Status Tracking
```

---

# Dataset

The project uses a structured workforce task-assignment dataset containing information about:

* Employees and their derived attributes
* Employee skills and proficiency levels
* Tasks and projects
* Required skills for each task
* Skill reference information
* Historical task assignments

## Dataset Details

| Item                | Details                                                                                                                                                                |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Dataset Name**    | Task Assignment Dataset                                                                                                                                                |
| **Format**          | CSV                                                                                                                                                                    |
| **Main Files**      | `task_assignments.csv`, `projects_tasks.csv`, `task_required_skills.csv`, `employee_skill_profiles.csv`, `employee_derived_attributes.csv`, `esco_skill_reference.csv` |
| **Purpose**         | Employee-task matching, recommendation, and assignment analysis                                                                                                        |
| **Source / Author** | Add the original dataset author/source here                                                                                                                            |
| **Download Source** | Add the original dataset URL here                                                                                                                                      |

> **Note:** Replace the source information above with the original dataset citation before publishing the project.

---

## Dataset Files

The main dataset files are:

```text
task_assignments.csv
    ↓
Historical employee-task assignments

projects_tasks.csv
    ↓
Project and task information

task_required_skills.csv
    ↓
Skills required for each task

employee_skill_profiles.csv
    ↓
Employee skills and proficiency levels

employee_derived_attributes.csv
    ↓
Employee availability, workload, experience,
performance, and other derived attributes

esco_skill_reference.csv
    ↓
Skill reference and skill metadata
```

---

## Dataset Setup

After downloading the dataset from its original source, place the CSV files inside the project's data directory.

```text
task-assignment-system/
│
├── backend/
│   │
│   └── data/
│       ├── task_assignments.csv
│       ├── projects_tasks.csv
│       ├── task_required_skills.csv
│       ├── employee_skill_profiles.csv
│       ├── employee_derived_attributes.csv
│       └── esco_skill_reference.csv
│
├── frontend/
│
├── ml/
│
├── docs/
│
└── docker-compose.yml
```

---

# Recommendation System

The recommendation engine evaluates employees based on multiple factors.

### Main Factors

* **Skill Match** — How well the employee's skills match the task requirements
* **Experience** — Relevant employee experience
* **Availability** — Whether the employee is currently available
* **Workload** — Current workload of the employee
* **Performance / Reliability** — Historical performance and reliability indicators

The system combines these factors to generate a final recommendation score and rank suitable employees.

### Example

```text
Task
 │
 ├── Required Skill: Python
 ├── Required Skill: SQL
 └── Required Experience: 2 years
          │
          ↓
   Recommendation Engine
          │
          ↓
 ┌─────────────────────────────┐
 │ Employee A → 92% Match      │
 │ Employee B → 87% Match      │
 │ Employee C → 81% Match      │
 └─────────────────────────────┘
          │
          ↓
    Ranked Employees
```

---

# Explainable Recommendations

The system does not only return a ranked employee list.

It also provides the factors contributing to the recommendation, such as:

```text
Employee: EMP001

Skill Match:       92%
Experience Score:  85%
Availability:      90%
Workload Score:    80%
Performance:       88%

Final Match Score: 88.5%
```

This makes the recommendation easier for managers to understand and evaluate.

---

# Task Assignment Workflow

```text
Create Task
     ↓
Define Required Skills
     ↓
Generate Employee Recommendations
     ↓
Review Recommended Employees
     ↓
Select Employee
     ↓
Create Assignment
     ↓
Pending / Approval
     ↓
In Progress
     ↓
Completed
```

Assignments can also be cancelled or rejected when required.

### Assignment Statuses

* `ACTIVE`
* `PENDING`
* `IN_PROGRESS`
* `COMPLETED`
* `CANCELLED`
* `REJECTED`

---

# Manager Workflow

The system is designed to give managers a centralized view of projects, employees, recommendations, and assignments.

```text
Manager Dashboard
       │
       ├── View Projects
       │      ↓
       │   Project Progress
       │      ↓
       │   Tasks & Assignments
       │
       ├── View Employees
       │      ↓
       │   Employee Details
       │      ↓
       │   Skills + Experience
       │      ↓
       │   Workload + Availability
       │
       └── Recommendations
              ↓
        Recommended Employees
              ↓
        Review Match Factors
              ↓
        Assign Employee
```

Managers can use employee information and recommendation results to make informed task-assignment decisions.

---

# API

The backend provides REST APIs using **FastAPI**.

API documentation is available through:

```text
Swagger UI
http://127.0.0.1:8000/docs
```

and:

```text
ReDoc
http://127.0.0.1:8000/redoc
```

> These URLs are available when the FastAPI backend is running locally.

---

# Tech Stack

## Frontend

* React
* JavaScript
* HTML
* CSS

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic

## Machine Learning

* Python
* Pandas
* NumPy
* Scikit-learn
* Recommendation / ranking logic

## Database

* PostgreSQL / SQL database

## Graph Database

* Neo4j

## API Testing

* Postman
* Swagger / OpenAPI

---

# Project Structure

```text
task-assignment-system/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── data/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── ml/
│   └── machine learning / recommendation components
│
├── neo4j/
│   └── graph database components
│
├── docs/
│
├── scripts/
│
├── docker-compose.yml
│
└── README.md
```

---

# How It Works

### 1. Employee Data

Employee information such as skills, experience, availability, workload, and performance is stored in the system.

### 2. Task Requirements

Each task contains information about the project, required skills, and other requirements.

### 3. Employee Matching

The recommendation engine compares task requirements with employee attributes.

### 4. Employee Ranking

Suitable employees are ranked according to their calculated match scores.

### 5. Explainable Recommendation

The system provides the factors behind the recommendation so that managers can understand why an employee was recommended.

### 6. Assignment

The manager can select a recommended employee and assign them to the task.

### 7. Progress Tracking

Project and task information can be monitored through the dashboard, allowing managers to track assignment and project progress.

---

# Running the Project

## Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

---

# Future Improvements

* **Individual Employee Selection** — Allow managers to directly choose and assign an individual employee to a task instead of relying only on team-based recommendations.

* **Project Progress Dashboard** — Provide a dashboard where managers can monitor overall project progress, task completion, pending tasks, active assignments, completed tasks, and project status.

* **Detailed Employee Profiles** — Allow managers to view detailed information about individual employees, including skills, proficiency levels, experience, availability, workload, performance, and current assignments.

* **Employee Recommendation Insights** — Show managers the recommendation results and the factors behind each recommendation, including skill match, experience, availability, workload, performance, and overall match score.

* **Employee Assignment History** — Provide a complete history of an employee's previous and current task assignments, including assignment status and completion information.

* **Advanced Team Formation** — Automatically generate suitable teams based on required skills, employee availability, workload, experience, and performance.

* **Workload Optimization** — Improve task allocation by balancing employee workloads and reducing the possibility of employee over-assignment.

* **Learning from Historical Assignments** — Use historical task assignment and completion data to improve future employee recommendations.

* **Real-Time Workforce Monitoring** — Provide real-time information about employee availability, workload, active tasks, and project progress.

* **Advanced Analytics and Reporting** — Add charts and reports for project performance, employee utilization, task completion, workload distribution, and assignment outcomes.

* **Role-Based Access Control** — Provide different access levels and functionality for managers, employees, and administrators.

* **Real-Time Notifications** — Notify managers and employees about new assignments, status changes, approvals, deadlines, and completed tasks.

* **Cloud Deployment** — Deploy the application using cloud infrastructure for scalable and remote access.

---

# Authors

### Sara Mansuri

**Machine Learning & Frontend**

### Divya Kansara

**Backend & Integration**

---

# Project Objective

The objective of this project is to build an intelligent workforce management system that assists organizations in assigning tasks to suitable employees based on multiple employee and task attributes.

Instead of relying only on manual assignment, the system uses structured employee and task data to generate ranked recommendations and provide explainable insights for task allocation.

The platform also provides managers with a centralized view of **projects, tasks, employees, recommendations, assignments, and project progress**.

---


