import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Company
from scraper import scrape_company
from analyzer import enrich_company


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Company Enricher API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Company Enricher API is running"
    }


# -----------------------------
# POST /enrich
# -----------------------------
@app.post("/enrich")
def enrich(data: dict):

    website = data.get("website")

    if not website:
        return {
            "error": "Website URL is required"
        }

    # Scrape Website
    scraped_data = scrape_company(website)

    if not scraped_data:
        return {
            "error": "Unable to scrape website"
        }

    # AI Enrichment
    ai_result = enrich_company(scraped_data)

    # Merge Results
    final_result = {
        **scraped_data,
        **ai_result
    }

    # Save to DB
    db: Session = SessionLocal()

    company = Company(
        website_name=final_result.get("website_name", ""),
        company_name=final_result.get("company_name", ""),
        address=final_result.get("address", ""),
        mobile_number=final_result.get("mobile_number", ""),
        mail=json.dumps(final_result.get("mail", [])),
        core_service=final_result.get("core_service", ""),
        target_customer=final_result.get("target_customer", ""),
        probable_pain_point=final_result.get("probable_pain_point", ""),
        outreach_opener=final_result.get("outreach_opener", ""),
    )

    db.add(company)
    db.commit()
    db.close()

    return final_result


# -----------------------------
# GET /results
# -----------------------------
@app.get("/results")
def results():

    db: Session = SessionLocal()

    companies = db.query(Company).all()

    output = []

    for company in companies:

        output.append({

            "website_name": company.website_name,
            "company_name": company.company_name,
            "address": company.address,
            "mobile_number": company.mobile_number,

            # Convert JSON string back to list
            "mail": json.loads(company.mail)
            if company.mail else [],

            "core_service": company.core_service,
            "target_customer": company.target_customer,
            "probable_pain_point": company.probable_pain_point,
            "outreach_opener": company.outreach_opener,

        })

    db.close()

    return output