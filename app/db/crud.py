from typing import Union, List, Type, Optional, Any

from . import SessionLocal
from .models import *


ModelInstances = Union[Source, Document, AnalysisResult, BlacklistedSource]
ModelTypes = Union[Type[Source], Type[Document], Type[AnalysisResult], Type[BlacklistedSource]]


def get_db() -> SessionLocal:
    """
    Возвращает объект для работы с БД

    Returns:
        Объект для работы с БД
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_entry_by_id(entry_id: int,
                    model: ModelTypes,
                    db: Optional[SessionLocal] = None) -> Union[ModelInstances, None]:
    """
    Возвращает запись из БД по id

    Args:
        entry_id: id записи, которую нужно получить
        model: класс модели записи, которую нужно получить
        db (optional): объект для работы с БД
    Returns:
        Найденную запись из БД; если не найдено, то None
    """
    if db is None:
        db = next(get_db())

    entry = db.query(model
                        ).filter(model.id == entry_id
                                 ).first()

    return entry


def update_entry_by_id(entry_id: int,
                       new_entry: ModelInstances,
                       db: Optional[SessionLocal] = None) -> Union[ModelInstances, None]:
    """
    Обновляет запись в БД по id

    Args:
        entry_id: id записи, которую нужно обновить
        new_entry: запись с заполненными полями, которые нужно обновить
        db (optional): объект для работы с БД
    Returns:
        Обновленную запись из БД; если не найдена исходная запись, то None
    """
    if db is None:
        db = next(get_db())

    existing_entry = get_entry_by_id(entry_id, new_entry.__class__, db)

    if existing_entry is None:
        return None

    for column in (attr for attr in vars(new_entry) if not attr.startswith('_')):
        setattr(existing_entry, column, getattr(new_entry, column))

    db.commit()
    db.refresh(existing_entry)

    return existing_entry


def add_entries(*entries: List[ModelInstances],
                db: Optional[SessionLocal] = None) -> Union[List[ModelInstances], ModelInstances, Any]:
    """
    Добавляет записи в БД

    Args:
        *entries: записи, которые нужно добавить
        db (optional): объект для работы с БД
    Returns:
        Список добавленных записей, если их несколько; Добавленную запись, если она одна
    """
    if db is None:
        db = next(get_db())

    db.add_all(entries)
    db.commit()

    for entry in entries:
        db.refresh(entry)

    if len(entries) == 1:
        return entries[0]
    else:
        return entries
