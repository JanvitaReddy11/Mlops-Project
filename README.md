# Diabetes Prediction System


## Project Overview

This project implements an end-to-end machine learning pipeline for predicting diabetes based on patient health metrics. I've created a modular system that handles everything from data ingestion through MongoDB to model deployment on Google Cloud Platform.

## What I've Built

- **Complete ML Pipeline**: Implemented a structured workflow from data collection to model deployment
- **MongoDB Atlas Integration**: Set up cloud database for storing and retrieving the diabetes dataset
- **Data Engineering Components**: Created robust modules for data ingestion, validation, and transformation
- **Model Training & Evaluation**: Developed systems to train, evaluate, and select the best performing model
- **GCP Deployment**: Deployed the solution using Google Cloud Platform services
- **CI/CD Pipeline**: Implemented automated testing and deployment using GitHub Actions
- **Containerization**: Dockerized the application for consistent environment across development and production
- **Web Interface**: Built a Flask-based web application for both training and prediction functionalities

## Key Features

- Modular component-based architecture
- Comprehensive logging and exception handling
- Schema-based data validation
- Automated model versioning and registry
- Real-time prediction capabilities

## Technical Implementation

The project follows the ML pipeline pattern with these key components:

1. **Data Ingestion**: Connects to MongoDB to extract and prepare training/testing datasets
2. **Data Validation**: Validates the schema and quality of incoming data
3. **Data Transformation**: Applies preprocessing steps to prepare features for modeling
4. **Model Trainer**: Trains various ML models with hyperparameter tuning
5. **Model Evaluation**: Evaluates models against existing production versions
6. **Model Pusher**: Deploys the best model to GCP for production use

## Deployment

The application has been successfully deployed on GCP and is available
https://diabetes-app-962034482112.us-central1.run.app/


## Technologies Used

- Python 3.10
- MongoDB Atlas
- Google Cloud Platform
- Docker
- GitHub Actions
- Flask
- Scikit-learn

## Setup Instructions

For local development:

1. Clone the repository
2. Create a virtual environment: `conda create -n diabetes python=3.10 -y`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up MongoDB connection URL as an environment variable
5. Set up GCP credentials
6. Run the application: `python app.py`