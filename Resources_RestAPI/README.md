# HR Recruiter AI

HR Recruiter AI is a FastAPI-based application designed to manage job resources by extracting and filtering candidate information from job descriptions. It uses MongoDB for storing job resource data, MySQL for candidate information, and integrates with Hugging Face LLM for natural language processing.

## Features

- Create, read, update, and delete job resources.
- Extracts key details from job descriptions using Hugging Face LLM.
- Filters candidates based on experience, skills, and qualifications.

## Table of Contents

- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8+
- MongoDB
- MySQL

### Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory with the following content:

```env
MONGODB_URI=mongodb://localhost:27017
MYSQL_URI=mysql+mysqlconnector://root:admin@localhost:3306/hr_recruiter
HUGGINGFACEHUB_API_TOKEN="your_huggingface_api_token"
```

Replace `your_huggingface_api_token` with your actual Hugging Face API token.

## Running the Application


### Run the FastAPI Application

```bash
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`.

## API Endpoints

### Create a Resource

```http
POST /api/v1/resource/
```

#### Request Body

```json
{
  "job_description": "string"
}
```

#### Response

```json
{
  "job_id": 1,
  "job_description": "string",
  "skills": ["string"],
  "qualification": ["string"],
  "experience": 0,
  "resource": ["string"]
}
```

### Get All Resources

```http
GET /api/v1/resource/
```

#### Response

```json
[
  {
    "job_id": 1,
    "job_description": "string",
    "skills": ["string"],
    "qualification": ["string"],
    "experience": 0,
    "resource": ["string"]
  }
]
```

### Get Resource by ID

```http
GET /api/v1/resource/{job_id}
```

#### Response

```json
{
  "job_id": 1,
  "job_description": "string",
  "skills": ["string"],
  "qualification": ["string"],
  "experience": 0,
  "resource": ["string"]
}
```

### Update Resource

```http
PUT /api/v1/resource/{job_id}
```

#### Request Body

```json
{
  "job_description": "string",
  "skills": ["string"],
  "qualification": ["string"],
  "experience": 0,
  "resource": ["string"]
}
```

#### Response

```json
{
  "job_id": 1,
  "job_description": "string",
  "skills": ["string"],
  "qualification": ["string"],
  "experience": 0,
  "resource": ["string"]
}
```

### Delete Resource

```http
DELETE /api/v1/resource/{job_id}
```

#### Response

```json
{
  "message": "deleted successfully"
}
```

## Development

### Code Structure

* `config/db.py`: Database configuration.
* `models/resource.py`: Pydantic models.
* `routes/resource.py`: API route definitions.
* `services/resource.py`: Business logic for resource management.
* `main.py`: Application entry point.
* `.env`: Environment variables.

### Running Tests

To be implemented...

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```bush
This `README.md` provides clear instructions and details about the project setup, environment variables, how to run the application, API endpoints, development guidelines, and contributing information.
