# Setting Up Your Bangalore Data Analyst Job Bot on GitHub

This guide will help you set up the automated job search bot on GitHub to receive daily email notifications about data analyst job opportunities in Bangalore.

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click on the '+' icon in the top-right corner and select 'New repository'
3. Name your repository (e.g., `bangalore-data-analyst-job-bot`)
4. Choose whether to make it public or private
5. Click 'Create repository'

## Step 2: Add Repository Secrets

The workflow needs access to your email credentials and API keys. Add them as repository secrets:

1. In your repository, go to 'Settings' > 'Secrets and variables' > 'Actions'
2. Click 'New repository secret'
3. Add the following secrets:
   - `SMTP_PASS`: Your email password or app password
   - `SERPAPI_KEY`: Your SerpAPI key (if you're using it)

## Step 3: Push Your Code to GitHub

From your local machine, push the code to your GitHub repository:

```bash
# Initialize git in your project folder (if not already done)
git init

# Add all files to git
git add .

# Commit the changes
git commit -m "Initial commit"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git

# Push to GitHub
git push -u origin main
```

## Step 4: Configure Your .env File

Before pushing to GitHub, make sure your `.env` file is properly configured with your email settings:

1. Copy `.env.example` to `.env` if you haven't already
2. Fill in all the required fields:
   - SMTP settings for your email provider
   - Email addresses for sending and receiving notifications
   - Search parameters for job listings

Note: The `.env` file is included in `.gitignore` and won't be pushed to GitHub. The GitHub Actions workflow will use the repository secrets you configured in Step 2.

## Step 5: Verify GitHub Actions Workflow

After pushing your code:

1. Go to the 'Actions' tab in your GitHub repository
2. You should see the workflow 'Daily Bangalore Data Analyst Job Scan'
3. The workflow is scheduled to run automatically at 5:30 AM and 1:00 PM IST daily
4. You can also manually trigger the workflow by clicking 'Run workflow'

## What to Expect

Once set up, you'll receive email notifications with data analyst job listings twice daily. Each email will contain:

- Job titles with links to apply
- Company names
- Locations
- Source of the job listing

The workflow also saves HTML reports as artifacts that you can download from the Actions tab.

## Troubleshooting

If you're not receiving emails:

1. Check if the GitHub Actions workflow is running successfully
2. Verify your email credentials and settings in the repository secrets
3. Check your spam folder
4. Make sure your email provider allows sending emails via SMTP

For Gmail users, you'll need to use an App Password instead of your regular password. [Learn how to create an App Password](https://support.google.com/accounts/answer/185833).