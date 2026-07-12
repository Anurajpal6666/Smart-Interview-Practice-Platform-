import csv
from app import app, db, Problem

def data(filepath):
    with app.app_context():

        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:

                obj = Problem(
                    frontendQuestionId=row["frontendQuestionId"],
                    title=row["title"],
                    topicTags=row["topicTags"],
                    difficulty=row["difficulty"],
                    acRate=float(row["acRate"]),
                    isFavor=row["isFavor"].strip().lower() == "true",
                    paidOnly=row["paidOnly"].strip().lower() == "true"
                )

                db.session.add(obj)

            db.session.commit()

    print("Data imported successfully!")


if __name__ == "__main__":
    data("data.csv")