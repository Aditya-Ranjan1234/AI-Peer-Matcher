# MongoDB Atlas Setup Guide for Render

This guide will walk you through setting up a free MongoDB Atlas database and connecting it to your Render backend.

## Phase 1: Create MongoDB Atlas Account & Cluster

1.  **Go to MongoDB Atlas**: Visit [https://www.mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register).
2.  **Sign Up**: Create an account (you can use Google Sign-in).
3.  **Create a Cluster**:
    *   Choose the **M0 Sandbox** (Free Tier).
    *   Select a provider (AWS is fine) and a region close to you (e.g., N. Virginia or Frankfurt).
    *   Click **Create Deployment**.

## Phase 2: Configure Security (Crucial!)

1.  **Create a Database User**:
    *   Go to **Security** -> **Database Access** (sidebar).
    *   Click **+ Add New Database User**.
    *   **Authentication Method**: Password.
    *   **Username**: `admin` (or whatever you prefer).
    *   **Password**: Click "Autogenerate Secure Password" and **COPY IT NOW**. You will need this later.
    *   **Built-in Role**: "Read and write to any database".
    *   Click **Add User**.

2.  **Allow Network Access**:
    *   Go to **Security** -> **Network Access** (sidebar).
    *   Click **+ Add IP Address**.
    *   Click **Allow Access from Anywhere** (0.0.0.0/0).
        *   *Note: Since Render's IP addresses change, this is the standard way to allow Render to connect.*
    *   Click **Confirm**.

## Phase 3: Get Connection String

1.  Go to **Deployment** -> **Database** (sidebar).
2.  Click **Connect** on your cluster.
3.  Select **Drivers**.
4.  **Driver**: Python.
5.  **Version**: 3.12 or later.
6.  **Copy the Connection String**:
    *   It will look like: `mongodb+srv://admin:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0`
    *   **Replace `<password>`** with the password you copied in Phase 2.

## Phase 4: Configure Render

1.  Go to your [Render Dashboard](https://dashboard.render.com/).
2.  Click on your **Web Service** (the backend).
3.  Go to **Environment** (sidebar).
4.  Click **Add Environment Variable**.
5.  **Key**: `MONGODB_URL`
6.  **Value**: Paste your connection string (with the real password).
7.  Click **Save Changes**.

## Next Steps

Once you have completed these steps, I will:
1.  Update `requirements.txt` to include `motor` (MongoDB driver).
2.  Update `main.py` to connect to this database.
3.  Deploy the changes.
