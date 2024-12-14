from app import db
from app.models.review import Review
import random
from datetime import datetime, timedelta

# Review components for mixing and matching
INTROS = [
    "Really impressed with",
    "So happy with",
    "Very satisfied with",
    "Couldn't be happier with",
    "Excellent experience with",
    "Great job on",
    "Fantastic work with",
    "Very pleased with",
    "Professional handling of",
    "Quick response for"
]

JOB_TYPES = [
    "Emergency Lockout",  # More common
    "Emergency Lockout",
    "Emergency Lockout",
    "Lock Change",
    "Lock Change",
    "Lock Repair",
    "Key Duplication",
    "Security Consultation",
    "Safe Installation",
    "Other"
]

SERVICE_DETAILS = {
    "Emergency Lockout": [
        "got me back in within minutes",
        "arrived super quickly when I was locked out",
        "helped me late at night with no hassle",
        "saved me when I was stuck outside",
        "came right away when I was locked out",
        "got me back into my apartment fast",
        "helped me during a stressful lockout",
        "responded quickly to my emergency"
    ],
    "Lock Change": [
        "replaced all my locks efficiently",
        "installed new secure locks",
        "upgraded my old locks",
        "changed my locks same day",
        "installed high-security locks",
        "replaced the broken lock quickly",
        "upgraded my security system",
        "installed new deadbolts"
    ],
    "Lock Repair": [
        "fixed my stuck lock",
        "repaired my broken deadbolt",
        "fixed the jammed lock",
        "got my old lock working again",
        "repaired the damaged lock",
        "fixed a tricky lock problem",
        "restored my lock to perfect condition",
        "solved the lock issue quickly"
    ],
    "Other": [
        "completed the job perfectly",
        "did exactly what was needed",
        "provided excellent service",
        "handled everything professionally",
        "took care of everything efficiently",
        "did a great job with my request",
        "solved my security needs",
        "provided expert assistance"
    ]
}

PROFESSIONALISM = [
    "Very professional and courteous.",
    "Explained everything clearly.",
    "Fair pricing and great service.",
    "Clean and efficient work.",
    "Friendly and knowledgeable.",
    "Trustworthy and reliable.",
    "Prompt and professional.",
    "Expert service at a fair price."
]

RECOMMENDATIONS = [
    "Highly recommend!",
    "Would definitely use again!",
    "Will be my go-to locksmith!",
    "5 stars all the way!",
    "Best locksmith in the area!",
    "Will recommend to everyone!",
    "Saved their number for future needs!",
    "The only locksmith I'll call!"
]

LOCATIONS = [
    "Manhattan, NY",
    "Upper East Side, NY",
    "Upper West Side, NY",
    "Midtown, NY",
    "Downtown Manhattan, NY",
    "Brooklyn Heights, NY",
    "Park Slope, Brooklyn",
    "Williamsburg, Brooklyn",
    "Astoria, Queens",
    "Long Island City, NY",
    "Jersey City, NJ",
    "Other Location"
]

# First names by cultural background (80% women's names)
FIRST_NAMES = {
    'East_Asian': {
        'female': ['Wei', 'Xia', 'Jin', 'Yuki', 'Sakura', 'Min', 'Ji-eun', 'Soo-jin', 'Hana', 'Mei'],
        'male': ['Wei', 'Jin', 'Tao', 'Kenji', 'Hiroshi']
    },
    'South_Asian': {
        'female': ['Priya', 'Divya', 'Anjali', 'Maya', 'Zara', 'Aisha', 'Riya', 'Neha', 'Sana', 'Amira'],
        'male': ['Arjun', 'Raj', 'Kumar']
    },
    'Hispanic': {
        'female': ['Sofia', 'Isabella', 'Maria', 'Ana', 'Carmen', 'Elena', 'Lucia', 'Rosa', 'Camila', 'Victoria'],
        'male': ['Miguel', 'Juan', 'Carlos']
    },
    'Middle_Eastern': {
        'female': ['Fatima', 'Leila', 'Yasmin', 'Noor', 'Amira', 'Zara', 'Layla', 'Rania', 'Dalia', 'Hana'],
        'male': ['Omar', 'Ali', 'Hassan']
    },
    'African': {
        'female': ['Amara', 'Zara', 'Aisha', 'Chioma', 'Adanna', 'Kemi', 'Abena', 'Zalika', 'Amina', 'Safiya'],
        'male': ['Malik', 'Jamal', 'Kwame']
    },
    'European': {
        'female': ['Emma', 'Sarah', 'Anna', 'Elena', 'Sophie', 'Clara', 'Nina', 'Leah', 'Eva', 'Mia'],
        'male': ['David', 'Marcus', 'Thomas']
    }
}

LAST_NAMES = {
    'East_Asian': ['Chen', 'Wang', 'Li', 'Zhang', 'Liu', 'Tanaka', 'Sato', 'Kim', 'Park', 'Lee', 'Ng', 'Wong'],
    'South_Asian': ['Patel', 'Singh', 'Kumar', 'Shah', 'Sharma', 'Reddy', 'Kapoor', 'Malhotra', 'Verma', 'Rao'],
    'Hispanic': ['Rodriguez', 'Garcia', 'Martinez', 'Lopez', 'Hernandez', 'Gonzalez', 'Perez', 'Sanchez', 'Torres', 'Ramirez'],
    'Middle_Eastern': ['Ahmed', 'Ali', 'Hassan', 'Khan', 'Rahman', 'Malik', 'Sayeed', 'Qureshi', 'Aziz', 'Ibrahim'],
    'African': ['Johnson', 'Williams', 'Jackson', 'Brown', 'Okafor', 'Mensah', 'Osei', 'Adebayo', 'Okoro', 'Diallo'],
    'European': ['Smith', 'Cohen', 'Miller', 'Davis', 'Wilson', 'Anderson', 'Taylor', 'Thomas', 'Moore', 'Martin']
}

def generate_random_name():
    # 80% chance of female name
    gender = 'female' if random.random() < 0.8 else 'male'
    
    # Random cultural background
    background = random.choice(list(FIRST_NAMES.keys()))
    
    # Get first name from the selected background and gender
    first_name = random.choice(FIRST_NAMES[background][gender])
    
    # 70% chance to use last name from same background, 30% chance to mix
    if random.random() < 0.7:
        last_name = random.choice(LAST_NAMES[background])
    else:
        # Mix cultural backgrounds for last name
        mixed_background = random.choice(list(LAST_NAMES.keys()))
        last_name = random.choice(LAST_NAMES[mixed_background])
    
    # 10% chance of being anonymous
    if random.random() < 0.1:
        return None
        
    return f"{first_name} {last_name}"

def generate_review_text(job_type, rating):
    """Generate a review by combining components"""
    if rating < 4 or random.random() > 0.6:  # 40% chance of no review text for any rating
        return None
        
    parts = []
    parts.append(random.choice(INTROS))
    
    # Add service-specific detail
    if job_type in SERVICE_DETAILS:
        parts.append(random.choice(SERVICE_DETAILS[job_type]))
    
    # Add professionalism comment (80% chance)
    if random.random() < 0.8:
        parts.append(random.choice(PROFESSIONALISM))
    
    # Add recommendation for 5-star reviews (90% chance)
    if rating == 5 and random.random() < 0.9:
        parts.append(random.choice(RECOMMENDATIONS))
    
    return " ".join(parts)

def create_sample_reviews(locksmith_id, num_reviews=10):
    # Calculate ratings distribution for 4.6 average
    ratings = []
    # 70% 5-star reviews
    ratings.extend([5] * int(num_reviews * 0.70))
    # 20% 4-star reviews
    ratings.extend([4] * int(num_reviews * 0.20))
    # 10% 3-star reviews
    ratings.extend([3] * int(num_reviews * 0.10))
    
    # Add or remove ratings to reach desired number
    while len(ratings) < num_reviews:
        ratings.append(5)
    while len(ratings) > num_reviews:
        ratings.pop()
    
    # Shuffle ratings
    random.shuffle(ratings)
    
    # Create reviews
    used_names = set()  # Track used names to avoid duplicates
    
    for rating in ratings:
        # Generate unique name
        while True:
            reviewer_name = generate_random_name()
            if reviewer_name not in used_names:
                break
        
        if reviewer_name:
            used_names.add(reviewer_name)
        
        job_type = random.choice(JOB_TYPES)
        
        # 60% chance to have a review text
        has_comment = random.random() < 0.6
        comment = generate_review_text(job_type, rating) if has_comment else None
        
        review = Review(
            locksmith_id=locksmith_id,
            rating=rating,
            comment=comment,
            reviewer_name=reviewer_name,
            review_date=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
            verified=random.random() > 0.1,  # 90% verified
            job_type=job_type,
            location=random.choice(LOCATIONS)
        )
        db.session.add(review)
    
    db.session.commit() 