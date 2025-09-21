# Lead Scoring System

## 🚀 Project Overview
This project is a backend service designed to qualify leads by scoring them based on product/offer information and prospect data. The scoring pipeline uses a hybrid approach combining a rule-based logic with AI reasoning to determine each lead's buying intent.

---

## 🎯 Objective

The primary goal of this service is to accept product offer details via a JSON payload and lead data through a CSV file. It then processes and scores each lead, assigning a final score (0-100) and an intent label (High, Medium, or Low) along with reasoning.

---

## ✨ Features

* **API Endpoints:** Implemented clean and well-documented REST APIs for data input, scoring, and retrieval.
* **Rule-Based Scoring:** A rule layer calculates a score of up to 50 points based on predefined criteria, including role relevance, industry match, and data completeness.
* **AI Reasoning:** An AI layer adds up to 50 points based on its analysis of the lead's profile and the offer's value propositions, providing a contextual reasoning for the score and a final intent classification.
* **Results APIs:** Provides an endpoint to retrieve scored leads as a JSON array and an optional endpoint to export the results as a CSV file.

---

## 💻 Technologies Used

* **Backend Framework:** Django & Django REST Framework
* **AI Integration:** Gemini AI
* **Database:** SQLite3 

---

## ⚙️ Setup Instructions

Follow these steps to set up and run the project locally.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Sufail07/Lead-Scoring-System.git
    cd Lead-Scoring-System
    ```
2.  **Create and Activate a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Database Migration:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5.  **Environment Variables:** Create a `.env` file in the project root with your Gemini API key.
    ```
    # .env
    GEMINI_API_KEY=your_ai_api_key_here
    ```
6.  **Run the Server:**
    ```bash
    python manage.py runserver
    ```

---

## 🔗 API Usage Examples

The following examples demonstrate how to interact with the API endpoints.

### **1. `POST /offer`**

This endpoint accepts a JSON payload with product details to be used for scoring.

* **Endpoint:** `/api/offer/`
* **Method:** `POST`
* **Request Body (JSON):**
    ```json
    {
      "name": "Cloud Data Analytics Platform",
      "value_props": [
        "Real-time insights",
        "Scalable data processing",
        "Cost optimization"
      ],
      "ideal_use_cases": [
        "Enterprise data teams",
        "Fintech startups",
        "E-commerce analytics"
      ]
    }
    ```

### **2. `POST /leads/upload/<int:offer_id>`**

This endpoint accepts a CSV file of leads, associated with an offer, to be uploaded to the database.

* **Endpoint:** `/api/leads/upload/<int:offer_id>`
* **Method:** `POST`
* **Request Body (Multipart Form Data):**
    `file`: A CSV file with the required lead data columns.
  **Required CSV Fields:**
```csv
role,company,industry,location,linkedin_bio
```

### **3. `POST /score`**

This endpoint triggers the scoring pipeline for all leads associated with a specific offer along with an offer_id integer.

* **Endpoint:** `/api/score/<int:offer_id>/`
* **Method:** `POST`

### **4. `GET /results`**

This endpoint returns a JSON array of the scored leads.

* **Endpoint:** `/api/results/`
* **Method:** `GET`

### **5. `GET /export`**

This endpoint returns a link to download CSV file of the scored leads.

* **Endpoint:** `/api/export/`
* **Method:** `GET`

---

## 🧠 Scoring Logic Explained

The lead scoring system employs a two-layer approach for a comprehensive evaluation:

* **Rule Layer (Max 50 points):** This layer uses predefined rules to assign a score based on a lead's attributes.
    * **Role Relevance:** `Decision Maker` (+20 points), `Influencer` (+10 points), `Else` (0 points).
    * **Industry Match:** `Exact Ideal Customer Profile (ICP)` (+20 points), `Adjacent` (+10 points), `Else` (0 points).
    * **Data Completeness:** `All Fields Present` (+10 points).

* **AI Layer (Max 50 points):** The system sends the lead and offer details to an AI model with a prompt asking for an intent classification and a short reasoning. The AI's response is mapped to points: `High` (50 points), `Medium` (30 points), `Low` (10 points).

**Final Score = Rule Layer Score + AI Layer Score**.

---

## 📖 API Documentation

The API documentation is generated and served using [drf-spectacular](https://drf-spectacular.readthedocs.io/):

- **SpectacularAPIView**: Provides the OpenAPI schema for the API.
- **SpectacularSwaggerView**: Serves an interactive Swagger UI for exploring and testing the API endpoints.

You can view and interact with the API documentation directly via the Swagger UI endpoint (`/api/schema/swagger-ui/`).

---
