# Use the NVIDIA CUDA base image
FROM nvidia/cuda:11.2.1-cudnn8-runtime-ubuntu20.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install PaddlePaddle with GPU support and FastAPI
RUN pip3 install paddlepaddle-gpu paddleocr fastapi uvicorn

# Create a directory for the app
WORKDIR /app

# Copy the FastAPI app code
COPY . /app

# Expose the FastAPI port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
