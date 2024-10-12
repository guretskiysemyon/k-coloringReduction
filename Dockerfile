# Use a more recent Python runtime as the base image
FROM python:3.10.15-slim

# Install system dependencies and build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgmp-dev \
    wget \
    autoconf \
    gperf \
    flex \
    bison \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Cython before building Boolector
RUN pip install --no-cache-dir cython

# Install BTOR solver using pysmt-install
RUN pysmt-install --btor --confirm-agreement

# Install Z3, MathSAT, and Yices solvers using pysmt-install
RUN pysmt-install --z3 --msat --yices --confirm-agreement

# Install CVC5
RUN pip install --no-cache-dir cvc5

# Copy your application code
COPY reduction/ ./reduction/

# Expose the port your app runs on
EXPOSE 80

# Environment variables for the app
ENV NAME=GraphColoring
ENV PYTHONPATH=/app/reduction

# Command to run the app
CMD ["python3", "reduction/reduction.py"]
