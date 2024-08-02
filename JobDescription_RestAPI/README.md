# JD-RecruiterAI

JD-RecruiterAI is an AI-powered job description generator that leverages language models to create customized job descriptions based on user input. This project uses Hugging Face's language models and FastAPI for API services.

## Features

- Generate job descriptions based on company details and requirements.
- Create, read, update, and delete job descriptions.
- Integrate with Hugging Face's language models for natural language processing.

## Getting Started

### Prerequisites

- Python 3.10+
- MongoDB (for storing job descriptions)
- Hugging Face API key

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/JD-RecruiterAI.git
    cd JD-RecruiterAI
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables by creating a `.env` file in the root directory:
    ```bash
    touch .env
    ```

    Add your Hugging Face API token to the `.env` file:
    ```env
    HUGGINGFACEHUB_API_TOKEN=your_huggingface_api_token
    ```

### Usage

1. Start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

### API Endpoints

#### Create Job Description

- **URL**: `/jds`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
      "prompt": "Prompt details here..."
    }
    ```
- **Response**:
    ```json
    {
      "id": 1,
      "prompt": "Prompt details here...",
      "job_description": "Generated job description..."
    }
    ```

#### Get All Job Descriptions

- **URL**: `/jds`
- **Method**: `GET`
- **Response**:
    ```json
    [
      {
        "id": 1,
        "prompt": "Prompt details here...",
        "job_description": "Generated job description..."
      },
      ...
    ]
    ```

#### Get Job Description by ID

- **URL**: `/jds/{id}`
- **Method**: `GET`
- **Response**:
    ```json
    {
      "id": 1,
      "prompt": "Prompt details here...",
      "job_description": "Generated job description..."
    }
    ```

#### Update Job Description

- **URL**: `/jds/{id}`
- **Method**: `PUT`
- **Request Body**:
    ```json
    {
      "prompt": "Updated prompt details here..."
    }
    ```
- **Response**:
    ```json
    {
      "id": 1,
      "prompt": "Updated prompt details here...",
      "job_description": "Updated job description..."
    }
    ```

#### Delete Job Description

- **URL**: `/jds/{id}`
- **Method**: `DELETE`
- **Response**:
    ```json
    {
      "detail": "Job description deleted successfully"
    }
    ```

### Project Structure

- `main.py`: Entry point for the FastAPI application.
- `routes/`: Contains the route definitions for the API.
- `services/`: Contains the service logic for handling job descriptions.
- `models/`: Contains the Pydantic models used for data validation.
- `schemas/`: Contains the schemas used for request and response validation.
- `config/`: Contains the database configuration.

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.
