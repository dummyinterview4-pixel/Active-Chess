import json
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(tags=['syllabus'])

DATA_FILE = Path(__file__).resolve().parents[1] / 'data' / 'syllabus_tracks.json'


@lru_cache
def _load_tracks() -> list:
    """
    Migrated from V16's src/data/syllabusData.js (syllabusTracks). Purely
    descriptive marketing/curriculum-overview content shown on the Syllabus
    page — distinct from the DB-backed `Track`/`Course` learning hierarchy,
    so it lives as static data rather than rows to avoid implying these are
    enrollable in the same way published courses are.
    """
    with DATA_FILE.open('r', encoding='utf-8') as fh:
        return json.load(fh)


@router.get('/syllabus-tracks')
def get_syllabus_tracks():
    return _load_tracks()
