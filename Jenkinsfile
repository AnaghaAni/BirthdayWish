pipeline {
    agent any

    triggers {
        // Schedule to run every day at 9:30 AM
        cron('30 9 * * *')
    }

    environment {
        // Map Jenkins Credentials to Environment Variables
        // You must add these in Jenkins -> Credentials -> System -> Global credentials
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
        SENDER_EMAIL = credentials('SENDER_EMAIL')
        SENDER_PASSWORD = credentials('SENDER_PASSWORD')
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = '587'
        PYTHON_EXE = 'C:\\Users\\Anagha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
        PYTHONIOENCODING = 'utf-8'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout code from your version control system (Git, etc.)
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                bat """
                "%PYTHON_EXE%" -m venv venv
                venv\\Scripts\\python -m pip install --upgrade pip
                venv\\Scripts\\pip install -r requirements.txt
                """
            }
        }

        stage('Execute Birthday Check') {
            steps {
                echo 'Starting daily birthday check at 9:30 AM...'
                bat """
                venv\\Scripts\\python main.py
                """
            }
        }
    }

    post {
        always {
            // Optional: Archive logs or send status notifications
            archiveArtifacts artifacts: 'birthday_bot.log', allowEmptyArchive: true
        }
        success {
            echo 'Birthday wishes sent successfully!'
        }
        failure {
            echo 'Failed to send birthday wishes. Check the logs.'
        }
    }
}
