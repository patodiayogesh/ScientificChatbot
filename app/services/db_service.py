import logging
import firebase_admin
from firebase_admin import credentials, firestore

from app.settings import get_settings
from app.services.recipe import (
    PdfInformationRecipe,
)

settings = get_settings()
logger = logging.getLogger(__name__)


class DatabaseService:

    def __init__(self):
        self.db = get_firebase_db()
        self.collection_name = settings.FIREBASE_COLLECTION_NAME


    def add_documents(self, documents: list[PdfInformationRecipe]):
        """
        Add multiple documents to the Firestore collection.

        :param documents: List of dictionaries representing the documents to be added.
        """
        try:

            if not documents:
                raise ValueError("No documents provided to add to the database.")

            batch = self.db.batch()
            collection_ref = self.db.collection(self.collection_name)
            for document in documents:
                doc_ref = collection_ref.document(document.title)
                batch.set(doc_ref, document.model_dump())
            batch.commit()

            logger.info(f"Successfully added {len(documents)} documents to the database.")
        except Exception as e:
            raise ValueError(f"Error adding documents to the database: {e}")


def get_firebase_db():
    """
    Function to set up credentials to connect to firebase db
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
        firebase_admin.initialize_app(cred)
    return firestore.client()
