# Deployment Guide for Financial Advisor Leads App

The project is already initialized with Git and the remote repository is configured.

## Step 1: Push Code to GitHub

Open your terminal in the project directory and run:

```bash
git push -u origin main
```

- You may be prompted to sign in to GitHub.
- Once the command completes, your code will be on GitHub.

## Step 2: Deploy to Streamlit Community Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **New app**.
3.  **Method 1: Use the Interactive Picker (Recommended)**
    - Select your repository: `localauditpro-stack/wealth-strategy-app`
    - Branch: `main`
    - Main file path: `app.py`
    - Click **Deploy!**

4.  **Method 2: Paste GitHub URL**
    - If you are asked to paste a "GitHub URL", use this exact link:
      ```
      https://github.com/localauditpro-stack/wealth-strategy-app/blob/main/app.py
      ```
    - This points directly to the main application file.

## Step 3: Share

- Once deployed, you will get a URL (e.g., `https://wealth-strategy-app.streamlit.app`).
- **Share this link!**
