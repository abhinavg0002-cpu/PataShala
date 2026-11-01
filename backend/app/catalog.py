"""Curriculum catalog (structure only) + original lessons.

Chapter titles / sub-topic headings come from the Telangana SCERT Class 8 English-medium books
(verified from the team's PDFs). Lesson text and questions are ORIGINAL; no book text is copied.
Prerequisite links are the team's own judgement (to be checked with a teacher).
"""

# ---- what the UI shows for the full system; "enabled" marks the demo slice -----------------
BOARDS = [
    {"id": "telangana", "name": "Telangana State Board (SCERT)", "enabled": True},
    {"id": "ap", "name": "Andhra Pradesh State Board", "enabled": False},
    {"id": "cbse", "name": "CBSE", "enabled": False},
    {"id": "icse", "name": "ICSE / ISC", "enabled": False},
    {"id": "karnataka", "name": "Karnataka State Board", "enabled": False},
    {"id": "tn", "name": "Tamil Nadu State Board", "enabled": False},
    {"id": "maharashtra", "name": "Maharashtra State Board", "enabled": False},
]
STATES = [
    {"id": "telangana", "name": "Telangana", "enabled": True},
    {"id": "ap", "name": "Andhra Pradesh", "enabled": False},
    {"id": "karnataka", "name": "Karnataka", "enabled": False},
    {"id": "tn", "name": "Tamil Nadu", "enabled": False},
    {"id": "maharashtra", "name": "Maharashtra", "enabled": False},
    {"id": "other", "name": "Other states", "enabled": False},
]
CLASSES = [{"no": n, "enabled": n == 8} for n in (6, 7, 8, 9, 10)]
AREA_TYPES = ["Urban", "Semi-urban", "Rural"]

# Class 8 subjects. Only three are in the demo.
SUBJECTS = [
    {"id": "maths", "name": "Mathematics", "enabled": True},
    {"id": "physical", "name": "Physical Science", "enabled": True},
    {"id": "biology", "name": "Biological Science", "enabled": True},
    {"id": "telugu", "name": "Telugu", "enabled": False},
    {"id": "hindi", "name": "Hindi", "enabled": False},
    {"id": "english", "name": "English", "enabled": False},
    {"id": "social", "name": "Social Studies", "enabled": False},
]

# Chapter titles seen in the SCERT PDFs / pages. Only Maths Ch 10 is known for Maths.
# Physical Science / Biology titles are listed WITHOUT numbers because the PDF index order was jumbled.
DEMO_CHAPTER = {
    "maths": "Direct and Inverse Proportions",
    "physical": "Force",
    "biology": "Cell - The Basic Unit of Life",
}
CHAPTERS = {
    "maths": [{"title": "Direct and Inverse Proportions", "no": 10}],
    "physical": [{"title": t} for t in [
        "Force", "Friction", "Synthetic fibres and plastics", "Metals and non-metals",
        "Reflection of light by plane surfaces", "Coal and petroleum",
        "Combustion, fuels and flame", "Electrical conductivity of liquids",
        "Some natural phenomena", "Sound", "Stars and solar system", "Graphs of motion"]],
    "biology": [{"title": t} for t in [
        "What is Science?", "Cell - The Basic Unit of Life", "The World of Microorganisms",
        "Production of Food from Plants", "Different Ecosystems", "Not for Breathing Not for Drinking",
        "Production of Food from Animals", "Why do we fall ill?", "Reproduction in Animals",
        "The Age of Adolescence", "Biodiversity - Conservation"]],
}
SUBTOPICS = {
    "maths": ["10.1 Direct Proportion", "10.2 Inverse Proportion", "10.3 Compound Proportion"],
    "physical": ["1.1 What is force?", "1.2 Types of forces", "1.3 Forces acting at a distance",
                 "1.4 Contact forces", "1.5 Net force", "1.6 How to calculate net force",
                 "1.7 What forces can do?", "1.8 Other effects of force", "1.9 Pressure"],
    "biology": ["2.1 Discovery of the cell", "2.2 Diversity in cells"],
}
BOOK = "Telangana SCERT Class VIII, English medium"

# ---- concepts ---------------------------------------------------------------------------------
# main=False  -> a prerequisite from earlier classes, probed only when needed.
def C(id, subject, name, sub, prereq, main, points, example, glossary=None):
    return {"id": id, "subject": subject, "name": name, "subtopic": sub, "prereq": prereq,
            "main": main, "learn": {"points": points, "example": example, "glossary": glossary or {}}}

CONCEPTS = [
    # ---------------- Maths ----------------
    C("m_ratio", "maths", "Ratio and unit rate", "Earlier classes", [], False,
      ["A ratio compares two amounts, like 12 : 18.",
       "To simplify a ratio, divide both numbers by the same number.",
       "Unit rate = how much for ONE item: total cost ÷ number of items."],
      {"q": "5 pens cost ₹30. What does 1 pen cost?", "steps": ["Unit rate = 30 ÷ 5", "= ₹6 for 1 pen"]},
      {"ratio": "a comparison of two numbers", "unit rate": "the amount for one item"}),
    C("m_direct", "maths", "Direct proportion", "10.1 Direct Proportion", ["m_ratio"], True,
      ["Two quantities are in direct proportion when they go up together or down together.",
       "Their ratio x ÷ y stays the same. That fixed number is the constant.",
       "To solve: write x1 ÷ y1 = x2 ÷ y2 and find the missing value."],
      {"q": "4 notebooks cost ₹60. What do 10 notebooks cost?",
       "steps": ["1 notebook = 60 ÷ 4 = ₹15", "10 notebooks = 10 × 15 = ₹150",
                 "More notebooks → more money: direct proportion"]},
      {"constant": "a number that never changes", "proportion": "two things changing in a fixed way"}),
    C("m_inverse", "maths", "Inverse proportion", "10.2 Inverse Proportion", ["m_ratio", "m_direct"], True,
      ["Two quantities are in inverse proportion when one goes UP and the other goes DOWN in the same proportion.",
       "Their product x × y stays the same.",
       "To solve: x1 × y1 = x2 × y2. More workers means LESS time."],
      {"q": "5 taps fill a tank in 12 hours. How long will 10 taps take?",
       "steps": ["5 × 12 = 60 (this stays the same)", "60 ÷ 10 = 6 hours",
                 "Double the taps → half the time: inverse proportion"]},
      {"inverse": "one goes up, the other goes down", "product": "the answer of multiplying"}),
    C("m_compound", "maths", "Compound proportion", "10.3 Compound Proportion", ["m_direct", "m_inverse"], True,
      ["Sometimes one quantity depends on TWO other things at once.",
       "Ask for each one separately: is it direct or inverse?",
       "Then combine the two changes to find the answer."],
      {"q": "3 men working 4 hours a day finish a job in 10 days. How many days do 6 men working 5 hours a day need?",
       "steps": ["Total work = 3 × 4 × 10 = 120 man-hours", "6 men × 5 hours = 30 man-hours per day",
                 "Days = 120 ÷ 30 = 4 days"]},
      {"compound": "made of two or more parts", "factor": "one thing that affects the answer"}),
    # ---------------- Physical Science ----------------
    C("p_motion", "physical", "Rest, motion and speed", "Earlier classes", [], False,
      ["An object is at rest if its position does not change, and in motion if it does.",
       "Speed = distance ÷ time."],
      {"q": "A bus goes 100 km in 4 hours. What is its speed?", "steps": ["Speed = 100 ÷ 4", "= 25 km/h"]},
      {"speed": "how fast something moves", "distance": "how far it goes"}),
    C("p_force", "physical", "What is force and what it does", "1.1 What is force?", ["p_motion"], True,
      ["A force is a push or a pull.",
       "A force can change the speed, the direction or the shape of an object.",
       "Force is measured in newton (N).",
       "A force can act even when nothing moves, like pushing a wall."],
      {"q": "You squeeze a sponge and it gets smaller. What did the force do?",
       "steps": ["The sponge's shape changed", "A change of shape is an effect of force"]},
      {"force": "a push or a pull", "newton": "the unit of force"}),
    C("p_types", "physical", "Contact and non-contact forces", "1.2 Types of forces", ["p_force"], True,
      ["Contact forces need touching: muscular force and friction.",
       "Some forces act without touching: gravity, magnetic force, electrostatic force."],
      {"q": "A magnet pulls a pin from 2 cm away. Which type of force?",
       "steps": ["The magnet does not touch the pin", "So it is a force acting at a distance (non-contact)"]},
      {"contact": "touching", "muscular": "from the muscles of the body", "friction": "the force that rubs against motion"}),
    C("p_net", "physical", "Net force", "1.5 Net force", ["p_force", "p_types"], True,
      ["Net force is the overall force when several forces act on one object.",
       "Same direction: add the forces. Opposite directions: subtract, and the bigger force decides the direction.",
       "Zero net force does NOT mean no forces. It means the forces are balanced."],
      {"q": "8 N pushes a box east and 3 N pushes it west. What is the net force?",
       "steps": ["Opposite directions → subtract: 8 − 3 = 5 N", "The bigger force is east → 5 N to the east"]},
      {"net": "overall", "balanced": "equal and opposite"}),
    C("p_pressure", "physical", "Pressure", "1.9 Pressure", ["p_force"], True,
      ["Pressure = force ÷ area. Its unit is the pascal (Pa), which is 1 N per square metre.",
       "The same force on a SMALLER area gives MORE pressure."],
      {"q": "A force of 200 N acts on an area of 4 m². What is the pressure?",
       "steps": ["Pressure = 200 ÷ 4", "= 50 Pa"]},
      {"pressure": "force on each square metre", "area": "the size of a surface"}),
    # ---------------- Biology ----------------
    C("b_prior", "biology", "Living things and the microscope", "Earlier classes", [], False,
      ["A microscope makes very small things look bigger.",
       "Living things grow, need food and reproduce. They do not all move."],
      {"q": "A plant is growing but does not move. Is it living?",
       "steps": ["It grows and needs food", "So it is living. Moving is not required."]},
      {"microscope": "an instrument that shows tiny things bigger", "reproduce": "make new living things"}),
    C("b_discovery", "biology", "Discovery of the cell", "2.1 Discovery of the cell", ["b_prior"], True,
      ["In 1665 Robert Hooke looked at thin cork slices and saw box-like spaces. He called them cells. 'Cell' means a little room.",
       "Cork cells are dead cells.",
       "In 1831 Robert Brown saw a dark round spot in orchid leaf cells and called it the nucleus."],
      {"q": "Who named the nucleus?", "steps": ["Hooke saw cork cells", "Brown saw the nucleus in an orchid leaf → Robert Brown"]},
      {"cork": "a light material from tree bark", "nucleus": "the dark round part inside a cell"}),
    C("b_parts", "biology", "Parts of a cell", "2.1 Discovery of the cell", ["b_discovery"], True,
      ["Cell membrane: the thin outer boundary of every cell. It gives shape and lets some things in and out.",
       "Cell wall: an extra layer OUTSIDE the membrane in plant cells. It gives strength.",
       "Cytoplasm: the jelly-like material inside the cell.",
       "Nucleus: a dense round body inside the cell."],
      {"q": "Onion cells have a clear outer layer that cheek cells lack. Which part?",
       "steps": ["The extra outer layer is outside the membrane", "That is the cell wall (only plant cells)"]},
      {"membrane": "thin skin around the cell", "cytoplasm": "jelly-like material inside the cell",
       "rigidity": "being stiff and strong", "selectively": "letting only some things pass"}),
    C("b_types", "biology", "Unicellular and multicellular organisms", "2.2 Diversity in cells", ["b_parts"], True,
      ["Unicellular organisms have ONE cell that does all life processes, like Amoeba.",
       "Multicellular organisms have many cells. Different types of cells do different jobs."],
      {"q": "Is a human unicellular or multicellular?", "steps": ["A human body has many cells", "So multicellular, with different cells doing different jobs"]},
      {"unicellular": "made of one cell", "multicellular": "made of many cells"}),
    C("b_size", "biology", "Shape and size of cells", "2.2 Diversity in cells", ["b_parts"], True,
      ["Cells differ in shape and size. A cell's shape is linked to its job.",
       "1 millimetre = 1000 micrometres, and 1 centimetre = 10 millimetres.",
       "The size of an animal depends on how MANY cells it has, not on how big each cell is."],
      {"q": "Why is an elephant bigger than a mouse?", "steps": ["Their cells are similar in size", "The elephant has many more cells"]},
      {"micrometre": "one millionth of a metre", "function": "the job something does"}),
]
CONCEPT = {c["id"]: c for c in CONCEPTS}
SUBJECT_CONCEPTS = {}
for _c in CONCEPTS:
    SUBJECT_CONCEPTS.setdefault(_c["subject"], []).append(_c["id"])

# ---- misconception tags: label for teachers, short fix for students ----------------------------
TAGS = {
    "treats_inverse_as_direct": ("Treats inverse proportion like direct",
        "More workers means LESS time, so the answer must go down. Use x × y = constant."),
    "treats_direct_as_inverse": ("Treats direct proportion like inverse",
        "More people need MORE rice. Both go up together."),
    "adds_difference": ("Adds the same amount instead of keeping the ratio",
        "Proportion is about multiplying by the same ratio, not adding the same number."),
    "inverts_ratio": ("Flips the ratio upside down",
        "Check the size: should the answer get bigger or smaller? Then set up the ratio the right way round."),
    "multiplies_quantities": ("Multiplies the given numbers together",
        "First find the value for ONE unit, then multiply by the new quantity."),
    "ignores_one_factor": ("Uses only one of the two changing things",
        "Two things changed. Handle each one, then combine them."),
    "subtracts": ("Subtracts instead of dividing", "Cost for one item means DIVIDE total cost by number of items."),
    "multiplies": ("Multiplies instead of dividing", "Rate for one means divide, not multiply."),
    "inverts_division": ("Divides the wrong way round", "Big number ÷ small number when you want the amount for ONE."),
    "reversed": ("Writes the ratio the wrong way round", "Keep the order of the ratio the same."),
    "partial_simplify": ("Stops simplifying too early", "Keep dividing until no common factor is left."),
    "no_change": ("Does not simplify", "Divide both numbers by their common factor."),
    "inverse_idea": ("Thinks 'doubles' means 'halves'", "In direct proportion, both change the same way."),
    "direct_idea": ("Thinks 'doubles' means 'doubles' for inverse", "In inverse proportion, one doubling makes the other half."),
    "adds_terms": ("Adds terms instead of multiplying", "Compound ratio multiplies the first terms and the second terms."),
    "cross_multiplies": ("Cross-multiplies the ratio terms", "Multiply first with first, second with second."),
    "gives_distance_not_speed": ("Gives distance instead of speed", "Read what the question asks for."),
    "no_motion_no_force": ("Thinks no motion means no force", "A force can act even when nothing moves, like pushing a wall."),
    "force_changes_mass": ("Thinks force changes mass", "A force changes shape, speed or direction, not how much matter there is."),
    "adds_opposite": ("Adds forces that act in opposite directions", "Opposite directions: subtract."),
    "subtracts_same_direction": ("Subtracts forces in the same direction", "Same direction: add."),
    "wrong_direction": ("Right size, wrong direction", "The bigger force decides the direction of the net force."),
    "adds_all": ("Adds all forces without checking direction", "Split the forces by direction first."),
    "zero_net_means_no_forces": ("Thinks zero net force means no forces", "Zero net force means the forces are balanced, not absent."),
    "uses_one_force": ("Looks at only one of the forces", "Net force uses all the forces."),
    "more_force_at_tip": ("Thinks the tip has more force", "The force is the same. The small area makes the pressure bigger."),
    "pressure_independent_of_area": ("Thinks area does not matter", "Pressure = force ÷ area. Area matters."),
    "magnet_must_touch": ("Thinks a magnet must touch", "A magnet can pull without touching."),
    "movement_means_living": ("Thinks living things must move", "Plants are living but do not move around."),
    "confuses_brown_hooke": ("Mixes up Hooke and Brown", "Hooke: cork cells (1665). Brown: nucleus (1831)."),
    "confuses_wall_membrane": ("Mixes up cell wall and cell membrane", "The cell wall is an extra outer layer in plant cells. The membrane is inside it."),
    "both_in_all_cells": ("Thinks every cell has a cell wall", "Only plant cells have a cell wall."),
    "many_processes_means_multicellular": ("Thinks many life processes means many cells", "A single cell can do all life processes."),
    "one_cell_does_all": ("Thinks one cell does everything in humans", "In humans, different cells do different jobs."),
    "bigger_animal_bigger_cells": ("Thinks bigger animals have bigger cells", "Bigger animals mostly have MORE cells, not bigger cells."),
    "divides": ("Divides when converting to a smaller unit", "Going to a smaller unit gives a bigger number."),
    "no_conversion": ("Forgets to convert units", "Convert first: 1 cm = 10 mm."),
    "compares_totals": ("Compares total prices, not the price for one", "Find the price of ONE kg for each deal, then compare."),
    "area_direct": ("Thinks pressure grows with area", "A bigger area spreads the force out, so the pressure goes down."),
}


def subject_main_concepts(subject):
    return [c for c in SUBJECT_CONCEPTS[subject] if CONCEPT[c]["main"]]


def public_catalog():
    return {
        "book": BOOK, "boards": BOARDS, "states": STATES, "classes": CLASSES, "area_types": AREA_TYPES,
        "subjects": SUBJECTS, "chapters": CHAPTERS, "subtopics": SUBTOPICS, "demo_chapter": DEMO_CHAPTER,
        "concepts": [{"id": c["id"], "subject": c["subject"], "name": c["name"], "subtopic": c["subtopic"],
                      "prereq": c["prereq"], "main": c["main"]} for c in CONCEPTS],
    }
