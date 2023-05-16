from fastapi import APIRouter

import server.schemas.ie as ie_schema

import server.ner as ner
import server.qa as qa


router = APIRouter(
    prefix="/v1/ie",
    tags=["v1/ie"],
)

@router.post("/", response_model=ie_schema.ExtractedInformation)
async def information_extraction(mail: ie_schema.Mail):
    body_text = mail.body_text
    model = mail.model
    if model == "ner":
        outputs = ner.ner(body_text)
    elif model == "qa":
        outputs = qa.qa(body_text)
    return ie_schema.ExtractedInformation(
        event=outputs['event'],
        startingDateTime=outputs['startingDateTime'],
        endingDateTime=outputs['endingDateTime'],
        location=outputs['location'],
        person=outputs['person'],
    )
