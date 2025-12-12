# AWS Deployment Guide

This guide describes how to deploy the Local RAG Demo to **AWS EC2** (simplest method).

## Prerequisites
1.   an **AWS Account**.
2.  **SSH Client** (like authentication keys) to access the server.

---

## Method 1: Deploy on EC2 (Virtual Machine)

This is the most standard way to host a python application.

### 1. Launch an Instance
1.  Log in to the **AWS Console** and go to **EC2**.
2.  Click **Launch Instance**.
3.  **Name**: `RAG-Demo-Server`.
4.  **AMI**: Choose **Ubuntu Server 24.04 LTS** (Free tier eligible).
5.  **Instance Type**: `t3.medium` or larger is recommended.
    *   *Note: `t2.micro` (free tier) might be too small (1GB RAM) to load the AI models.*
    *   `t3.medium` (4GB RAM) costs roughly $0.04/hour.
6.  **Key Pair**: Create a new key pair (save the `.pem` file) or use an existing one.
7.  **Network Settings**:
    *   Allow SSH (Port 22).
    *   Allow HTTP/HTTPS (Optional).
    *   **IMPORTANT**: We need to open Port **8501** later.

### 2. Configure Security Group
1.  After finding the instance, go to the **Security** tab -> Click on the **Security Group**.
2.  Click **Edit inbound rules**.
3.  Add Rule:
    *   **Type**: Custom TCP
    *   **Port range**: `8501`
    *   **Source**: `0.0.0.0/0` (Anywhere)
4.  Save rules.

### 3. Connect to the Instance
Use SSH to connect (replace `key.pem` and `public-ip` with yours):
```bash
ssh -i "path/to/key.pem" ubuntu@<your-public-ip>
```

### 4. Setup the Environment
Run these commands on the AWS server to install Docker and Git:

```bash
# Update system
sudo apt-get update
sudo apt-get install -y git docker.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```
*(Log out and log back in for the user group change to take effect)*

### 5. Deploy the App
Clone your repo and run it with Docker:

```bash
# Clone the repository
git clone https://github.com/TechSuvam/RAG_Demo.git
cd RAG_Demo

# Build the Docker image (this takes a few minutes)
docker build -t rag-app .

# Run the container
# -d: Run in background
# -p 8501:8501: Map port 8501
docker run -d -p 8501:8501 --name rag-container rag-app
```

### 6. Access the App
Open your browser and visit:
`http://<your-ec2-public-ip>:8501`

---

## Method 2: AWS App Runner (Managed Container)

If you don't want to manage a server, use App Runner.

1.  Push your code (including the `Dockerfile`) to GitHub.
2.  Go to **AWS App Runner** in the console.
3.  Create Service -> Source: **Source Code Repository**.
4.  Connect your GitHub and select the `RAG_Demo` repo.
5.  Deployment Settings: **Automatic**.
6.  Configuration:
    *   Runtime: **Python 3** (or Docker).
    *   Build Command: `pip install -r requirements.txt`
    *   Start Command: `streamlit run app.py --server.port 8080 --server.address 0.0.0.0`
    *   **Port**: 8080.
7.  Deploy.
    *   *Note: App Runner is more expensive than a small EC2 instance but easiest to manage.*
