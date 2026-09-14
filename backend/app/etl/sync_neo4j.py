from app.db.database import SessionLocal
from app.services.graph_sync_service import GraphSyncService


def main():

    db = SessionLocal()

    try:

        service = GraphSyncService(db)

        result = service.sync_all()

        print("\nSYNC SUMMARY")
        print(result)

    finally:

        db.close()


if __name__ == "__main__":
    main()