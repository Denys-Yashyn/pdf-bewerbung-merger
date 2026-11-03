import enum, os
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Базовый класс, от которого будут наследоваться наши таблицы
Base = declarative_base()

# 1. Python-эквивалент твоего ENUM из PostgreSQL
class ApplicationStatus(enum.Enum):
    PLANNED = 'PLANNED'
    APPLIED = 'APPLIED'
    INTERVIEW = 'INTERVIEW'
    REJECTED = 'REJECTED'
    OFFER = 'OFFER'

# 2. Модель компании (соответствует таблице companies)
class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    city = Column(String(100))
    website = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Двусторонняя связь (одна компания -> много откликов)
    applications = relationship("Application", back_populates="company", cascade="all, delete-orphan")

    # Магический метод для красивого вывода при принте (например: <Company(name='Telekom', city='Erfurt')>)
    def __repr__(self):
        return f"<Company(name='{self.name}', city='{self.city}')>"

# 3. Модель отклика (соответствует таблице applications)
class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    position_title = Column(String(255), nullable=False)
    
    # Используем созданный Enum
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    applied_date = Column(Date, default=date.today)
    document_path = Column(Text)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Обратная связь с классом Company
    company = relationship("Company", back_populates="applications")

    def __repr__(self):
        return f"<Application(position='{self.position_title}', status='{self.status.name}')>"

load_dotenv()

# Достаем данные для подключения (с дефолтными значениями на крайний случай)
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Формируем строку подключения (Connection String)
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем 'движок' (engine) — он отвечает за физическое соединение с PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий (SessionLocal) — через нее мы будем отправлять запросы
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Генератор сессий. 
    Он аккуратно открывает соединение с базой и ГАРАНТИРОВАННО закрывает его 
    после завершения операции (даже если произойдет ошибка), чтобы не "повесить" базу.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_application_to_db(company_name: str, position_title: str, pdf_path: str):
    """Сохраняет сгенерированный бевербунг в базу данных PostgreSQL."""
    # Получаем сессию из генератора
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # 1. Ищем компанию в базе
        company = db.query(Company).filter(Company.name == company_name).first()
        
        # Если компании еще нет, создаем новую
        if not company:
            company = Company(name=company_name)
            db.add(company)
            db.commit()
            db.refresh(company) # Обновляем объект, чтобы получить его сгенерированный ID
        
        # 2. Создаем запись об отклике (Application)
        new_application = Application(
            company_id=company.id,
            position_title=position_title,
            document_path=str(pdf_path)
        )
        
        db.add(new_application)
        db.commit()
        print(f"💾 Erfolgreich in der Datenbank gespeichert: {position_title} bei {company_name}")
        
    except Exception as e:
        db.rollback() # Откатываем транзакцию в случае ошибки, чтобы не сломать базу
        print(f"⚠️ Datenbankfehler: {e}")
    finally:
        db.close()