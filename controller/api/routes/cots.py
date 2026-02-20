from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from shared.cots.database.models import COTSItemORM

# Initialize router
router = APIRouter(prefix="/cots", tags=["cots"])

# Database setup
# Using sync engine for SQLite since we don't have aiosqlite easily available.
# FastAPI will run this in a threadpool.
DB_PATH = "parts.db"

# Initialize database with test data if it doesn't exist
import os
if not os.path.exists(DB_PATH):
    import json
    
    engine = create_engine(
        f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, echo=False
    )
    
    # Create tables
    from shared.cots.database.models import Base
    Base.metadata.create_all(engine)
    
    # Insert test data
    with Session(engine) as session:
        test_data = [
            {
                'part_id': 'M3-16-SS',
                'name': 'M3 x 16mm Stainless Steel Screw',
                'category': 'fastener',
                'unit_cost': 0.15,
                'weight_g': 1.2,
                'metadata_dict': {
                    'manufacturer': 'Generic',
                    'material': 'stainless_steel',
                    'size': 'M3x16'
                }
            },
            {
                'part_id': 'M3-NUT-SS',
                'name': 'M3 Stainless Steel Nut',
                'category': 'fastener', 
                'unit_cost': 0.05,
                'weight_g': 0.8,
                'metadata_dict': {
                    'manufacturer': 'Generic',
                    'material': 'stainless_steel',
                    'size': 'M3'
                }
            },
            {
                'part_id': 'BEARING-608',
                'name': '608 Ball Bearing',
                'category': 'bearing',
                'unit_cost': 2.50,
                'weight_g': 8.5,
                'metadata_dict': {
                    'manufacturer': 'Generic',
                    'size': '608'
                }
            }
        ]
        
        for item in test_data:
            db_item = COTSItemORM(
                part_id=item['part_id'],
                name=item['name'],
                category=item['category'],
                unit_cost=item['unit_cost'],
                weight_g=item['weight_g'],
                metadata_dict=item['metadata_dict']
            )
            session.add(db_item)
        
        session.commit()
        print(f"✅ Created {DB_PATH} with test COTS data")

engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/search")
def search_cots(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """
    Search for COTS parts by name or category.
    """
    # SQLite LIKE is case-insensitive for ASCII characters by default
    stmt = (
        select(COTSItemORM)
        .where(
            (COTSItemORM.name.like(f"%{q}%")) | (COTSItemORM.category.like(f"%{q}%"))
        )
        .limit(limit)
    )

    results = db.scalars(stmt).all()

    response = []
    for item in results:
        # Map ORM object to response schema expected by tests/clients
        response.append(
            {
                "part_id": item.part_id,
                "name": item.name,
                "category": item.category,
                # Placeholder values as per schema requirements in tests
                "manufacturer": item.metadata_dict.get("manufacturer", "Generic"),
                "price": item.unit_cost,
                "source": "internal",
                "weight_g": item.weight_g,
                "metadata": item.metadata_dict,
            }
        )

    return response
