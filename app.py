from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from uvicorn import run as app_run

from typing import Optional

# Import your constants and pipeline modules
from src.constants import APP_HOST, APP_PORT
from src.pipline.prediction_pipeline import DiabetesData, DiabetesClassifier
from src.pipline.training_pipeline import TrainPipeline

# Initialize FastAPI app
app = FastAPI()

# Mount static files like CSS/JS/images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set Jinja2 templates directory
templates = Jinja2Templates(directory='templates')

# CORS config
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DataForm class to handle form submission
class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.Pregnancies: Optional[int] = None
        self.Glucose: Optional[int] = None
        self.BloodPressure: Optional[int] = None
        self.SkinThickness: Optional[int] = None
        self.Insulin: Optional[int] = None
        self.BMI: Optional[float] = None
        self.DiabetesPedigreeFunction: Optional[float] = None
        self.Age: Optional[int] = None

    async def get_diabetes_data(self):
        form = await self.request.form()
        self.Pregnancies = form.get("Pregnancies")
        self.Glucose = form.get("Glucose")
        self.BloodPressure = form.get("BloodPressure")
        self.SkinThickness = form.get("SkinThickness")
        self.Insulin = form.get("Insulin")
        self.BMI = form.get("BMI")
        self.DiabetesPedigreeFunction = form.get("DiabetesPedigreeFunction")
        self.Age = form.get("Age")

# Home page with input form
@app.get("/", tags=["ui"])
async def index(request: Request):
    return templates.TemplateResponse("diabetes_form.html", {"request": request, "context": " "})

# Trigger training pipeline
@app.get("/train")
async def train_model():
    try:
        train_pipeline = TrainPipeline()
        train_pipeline.run_pipeline()
        return Response("Training successful!!!")
    except Exception as e:
        return Response(f"Training failed: {e}")

# Predict endpoint
@app.post("/")
async def predict_diabetes(request: Request):
    try:
        form = DataForm(request)
        await form.get_diabetes_data()

        diabetes_data = DiabetesData(
            Pregnancies=form.Pregnancies,
            Glucose=form.Glucose,
            BloodPressure=form.BloodPressure,
            SkinThickness=form.SkinThickness,
            Insulin=form.Insulin,
            BMI=form.BMI,
            DiabetesPedigreeFunction=form.DiabetesPedigreeFunction,
            Age=form.Age
        )

        input_df = diabetes_data.get_diabetes_input_dataframe()
        predictor = DiabetesClassifier()
        prediction = predictor.predict(input_df)[0]

        status = "Positive for Diabetes" if prediction == 1 else "Negative for Diabetes"

        return templates.TemplateResponse("diabetes_form.html", {
            "request": request,
            "context": status,
        })

    except Exception as e:
        return {"status": False, "error": str(e)}

# Run the app
if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=8080)
