"""
Demo document generator.

Produces the sample PDFs used by the demo seed script (demo/seed.ts) so the
knowledge base has realistic, citeable content for a walkthrough. Run with:

    cd apps/api && .venv/bin/python ../../demo/generate_documents.py

Output is written to demo/documents/. Safe to re-run — files are overwritten.
"""

import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "documents")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Title"],
            fontSize=20,
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading",
            parent=styles["Heading2"],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontSize=11,
            leading=16,
            spaceAfter=8,
        )
    )
    return styles


def _build(filename: str, flowables) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        title=filename,
    )
    doc.build(flowables)
    print(f"Created {path}")


def rental_contract(styles) -> None:
    s = styles
    story = [
        Paragraph("Residential Tenancy Agreement", s["DocTitle"]),
        Paragraph("1. Parties", s["Heading"]),
        Paragraph(
            "This agreement is made between the Landlord, Acme Property "
            "Holdings Pty Ltd, and the Tenant, the individual named in the "
            "signature block below. The two parties agree to the terms set out "
            "in this document for the rental of the premises.",
            s["Body"],
        ),
        Paragraph("2. Premises", s["Heading"]),
        Paragraph(
            "The premises let under this agreement is the apartment located at "
            "42 Riverside Avenue, Unit 7, including one allocated parking space "
            "and access to shared building facilities.",
            s["Body"],
        ),
        Paragraph("3. Rent", s["Heading"]),
        Paragraph(
            "The Tenant shall pay rent of $2,400 per calendar month, due in "
            "advance on the first day of each month. Rent is to be paid by bank "
            "transfer to the Landlord's nominated account. A late fee of $50 "
            "applies if rent is more than five days overdue.",
            s["Body"],
        ),
        Paragraph("4. Security Bond", s["Heading"]),
        Paragraph(
            "The Tenant shall pay a security bond equal to four weeks' rent "
            "($2,215) before taking occupancy. The bond is lodged with the "
            "relevant tenancy authority and is refundable at the end of the "
            "tenancy, less any deductions for damage beyond fair wear and tear "
            "or unpaid rent.",
            s["Body"],
        ),
        PageBreak(),
        Paragraph("5. Termination", s["Heading"]),
        Paragraph(
            "Either party may terminate this agreement by providing not less "
            "than 30 days' written notice. If the Tenant vacates before the end "
            "of a fixed term without agreement, they may be liable for "
            "reasonable re-letting costs. The Landlord may terminate "
            "immediately for serious breaches, including non-payment of rent "
            "for 14 consecutive days.",
            s["Body"],
        ),
        Paragraph("6. Maintenance and Repairs", s["Heading"]),
        Paragraph(
            "The Landlord is responsible for maintaining the premises in a "
            "reasonable state of repair, including structural elements, "
            "plumbing, and electrical systems. The Tenant must report any "
            "maintenance issues promptly and is responsible for minor upkeep "
            "such as replacing light bulbs and keeping the premises clean. "
            "Urgent repairs affecting safety will be addressed within 24 hours "
            "of being reported.",
            s["Body"],
        ),
        Paragraph("7. Use of Premises", s["Heading"]),
        Paragraph(
            "The premises shall be used solely as a private residence. "
            "Subletting is not permitted without the Landlord's prior written "
            "consent. The Tenant shall not cause a nuisance to neighbours.",
            s["Body"],
        ),
        Spacer(1, 24),
        Paragraph("Signed by Tenant: ______________________", s["Body"]),
        Paragraph("Signed by Landlord: ______________________", s["Body"]),
    ]
    _build("rental-contract.pdf", story)


def fastapi_notes(styles) -> None:
    s = styles
    story = [
        Paragraph("FastAPI Study Notes", s["DocTitle"]),
        Paragraph("What FastAPI Is", s["Heading"]),
        Paragraph(
            "FastAPI is a modern, high-performance Python web framework for "
            "building APIs. It is built on top of Starlette for the web parts "
            "and Pydantic for data validation. Its headline features are "
            "automatic interactive documentation, native async support, and "
            "type-hint-driven validation that reduces boilerplate.",
            s["Body"],
        ),
        Paragraph("Route Decorators", s["Heading"]),
        Paragraph(
            "Endpoints are declared with decorators on an APIRouter or the app "
            "instance, such as @app.get(\"/items\") or @router.post(\"/items\"). "
            "The decorated function's parameters and return type annotations "
            "define how the request is parsed and how the response is "
            "serialized. Path and query parameters are inferred from the "
            "function signature.",
            s["Body"],
        ),
        Paragraph("Dependency Injection", s["Heading"]),
        Paragraph(
            "FastAPI provides a powerful dependency injection system via the "
            "Depends() helper. Dependencies are plain callables that can supply "
            "shared resources such as a database session, the current user, or "
            "configuration. They are resolved per request and can themselves "
            "depend on other dependencies, forming a clean, testable graph.",
            s["Body"],
        ),
        PageBreak(),
        Paragraph("Pydantic Models", s["Heading"]),
        Paragraph(
            "Request and response bodies are described with Pydantic models. "
            "FastAPI uses these models to validate incoming JSON, coerce types, "
            "and produce clear validation errors automatically. The same models "
            "drive the generated OpenAPI schema, keeping documentation in sync "
            "with the code.",
            s["Body"],
        ),
        Paragraph("Async Support", s["Heading"]),
        Paragraph(
            "Route handlers can be defined with async def, allowing the use of "
            "await for non-blocking I/O such as database queries or external "
            "HTTP calls. Because FastAPI runs on an ASGI server like Uvicorn, "
            "async handlers let a single worker serve many concurrent requests "
            "efficiently. Synchronous handlers are still supported and are run "
            "in a thread pool.",
            s["Body"],
        ),
        PageBreak(),
        Paragraph("Validation and Errors", s["Heading"]),
        Paragraph(
            "When validation fails, FastAPI returns a 422 response with a "
            "structured list of the offending fields. Application code can "
            "raise HTTPException to return specific status codes and detail "
            "messages, which is the idiomatic way to surface business errors "
            "such as 404 Not Found or 429 Too Many Requests.",
            s["Body"],
        ),
        Paragraph("Why It Suits This Project", s["Heading"]),
        Paragraph(
            "MiniGlean uses FastAPI for its async database access (SQLAlchemy "
            "with asyncpg), its streaming responses for the chat endpoint, and "
            "the automatic documentation that makes the API easy to explore "
            "during development.",
            s["Body"],
        ),
    ]
    _build("fastapi-notes.pdf", story)


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    styles = _styles()
    rental_contract(styles)
    fastapi_notes(styles)


if __name__ == "__main__":
    main()
