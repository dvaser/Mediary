# Project: MEDIARY

<div style="text-align: left;">
  <img src="project/img/header.png" alt="Header Image" style="width: 60%;">
</div>

## Project Purpose

> The aim is to automate processes such as diagnosing based on patient history, recommending tests, interpreting results, and providing personalized health assessments with the support of artificial intelligence.
>
> The project aims to provide clinical decision support for doctors, offer preliminary information to patients, and reduce the workload within the healthcare system.
>
> In the initial phase of the project, the data collection process has been focused on the field of Internal Medicine; therefore, diseases specific to this area will be prioritized for evaluation. In later stages, data will also be gathered from other medical specialties, aiming to obtain stronger insights into a broader range of health conditions.

## Team Details

>  **[Click here to see team details](project/markdowns/team.md)**

## Sprint Details

>  **[Click here to see the sprint-1 workouts](project/markdowns/sprint/sprint-1.md)** 
>
>  **[Click here to see the sprint-2 workouts](project/markdowns/sprint/sprint-2.md)** 
>
>  **[Click here to see the sprint-3 workouts](project/markdowns/sprint/sprint-3.md)** 


## 🚀 Installation Steps

You can run the project by following the steps below:

```bash
# 1. Clone repository (optional)
git clone https://github.com/dvaser/Mediary.git
cd Mediary

# 2. Create a virtual environment (.venv)
python -m venv .venv

# 3. Activate the virtual environment (.venv) 
    # Windows (PowerShell)
    .venv\Scripts\Activate.ps1

    # If you get a script execution error in PowerShell:
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

    # Windows (CMD)
    .venv\Scripts\activate.bat

    # Windows (Powershell)
    .venv\Scripts\activate

    # macOS / Linux
    source .venv/bin/activate

# 4. Install the required packages
pip install -r requirements.txt

# 5. Start the application
python main.py

# 6. Log out of the virtual environment (.venv)
deactivate

# (In addition) Transfer libraries used (requirements.txt)
pip freeze > requirements.txt
```

## Pipeline
```
PDFChunker  --->  GeminiEmbedder  --->  ChromaDBWrapper  --->  Query + Gemini Answer
```

## Structure
```
project/
│
├── code/
│   ├── pdf_prep.py               # PDFChunker
│   ├── model/
│   │   ├── gemini.py             # GeminiEmbedder + GeminiAnswerGenerator
│   │   └── chroma.py             # ChromaDBWrapper
│   └── pipeline.py               # RAGPipeline
│
├── main.py                       # Uygulamanın başlangıç noktası
└── chromadb_persist/             # Vektör veritabanı dosyaları (otomatik oluşur)
```

## Product Features

> 🧠 **AI-Powered Diagnosis Prediction:** Predicts possible diseases based on the patient's medical history.
>
> 🔬 **Test Recommendation System:** Lists diagnostic tests relevant to the suspected condition and submits them for physician approval.
>
> 📊 **Test Result Analysis:** Compares results against normal reference ranges and interprets them accordingly.
>
> 💬 **AI-Assisted Interpretation:** Simplifies and summarizes all medical data into clear, understandable reports.
>
> 🌐 **Web-Based Interface:** User-friendly input and output panels designed for both patients and healthcare professionals.
>
> 📁 **Database and Knowledge Mapping:** Includes disease–test associations and reference value tables for clinical accuracy.

## Target Audience

* #### *Medical School Students* 
* #### *Family Physicians and Internal Medicine Specialists* 
* #### *Medical Secretaries and Allied Health Personnel* 
* #### *Healthcare Technology Developers* 
* #### *Curious Patients and Health-Conscious Individuals*