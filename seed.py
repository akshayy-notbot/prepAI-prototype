from models import SessionLocal, Question, engine, Base

# This creates the 'questions' table based on our new model
print("Creating questions table...")
Base.metadata.create_all(bind=engine)
print("Table created.")

# A list of questions to add to the database
questions_to_add = [
    Question(
        question_text="How would you design a product to help people learn a new language?",
        role="Product Manager",
        seniority="Senior",
        skill_tags=["Product Design", "User Empathy"]
    ),
    Question(
        question_text="Tell me about a time you used data to influence a product decision.",
        role="Product Manager",
        seniority="Senior",
        skill_tags=["Metrics", "Execution"]
    ),
    Question(
        question_text="What are the key metrics you would track for a product like Instagram Stories?",
        role="Product Manager",
        seniority="Senior",
        skill_tags=["Metrics", "Product Sense"]
    ),
    Question(
        question_text="Your product's engagement suddenly drops by 15%. How would you investigate this?",
        role="Product Manager",
        seniority="Senior",
        skill_tags=["Execution", "Metrics", "Problem Solving"]
    ),
    Question(
        question_text="Walk me through the design of your favorite product.",
        role="Product Manager",
        seniority="Junior",
        skill_tags=["Product Sense"]
    ),
]

# Get a database session
db = SessionLocal()

print("Seeding database...")
try:
    # Add all the questions to the session
    for question in questions_to_add:
        db.add(question)

    # Commit the transaction to save them to the database
    db.commit()
    print("Successfully added questions to the database.")
except Exception as e:
    print(f"An error occurred: {e}")
    db.rollback()
finally:
    # Close the session
    db.close()