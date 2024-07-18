# Use the NVIDIA CUDA base image
FROM ubuntu:22.04

# Update and upgrade system packages, then install necessary dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    python3-pip \
    python3 \
    libgl1-mesa-glx \
    libglib2.0-0 && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install PaddlePaddle with GPU support and FastAPI
RUN pip3 install paddlepaddle paddleocr fastapi uvicorn requests

# Create a directory for the app
WORKDIR /app

# Copy the FastAPI app code
COPY . /app

# Expose the FastAPI port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

