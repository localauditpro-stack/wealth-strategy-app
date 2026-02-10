# Deployment Guide for Financial Advisor Leads App

This guide will help you deploy your application to **Streamlit Community Cloud**, which is the easiest and free way to share Streamlit apps.

## Prerequisites

1.  **GitHub Account**: You need a GitHub account. If you don't have one, sign up at [github.com](https://github.com/).
2.  **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io/) using your GitHub account.

## Step 1: Push Code to GitHub

Since I cannot access your GitHub account directly, you need to create a repository and push the code:

1.  **Create a New Repository**:
    - Go to [GitHub - New Repository](https://github.com/new).
    - Name it something like `wealth-strategy-app`.
    - Select **Public** (Streamlit Community Cloud is free for public repos).
    - **Do NOT** check "Initialize with README", .gitignore, or license (we already have them).
    - Click **Create repository**.

2.  **Push the Code**:
    - Copy the commands under "**…or push an existing repository from the command line**".
    - It will look like this (replace `YOUR_USERNAME` with your actual username):
      ```bash
      git remote add origin https://github.com/YOUR_USERNAME/wealth-strategy-app.git
      git branch -M main
      git push -u origin main
      ```
    - Run these commands in your terminal (I can run them for you if you provide the URL).

## Step 2: Deploy to Streamlit Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **New app**.
3.  **Repository**: Select your new repository (`wealth-strategy-app`).
4.  **Branch**: `main`.
5.  **Main file path**: `app.py`.
6.  Click **Deploy!**.

## Step 3: Share

- Once deployed, you will get a URL (e.g., `https://wealth-strategy-app.streamlit.app`).
- You can share this link with anyone!

## Troubleshooting

- **Dependencies**: If the app fails to load, check the "Manage app" logs on Streamlit Cloud. It usually means a missing library in `requirements.txt`.
- **Secrets**: This app currently does not use any secrets (API keys), so you don't need to configure them yet.
