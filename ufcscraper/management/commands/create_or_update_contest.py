import requests
import firebase_admin
from firebase_admin import credentials, firestore
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set a document in Firestore"

    def add_arguments(self, parser):
        parser.add_argument(
            "project_id", type=str, help="The Firebase project ID", default="redegg"
        )
        parser.add_argument(
            "number", type=int, help="Last x event to update in firebase", default=1
        )

    def handle(self, *args, **kwargs):
        project_id = kwargs["project_id"]
        number = kwargs["number"]
        self.stdout.write(
            self.style.NOTICE(
                f"Creating/Updating last {number} contests for {project_id}"
            )
        )
        # Use a service account.
        cred = credentials.Certificate("service-account.json")
        options = {"projectId": project_id}
        app = firebase_admin.initialize_app(cred, options)
        db = firestore.client()
        try:
            # Fetch the upcoming event.
            if number == 1:
                response = requests.get("http://localhost:8000/events/?upcoming=true")
            else:
                response = requests.get(f"http://localhost:8000/events/")
            response.raise_for_status()  # Raise an exception if the request was unsuccessful.
            events = response.json()["results"][:number]

            for event in events:
                # Fetch the fights for the event.
                response = requests.get(
                    f'http://localhost:8000/fights/?event_id={event["id"]}'
                )
                response.raise_for_status()  # Raise an exception if the request was unsuccessful.
                fights = response.json()["results"]

                # Add the fights to the event.
                event["fights"] = fights

                # Set contest status
                if event["upcoming"]:
                    event["status"] = "open"
                elif event["completed"]:
                    event["status"] = "finished"
                else:
                    event["status"] = "live"

                # Set the document in Firestore.
                doc_ref = db.collection("contests").document(str(event["event_id"]))
                doc_ref.set(event)

                self.stdout.write(
                    self.style.SUCCESS("Successfully set document in Firestore")
                )
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(
                    f"An error occurred while fetching data from the API: {e}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
