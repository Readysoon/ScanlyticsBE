# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install dependencies into the container directly acting as a virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Check if surrealdb is installed correctly
RUN python -c "import surrealdb" && echo "SurrealDB package installed successfully."

# Copy the rest of the application code into the container
COPY . .

# Run the app with uvicorn
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001" ]

# Excuse me, second test
