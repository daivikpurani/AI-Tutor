"""
Materials API endpoints for uploading course materials.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from app.db.session import get_db
from app.models import Material, Section
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store_service
from app.utils.file_handler import file_handler
from app.models.material import MaterialType


router = APIRouter()


@router.post("/upload")
async def upload_material(
    file: UploadFile = File(...),
    section_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    material_type: str = Form("pdf"),
    db: Session = Depends(get_db)
):
    """
    Upload course material (professor's study materials).
    
    This endpoint:
    1. Saves the file to disk
    2. Extracts text and creates chunks
    3. Stores chunks in section's vector store (ChromaDB)
    4. Creates database record
    """
    try:
        logger.info(f"Uploading material: {file.filename} for section {section_id}")
        
        # Validate section exists
        section = db.query(Section).filter(Section.id == section_id).first()
        if not section:
            raise HTTPException(status_code=404, detail=f"Section {section_id} not found")
        
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        file_content = await file.read()
        
        # Save file to disk
        file_path, saved_filename, file_size = file_handler.save_material(
            file_content=file_content,
            filename=file.filename,
            section_id=section_id
        )
        
        # Process PDF: extract text and create chunks
        processing_result = document_processor.process_pdf_bytes(
            pdf_bytes=file_content,
            filename=file.filename,
            metadata={
                "section_id": section_id,
                "title": title,
                "material_type": material_type
            }
        )
        
        # Create material record first (to get ID)
        material = Material(
            section_id=section_id,
            title=title,
            description=description,
            material_type=MaterialType(material_type.lower()),
            file_name=saved_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file_handler.get_mime_type(file.filename),
            is_indexed=0,  # Not yet indexed
            chunk_count=0
        )
        
        db.add(material)
        db.flush()  # Get the ID
        
        # Store in vector store
        vector_store_collection_id = section.vector_store_collection_id
        if not vector_store_collection_id:
            # Generate collection ID if not exists
            vector_store_collection_id = f"section_{section_id}_materials"
            section.vector_store_collection_id = vector_store_collection_id
        
        document_ids = vector_store_service.add_documents(
            collection_name=vector_store_collection_id,
            chunks=processing_result['chunks'],
            material_id=material.id,
            section_id=section_id
        )
        
        # Update material record
        material.vector_store_document_ids = str(document_ids)  # Store as JSON string
        material.is_indexed = 1
        material.chunk_count = len(processing_result['chunks'])
        
        db.commit()
        db.refresh(material)
        
        logger.info(f"Material uploaded successfully: {material.id}")
        
        return {
            "success": True,
            "message": "Material uploaded and indexed successfully",
            "material": {
                "id": material.id,
                "title": material.title,
                "file_name": material.file_name,
                "section_id": section_id,
                "statistics": processing_result['statistics'],
                "vector_store_collection": vector_store_collection_id,
                "is_indexed": True
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Error uploading material")
        raise HTTPException(status_code=500, detail=f"Error uploading material: {type(e).__name__}: {str(e)[:300]}")


@router.get("/section/{section_id}")
async def list_materials(section_id: int, db: Session = Depends(get_db)):
    """
    List all materials for a section.
    """
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail=f"Section {section_id} not found")
    
    materials = db.query(Material).filter(Material.section_id == section_id).all()
    
    return {
        "section_id": section_id,
        "section_code": section.section_code,
        "total_materials": len(materials),
        "materials": [
            {
                "id": m.id,
                "title": m.title,
                "file_name": m.file_name,
                "material_type": m.material_type.value,
                "file_size": m.file_size,
                "chunk_count": m.chunk_count,
                "is_indexed": bool(m.is_indexed),
                "created_at": m.created_at
            }
            for m in materials
        ]
    }


@router.get("/vector-store/stats/{section_id}")
async def get_vector_store_stats(section_id: int, db: Session = Depends(get_db)):
    """
    Get vector store statistics for a section.
    """
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail=f"Section {section_id} not found")
    
    if not section.vector_store_collection_id:
        return {
            "section_id": section_id,
            "vector_store_collection": None,
            "document_count": 0,
            "message": "No vector store collection created yet"
        }
    
    stats = vector_store_service.get_collection_stats(section.vector_store_collection_id)
    
    return {
        "section_id": section_id,
        "section_code": section.section_code,
        "vector_store_collection": section.vector_store_collection_id,
        **stats
    }
