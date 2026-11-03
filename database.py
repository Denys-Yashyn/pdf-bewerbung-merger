import enum, os
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

# Umgebungsvariablen aus der .env-Datei laden
load_dotenv()

# Basisklasse, von der unsere Tabellen erben
Base = declarative_base()

# 1. Python-Äquivalent zum PostgreSQL ENUM
class ApplicationStatus(enum.Enum):
    PLANNED = 'PLANNED'
    APPLIED = 'APPLIED'
    INTERVIEW = 'INTERVIEW'
    REJECTED = 'REJECTED'
    OFFER = 'OFFER'

# 2. Unternehmensmodell (entspricht der Tabelle 'companies')
class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    city = Column(String(100))
    website = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Bidirektionale Beziehung (Ein Unternehmen -> Viele Bewerbungen)
    applications = relationship("Application", back_populates="company", cascade="all, delete-orphan")

    # Magische Methode für eine saubere Konsolenausgabe (z. B. <Company(name='Telekom', city='Erfurt')>)
    def __repr__(self):
        return f"<Company(name='{self.name}', city='{self.city}')>"

# 3. Bewerbungsmodell (entspricht der Tabelle 'applications')
class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    position_title = Column(String(255), nullable=False)
    
    # Verwendet das erstellte Enum
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    applied_date = Column(Date, default=date.today)
    document_path = Column(Text)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Rückbeziehung zur Company-Klasse
    company = relationship("Company", back_populates="applications")

    def __repr__(self):
        return f"<Application(position='{self.position_title}', status='{self.status.name}')>"

# Verbindungsdaten abrufen
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Verbindungszeichenfolge (Connection String) erstellen
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Engine erstellen – verantwortlich für die physische Verbindung zu PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session-Fabrik erstellen (SessionLocal) – darüber senden wir unsere Datenbankabfragen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Session-Generator. 
    Öffnet eine Datenbankverbindung und schließt sie GARANTIERT 
    nach Abschluss der Operation (selbst bei Fehlern), um die Datenbank nicht zu blockieren.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_application_to_db(company_name: str, position_title: str, pdf_path: str):
    """Speichert die generierte Bewerbung in der PostgreSQL-Datenbank."""
    # Session aus dem Generator abrufen
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # 1. Unternehmen in der Datenbank suchen
        company = db.query(Company).filter(Company.name == company_name).first()
        
        # Falls das Unternehmen noch nicht existiert, ein neues anlegen
        if not company:
            company = Company(name=company_name)
            db.add(company)
            db.commit()
            db.refresh(company) # Objekt aktualisieren, um die generierte ID zu erhalten
        
        # 2. Bewerbungsdatensatz erstellen (Application)
        new_application = Application(
            company_id=company.id,
            position_title=position_title,
            document_path=str(pdf_path)
        )
        
        db.add(new_application)
        db.commit()
        print(f"💾 Erfolgreich in der Datenbank gespeichert: {position_title} bei {company_name}")
        
    except Exception as e:
        db.rollback() # Transaktion im Fehlerfall rückgängig machen (Rollback), um die DB zu schützen
        print(f"⚠️ Datenbankfehler: {e}")
    finally:
        db.close()
