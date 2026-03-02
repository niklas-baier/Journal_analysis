# Use the NVIDIA CUDA base image
FROM nvidia/cuda:12.1.0-base-ubuntu22.04

# Install Python 3.11 and Pip
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-dev \
    && rm -rf /var/lib/apt/lists/*

# Set python3.11 as the default 'python' command
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# cpu version uncomment the prev lines 1. Start with Python 3.11
#FROM python:3.11-slim

# 2. Create a workspace at the ROOT of the project
WORKDIR /app

# 3. Install requirements
COPY requirements.txt .
# Use python -m pip to ensure it installs to the 3.11 site-packages
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt
# 4. Pre-download NLTK data
RUN python -m nltk.downloader punkt punkt_tab words

# 5. Copy everything into /app
# This ensures /app/src, /app/notebooks, and /app/pyproject.toml exist
COPY src/ ./src/
COPY notebooks/ ./notebooks/
COPY configs/ ./configs/
COPY pyproject.toml .

# 6. Install your package while standing in /app
# This links the 'diary_analyzer' folder in /app/src/ to your python libs
RUN pip install -e .

# 7. Move to notebooks folderfor the final command
WORKDIR /app/notebooks

# 8. Start the script
CMD ["python", "-u", "personal.py"]
