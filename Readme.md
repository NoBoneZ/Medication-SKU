
---



This repository contains an API to manage a medication SKU catalogue, providing users with functionality to **create**, **read**, **update**, and **delete** individual medication SKUs. Additionally, it supports **bulk upload** of medication SKUs to the catalogue.

## Features
- **CRUD operations** for individual medication SKUs through dedicated API endpoints.
- **Bulk upload** functionality for adding multiple medication SKUs at once.

## Postman Documentation
The API endpoints for CRUD operations and bulk upload are documented in Postman. You can view and test these endpoints via the Postman collection linked below.

- [Postman API Documentation](https://documenter.getpostman.com/view/26527466/2sAYBSkDto)

## Project Setup

There are two primary ways to launch the project: 

1. **Using Normal (Local) Setup**
2. **Using Docker**

### Normal Setup

Follow these steps to run the project locally:

#### Prerequisites:
- Python 3.11+
- pip (Python package installer)
- PostgreSQL (or use Docker for containerized database setup)

#### Steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/https://github.com/NoBoneZ/axmed-assessment.git
    cd axmed-assessment
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Setup environment variables:**
    Create a `.env` file by copying from the `.env.example` provided:
    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file to match your local configuration.

4. **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

5. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at [http://localhost:8000](http://localhost:8000).

### Docker Setup

To run the project using Docker, follow the steps below.

#### Prerequisites:
- Docker
- Docker Compose

#### Steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/NoBoneZ/axmed-assessment.git
    cd axmed-assessment
    ```

2. **Create a `.env` file:**
    Copy the `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```

    Edit `.env` to match your configuration, such as the database and secret keys.

3. **Build and run the application using Docker Compose:**
    ```bash
    docker-compose up --build
    ```

This will build the Docker image for the Django app and start the containers for both the application and PostgreSQL.

The application will be available at [http://localhost:8000](http://localhost:8000).

### Environment Variables

Here are the environment variables used in the project:

- **API-KEY**: Used for authenticating requests to the API.
- **HASH-KEY**: A key generated from the combination of `API_KEY`, `SECRET_KEY`, and `IDEMPOTENCY_KEY`, used for request validation.
- **IDEMPOTENCY-KEY**: A unique key.

The `.env.example` file is provided to help structure your `.env` file. Ensure all necessary keys are set, including the `API_KEY`, `SECRET_KEY`, and any database configurations.

```env
API_KEY=your_api_key
SECRET_KEY=your_secret_key
DB_NAME=your_db_name
DB_USERNAME=your_db_user
DB_PASSWORD=your_db_password
```

### Security

The project uses **AES encryption** for additional security. If the `USE_ENCRYPTION` variable is set to `True` in the `.env` file, AES encryption will be applied to the payload of requests.

Here is an explanation of how the AES encryption works:
- **AES Encryption**: Data is encrypted using a shared secret key. The secret key is typically combined with a salt and an initialization vector (IV) to ensure secure encryption and decryption.
- Requests that require encryption will need to include an encrypted body, and the server will decrypt it before processing.

If encryption is enabled, each request must include:
- `API-KEY`: For identifying the source.
- `HASH-KEY`: Generated using the combination of the `API_KEY`, `SECRET_KEY`, and the `IDEMPOTENCY_KEY`.
- `IDEMPOTENCY-KEY`: A unique identifier.

### Hash Key and Idempotency Key

The `HASH-KEY` is created by concatenating the following three values:
1. `API-KEY`
2. `SECRET-KEY`
3. `IDEMPOTENCY-KEY`

The `IDEMPOTENCY-KEY` is a unique key for the request, typically representing the current timestamp or another value that ensures uniqueness. It is used as the third value in the concatenation, alongside the `API-KEY` and `SECRET-KEY`.

Here’s how to generate the `HASH-KEY`:

1. Concatenate the `API-KEY`, `SECRET-KEY`, and `IDEMPOTENCY-KEY` (which can be a timestamp or a unique string).
2. Encode the concatenated string in UTF-8.
3. Hash the resulting string using the SHA256 algorithm.
4. Output the hashed string in hexadecimal format.

This `HASH-KEY` will be used in each API request to ensure data integrity and security.

### Test Cases

The project includes tests for the **Catalogue** and **Account** apps. These tests ensure that the API behaves correctly and can handle requests as expected. To run the tests:

1. **Run tests locally:**
    ```bash
    python manage.py test
    ```

2. **Running tests with Docker:**
    ```bash
    docker-compose exec axmed_django python manage.py test
    ```

The tests will verify that the CRUD operations and bulk upload functionality work as intended, along with any other business logic implemented in the APIs.

### Extra Headers

Each API request must include the following headers for security:

- `API-KEY`: Your API key for authenticating the request.
- `HASH-KEY`: A hashed key generated by combining `API_KEY`, `SECRET_KEY`, and the `IDEMPOTENCY-KEY`.
- `IDEMPOTENCY-KEY`: A unique identifier for each request to avoid duplicate submissions.

### Troubleshooting

If you encounter any issues during the setup or while running the project, ensure that the following steps have been correctly followed:
- The `.env` file contains the correct keys and database configurations.
- Docker and Docker Compose are installed correctly if using the containerized setup.
- Dependencies are installed successfully when using the local setup.
- The developer could also be reached on email, via adekunleabraham09@gmail.com, or via mobile on +2347019829316 

---
