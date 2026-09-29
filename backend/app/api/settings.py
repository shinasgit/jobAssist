import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
from app.schemas.setting import SettingUpdate, SettingResponse

router = APIRouter()

DEFAULT_KEYWORDS = ["Junior AI Developer"]
DEFAULT_LOCATIONS = ["Bangalore"]
DEFAULT_EXPERIENCE = "Fresher"
DEFAULT_REMOTE = "any"
DEFAULT_EMPLOYMENT = ["Full-time"]
DEFAULT_SOURCES = ["himalayas", "remotive", "arbeitnow", "greenhouse", "lever", "ashby", "workable", "recruitee", "breezy"]

def _db_to_response(setting_obj: models.Setting) -> dict:
    def parse_json_list(val, default):
        if not val:
            return default
        try:
            res = json.loads(val)
            return res if isinstance(res, list) else default
        except Exception:
            return [x.strip() for x in val.split(",") if x.strip()]

    return {
        "id": setting_obj.id,
        "keywords": parse_json_list(setting_obj.keywords, DEFAULT_KEYWORDS),
        "locations": parse_json_list(setting_obj.locations, DEFAULT_LOCATIONS),
        "experience": setting_obj.experience or DEFAULT_EXPERIENCE,
        "remote_type": setting_obj.remote_type or DEFAULT_REMOTE,
        "employment_types": parse_json_list(setting_obj.employment_types, DEFAULT_EMPLOYMENT),
        "enabled_sources": parse_json_list(setting_obj.enabled_sources, DEFAULT_SOURCES)
    }

@router.get("", response_model=SettingResponse)
def get_settings(db: Session = Depends(get_db)):
    setting_obj = db.query(models.Setting).first()
    if not setting_obj:
        setting_obj = models.Setting(
            keywords=json.dumps(DEFAULT_KEYWORDS),
            locations=json.dumps(DEFAULT_LOCATIONS),
            experience=DEFAULT_EXPERIENCE,
            remote_type=DEFAULT_REMOTE,
            employment_types=json.dumps(DEFAULT_EMPLOYMENT),
            enabled_sources=json.dumps(DEFAULT_SOURCES)
        )
        db.add(setting_obj)
        db.commit()
        db.refresh(setting_obj)

    return _db_to_response(setting_obj)

@router.put("", response_model=SettingResponse)
def update_settings(body: SettingUpdate, db: Session = Depends(get_db)):
    setting_obj = db.query(models.Setting).first()
    if not setting_obj:
        setting_obj = models.Setting()
        db.add(setting_obj)

    if body.keywords is not None:
        cleaned_kw = list(dict.fromkeys([k.strip() for k in body.keywords if k.strip()]))
        setting_obj.keywords = json.dumps(cleaned_kw)
    if body.locations is not None:
        cleaned_loc = list(dict.fromkeys([l.strip() for l in body.locations if l.strip()]))
        setting_obj.locations = json.dumps(cleaned_loc)
    if body.experience is not None:
        setting_obj.experience = body.experience
    if body.remote_type is not None:
        setting_obj.remote_type = body.remote_type
    if body.employment_types is not None:
        cleaned_emp = list(dict.fromkeys([e.strip() for e in body.employment_types if e.strip()]))
        setting_obj.employment_types = json.dumps(cleaned_emp)
    if body.enabled_sources is not None:
        cleaned_src = list(dict.fromkeys([s.strip().lower() for s in body.enabled_sources if s.strip()]))
        setting_obj.enabled_sources = json.dumps(cleaned_src)

    db.commit()
    db.refresh(setting_obj)
    return _db_to_response(setting_obj)
