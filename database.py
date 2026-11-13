import enum, os
from datetime import datetime, date
from sqlalchemy import create_engine, func, Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
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
    website = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Bidirektionale Beziehung (Ein Unternehmen -> Viele Bewerbungen)
    applications = relationship("Application", back_populates="company", cascade="all, delete-orphan")

    # Magische Methode für eine saubere Konsolenausgabe (z. B. <Company(name='Telekom')>)
    def __repr__(self):
        return f"<Company(name='{self.name}')>"

# 3. Bewerbungsmodell (entspricht der Tabelle 'applications')
class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    position_title = Column(String(255), nullable=False)
    city = Column(String(100))
    
    # Verwendet das erstellte Enum
    status = Column(Enum(ApplicationStatus, name="application_status"), default=ApplicationStatus.APPLIED)
    applied_date = Column(Date, default=date.today)
    document_path = Column(Text)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Rückbeziehung zur Company-Klasse
    company = relationship("Company", back_populates="applications")

    def __repr__(self):
        return f"<Application(position='{self.position_title}', city='{self.city}', status='{self.status.name}')>"

# Verbindungs-URL aus der .env erstellen (URL.create maskiert Sonderzeichen im Passwort)
SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT") or 5432),
    database=os.getenv("DB_NAME"),
)

# Engine erstellen – verantwortlich für die physische Verbindung zu PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session-Fabrik erstellen (SessionLocal) – darüber senden wir unsere Datenbankabfragen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def save_application_to_db(company_name: str, position_title: str, pdf_path: str, city: str = "", notes: str = "") -> None:
    """Speichert die generierte Bewerbung in der PostgreSQL-Datenbank.

    Ein vorhandenes Unternehmen wird wiederverwendet. Existiert bereits eine Bewerbung
    mit gleichem Unternehmen, Ort und Position, wird sie aktualisiert statt doppelt angelegt.
    """
    try:
        # Tabellen beim ersten Start anlegen (vorhandene Tabellen bleiben unverändert)
        Base.metadata.create_all(engine)

        with SessionLocal() as db:
            company = db.query(Company).filter(Company.name == company_name).first()
            if not company:
                company = Company(name=company_name)
                db.add(company)

            application = None
            if company.id is not None:
                application = db.query(Application).filter(
                    Application.company_id == company.id,
                    Application.position_title == position_title,
                    func.coalesce(Application.city, "") == city,
                ).order_by(Application.id.desc()).first()

            if application:
                application.document_path = str(pdf_path)
                if notes:
                    application.notes = notes
                action = "aktualisiert"
            else:
                db.add(Application(
                    company=company,
                    city=city or None,
                    position_title=position_title,
                    document_path=str(pdf_path),
                    notes=notes or None,
                ))
                action = "gespeichert"
            db.commit()
        print(f"💾 Erfolgreich in der Datenbank {action}: {position_title} bei {company_name}")
    except SQLAlchemyError as e:
        print(f"⚠️ Datenbankfehler: {e}")
