# Deployment Guide for Sentiment Analysis API

## Prerequisites
- **VPS** with Docker and Docker Compose installed.
- **Git** installed on the VPS.
- **SSH Access** to your VPS.

## Deployment Steps

1.  **Access your VPS** via SSH:
    ```bash
    ssh user@your-vps-ip
    ```

2.  **Navigate to your applications folder** (e.g., `/var/www` or `~/apps`):
    ```bash
    mkdir -p sentiment-api
    cd sentiment-api
    ```

3.  **Clone the Repository** (Replace with your actual GitHub URL):
    ```bash
    git clone https://github.com/YOUR_USERNAME/REPO_NAME.git .
    ```

4.  **Configuration (Optional)**:
    - If you need to change ports, edit `docker-compose.yml`:
      ```bash
      nano docker-compose.yml
      ```
    - The default port is `5000`. Ensure this port is open in your VPS firewall (and ICP panel firewall if applicable).

5.  **Build and Run**:
    Run the application in detached mode (background):
    ```bash
    docker-compose up -d --build
    ```
    *Note: The first build will take a few minutes as it downloads large machine learning libraries (PyTorch).*

6.  **Verify Status**:
    Check if the container is running:
    ```bash
    docker-compose ps
    ```
    View logs if needed:
    ```bash
    docker-compose logs -f
    ```

## Updates
To update the application after pushing changes to GitHub:
```bash
git pull
docker-compose up -d --build
```
