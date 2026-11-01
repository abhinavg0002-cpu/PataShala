"""Original question bank (all questions written by the team; nothing copied from textbooks).

load  = "low": short / numbers or one fact.  "high": longer story-style English.
pair  = links a low-load and a high-load question testing the same skill (used to spot English load).
tags  = {option_index: misconception_tag} for wrong options.
simple = the same question in plain words, shown when the student seems to be struggling with English.
"""

BANK = []


def Q(id, concept, diff, load, text, opts, ans, tags, hints, why, pair=None, simple=None):
    assert len(opts) == 4 and 0 <= ans < 4 and len(hints) == 3, id
    BANK.append({"id": id, "concept": concept, "difficulty": diff, "load": load, "text": text,
                 "options": opts, "answer": ans, "tags": {str(k): v for k, v in tags.items()},
                 "hints": hints, "why": why, "pair": pair, "simple": simple})


# ============================ MATHS : Direct and Inverse Proportions ==========================
Q("m_r1", "m_ratio", "easy", "low", "Simplify the ratio 12 : 18.", ["2 : 3", "3 : 2", "6 : 9", "12 : 18"], 0,
  {1: "reversed", 2: "partial_simplify", 3: "no_change"},
  ["Look for a number that divides both 12 and 18.", "Both numbers can be divided by 6.",
   "12 ÷ 6 = 2 and 18 ÷ 6 = 3, so the ratio is 2 : 3."], "Divide both terms by 6.")
Q("m_r2", "m_ratio", "medium", "low", "₹40 for 5 pens. What is the price of 1 pen?", ["₹8", "₹35", "₹200", "₹0.125"], 0,
  {1: "subtracts", 2: "multiplies", 3: "inverts_division"},
  ["You want the price of ONE pen.", "Divide the total cost by the number of pens.", "40 ÷ 5 = 8."], "40 ÷ 5 = ₹8.", pair="p_mr")
Q("m_r3", "m_ratio", "medium", "high",
  "A shopkeeper in Warangal sells a packet of 6 identical notebooks for ₹90. Ravi wants to buy only one notebook from the packet. How much should he pay?",
  ["₹15", "₹84", "₹540", "₹0.07"], 0, {1: "subtracts", 2: "multiplies", 3: "inverts_division"},
  ["Find the price of ONE notebook.", "Divide the packet price by the number of notebooks.", "90 ÷ 6 = 15."], "90 ÷ 6 = ₹15.",
  pair="p_mr", simple="6 notebooks cost ₹90. What does 1 notebook cost?")
Q("m_r4", "m_ratio", "hard", "low", "Which is the better buy: 3 kg for ₹150, or 5 kg for ₹225?",
  ["5 kg for ₹225", "3 kg for ₹150", "Both are the same", "Cannot be decided"], 0, {1: "compares_totals"},
  ["Compare the price of ONE kg, not the total price.", "Find 150 ÷ 3 and 225 ÷ 5.", "₹50 per kg versus ₹45 per kg, so 5 kg for ₹225 is cheaper per kg."],
  "₹45 per kg is cheaper than ₹50 per kg.")

Q("m_d1", "m_direct", "easy", "low", "In direct proportion, if one quantity becomes double, the other becomes:",
  ["Double", "Half", "The same", "Zero"], 0, {1: "inverse_idea"},
  ["Direct means they move together.", "If one goes up, so does the other.", "Double goes with double."], "Both change the same way.")
Q("m_d2", "m_direct", "medium", "low", "x ÷ y = 3 ÷ 12 always stays the same. If y = 60, find x.", ["15", "63", "240", "5"], 0,
  {1: "adds_difference", 2: "inverts_ratio"},
  ["Write x ÷ 60 = 3 ÷ 12.", "Multiply both sides by 60.", "x = 3 × 60 ÷ 12 = 15."], "x = 60 × 3 ÷ 12 = 15.", pair="p_md")
Q("m_d3", "m_direct", "medium", "high",
  "A bakery in Karimnagar uses 2 cups of flour to make 8 rotis. How many cups of flour does it need to make 40 rotis?",
  ["10", "34", "160", "5"], 0, {1: "adds_difference", 2: "inverts_ratio"},
  ["More rotis need more flour: direct proportion.", "Find the flour for 1 roti: 2 ÷ 8.", "40 × (2 ÷ 8) = 10."], "2 ÷ 8 × 40 = 10 cups.",
  pair="p_md", simple="2 cups of flour make 8 rotis. How many cups make 40 rotis?")
Q("m_d4", "m_direct", "hard", "low", "15 kg of rice costs ₹600. What do 22 kg cost?", ["₹880", "₹607", "₹409", "₹330"], 0,
  {1: "adds_difference", 2: "inverts_ratio", 3: "multiplies_quantities"},
  ["Find the cost of 1 kg first.", "600 ÷ 15 = 40 per kg.", "22 × 40 = 880."], "₹40 per kg × 22 = ₹880.")
Q("m_d5", "m_direct", "hard", "high",
  "Asha types 180 words in 4 minutes at a steady speed. How many words can she type in 7 minutes at the same speed?",
  ["315", "183", "103", "1,260"], 0, {1: "adds_difference", 2: "inverts_ratio", 3: "multiplies_quantities"},
  ["Steady speed means direct proportion.", "Words in 1 minute: 180 ÷ 4 = 45.", "45 × 7 = 315."], "45 words a minute × 7 = 315.",
  simple="Asha types 180 words in 4 minutes. How many words in 7 minutes?")

Q("m_i1", "m_inverse", "easy", "low", "In inverse proportion, if one quantity becomes double, the other becomes:",
  ["Half", "Double", "The same", "Zero"], 0, {1: "direct_idea"},
  ["Inverse means opposite directions.", "If one goes up, the other comes down.", "Double goes with half."], "Opposite change: double and half.")
Q("m_i2", "m_inverse", "medium", "low", "x × y always stays the same. When x = 6, y = 12. Find y when x = 9.", ["8", "18", "15", "108"], 0,
  {1: "treats_inverse_as_direct", 2: "adds_difference", 3: "multiplies_quantities"},
  ["The product x × y is fixed: 6 × 12.", "6 × 12 = 72.", "72 ÷ 9 = 8."], "6 × 12 = 72, and 72 ÷ 9 = 8.", pair="p_mi")
Q("m_i3", "m_inverse", "medium", "high",
  "A parcel company's 4 workers take 18 days to pack all the parcels in a godown. How many days will 6 workers take to pack the same parcels?",
  ["12", "27", "20", "432"], 0, {1: "treats_inverse_as_direct", 2: "adds_difference", 3: "multiplies_quantities"},
  ["More workers means less time: inverse proportion.", "Workers × days stays the same: 4 × 18 = 72.", "72 ÷ 6 = 12."], "4 × 18 = 72 and 72 ÷ 6 = 12 days.",
  pair="p_mi", simple="4 workers take 18 days. How many days will 6 workers take (same work)?")
Q("m_i4", "m_inverse", "hard", "low", "In inverse proportion, x = 48 when y = 5. Find x when y = 4.", ["60", "38.4", "49", "240"], 0,
  {1: "treats_inverse_as_direct", 2: "adds_difference", 3: "multiplies_quantities"},
  ["x × y is fixed.", "48 × 5 = 240.", "240 ÷ 4 = 60."], "48 × 5 = 240 and 240 ÷ 4 = 60.")
Q("m_i5", "m_inverse", "hard", "high",
  "A hostel has food for 80 students for 30 days. If 20 more students join on the first day, for how many days will the same food last?",
  ["24 days", "37.5 days", "10 days", "50 days"], 0, {1: "treats_inverse_as_direct", 2: "adds_difference", 3: "adds_difference"},
  ["More students means the food lasts fewer days.", "Total food = 80 × 30 = 2400 student-days.", "Now 100 students: 2400 ÷ 100 = 24."],
  "80 × 30 = 2400 and 2400 ÷ 100 = 24 days.", simple="Food for 80 students lasts 30 days. How long does it last for 100 students?")

Q("m_c1", "m_compound", "easy", "low", "The compound ratio of 2 : 3 and 4 : 5 is:", ["8 : 15", "6 : 8", "10 : 12", "2 : 5"], 0,
  {1: "adds_terms", 2: "cross_multiplies"},
  ["Compound ratio multiplies the ratios.", "First terms: 2 × 4. Second terms: 3 × 5.", "2 × 4 = 8 and 3 × 5 = 15."], "8 : 15.")
Q("m_c2", "m_compound", "medium", "low",
  "6 workers, 8 hours a day, 10 days. How many days for 4 workers working 6 hours a day (same job)?", ["20", "5", "15", "12"], 0,
  {1: "treats_inverse_as_direct", 2: "ignores_one_factor"},
  ["Fewer workers AND fewer hours: the days go up.", "Total work = 6 × 8 × 10 = 480 worker-hours.", "480 ÷ (4 × 6) = 20."], "480 ÷ 24 = 20 days.", pair="p_mc")
Q("m_c3", "m_compound", "medium", "high",
  "Twelve men working six hours every day can dig a canal in fifteen days. A contractor wants the same canal dug by eighteen men who will work five hours every day. How many days will the eighteen men need?",
  ["12 days", "10 days", "18 days", "20 days"], 0, {1: "ignores_one_factor", 2: "ignores_one_factor"},
  ["Both the number of men and the hours changed.", "Total work = 12 × 6 × 15 = 1080 man-hours.", "1080 ÷ (18 × 5) = 12."], "1080 ÷ 90 = 12 days.",
  pair="p_mc", simple="12 men, 6 hours a day, take 15 days. How many days for 18 men, 5 hours a day?")
Q("m_c4", "m_compound", "hard", "high",
  "A school kitchen cooks for 150 students for 20 days using 600 kg of rice. How much rice is needed for 100 students for 15 days?",
  ["300 kg", "400 kg", "450 kg", "1,200 kg"], 0, {1: "ignores_one_factor", 2: "ignores_one_factor", 3: "treats_direct_as_inverse"},
  ["Rice goes up with students AND with days (both direct).", "600 × (100 ÷ 150) × (15 ÷ 20).", "600 × 2/3 × 3/4 = 300."], "600 × 2/3 × 3/4 = 300 kg.",
  simple="600 kg of rice feeds 150 students for 20 days. How much rice for 100 students for 15 days?")

# ============================ PHYSICAL SCIENCE : Force ==========================================
Q("p_m1", "p_motion", "easy", "low", "An object that does not change its position with time is:",
  ["At rest", "In motion", "Speeding up", "Rotating"], 0, {}, ["Think about whether the position changes.", "No change in position means not moving.", "That is called being at rest."], "No change of position = at rest.")
Q("p_m2", "p_motion", "medium", "low", "Distance = 40 km, time = 2 h. Speed = ?", ["20 km/h", "80 km/h", "38 km/h", "42 km/h"], 0,
  {1: "multiplies", 2: "subtracts", 3: "adds_difference"},
  ["Speed tells distance covered in ONE hour.", "Speed = distance ÷ time.", "40 ÷ 2 = 20."], "40 ÷ 2 = 20 km/h.", pair="p_pm")
Q("p_m3", "p_motion", "medium", "high",
  "Anil rides his bicycle along a straight road without stopping and covers 30 kilometres in two hours. What is the speed of his bicycle?",
  ["15 km/h", "60 km/h", "28 km/h", "32 km/h"], 0, {1: "multiplies", 2: "subtracts", 3: "adds_difference"},
  ["Speed is distance covered in one hour.", "Speed = distance ÷ time.", "30 ÷ 2 = 15."], "30 ÷ 2 = 15 km/h.", pair="p_pm", simple="30 km in 2 hours. What is the speed?")

Q("p_f1", "p_force", "easy", "low", "A force is a:", ["Push or a pull", "Kind of material", "Measure of time", "Change of colour"], 0, {},
  ["Think about opening a door.", "You push or pull it.", "A force is a push or a pull."], "A force is a push or a pull.")
Q("p_f5", "p_force", "easy", "low", "In which unit is force measured?", ["Newton", "Kilogram", "Metre", "Second"], 0, {},
  ["It is named after a scientist.", "Its short form is N.", "Force is measured in newton."], "The unit of force is the newton (N).")
Q("p_f2", "p_force", "medium", "low", "Which of these can a force change?", ["The shape of an object", "The mass of an object", "The colour of an object", "The material of an object"], 0,
  {1: "force_changes_mass"}, ["Think about squeezing clay.", "A force can change shape, speed or direction.", "Of these, only the shape."], "A force can change shape, speed or direction.", pair="p_pf")
Q("p_f3", "p_force", "medium", "high",
  "Rani presses a soft rubber ball between her two palms and the ball becomes flat. What has the force done to the ball?",
  ["Changed its shape", "Changed its mass", "Changed its colour", "Changed its material"], 0, {1: "force_changes_mass"},
  ["Look at what happened to the ball.", "It became flat.", "Becoming flat is a change of shape."], "A force changed the shape of the ball.",
  pair="p_pf", simple="A force squeezes a rubber ball flat. What changed?")
Q("p_f4", "p_force", "hard", "high", "Meena pushes a big wall with all her strength, but the wall does not move at all. Which statement is correct?",
  ["She applies a force, but we cannot see any motion", "She applies no force because nothing moved", "The wall applies a force but she does not", "A force can act only when something moves"], 0,
  {1: "no_motion_no_force", 3: "no_motion_no_force"},
  ["Is pushing the same as moving?", "You can push hard even when nothing moves.", "A force acts even when there is no visible motion."],
  "A force can act without any visible motion.", simple="Meena pushes a wall. It does not move. Is a force acting?")

Q("p_t1", "p_types", "easy", "low", "Which of these is a force that acts at a distance?", ["Magnetic force", "Muscular force", "Frictional force", "A push by hand"], 0, {},
  ["Which force works without touching?", "A magnet can pull without touching.", "Magnetic force acts at a distance."], "Magnetic force does not need touching.")
Q("p_t2", "p_types", "medium", "low", "A magnet pulls an iron nail without touching it. This is a:", ["Non-contact force", "Contact force", "Muscular force", "Frictional force"], 0,
  {1: "magnet_must_touch"}, ["Is there touching?", "No touching, so not a contact force.", "It is a non-contact force."], "Non-contact: no touching needed.", pair="p_pt")
Q("p_t3", "p_types", "medium", "high",
  "When Kavya lets go of her pen, it falls to the floor even though nothing touches it. Which force pulls the pen downwards?",
  ["Gravitational force", "Muscular force", "Frictional force", "Magnetic force"], 0, {},
  ["Nothing touches the pen, so it is not a contact force.", "The Earth pulls things towards itself.", "That is gravitational force."], "Gravity pulls the pen down without touching it.",
  pair="p_pt", simple="A pen falls when released. Which force pulls it down?")
Q("p_t4", "p_types", "hard", "high",
  "Rahul pushes a heavy almirah along the floor and it moves slowly. Which two forces are acting on the almirah because of CONTACT with Rahul's hand and with the floor?",
  ["Muscular force and friction", "Magnetic force and gravity", "Gravity and electrostatic force", "Muscular force and magnetic force"], 0, {},
  ["Contact means touching.", "Rahul's hand touches the almirah. The floor touches it too.", "Muscular force from his hand and friction from the floor."],
  "Muscular force and friction act by contact.", simple="Rahul pushes an almirah on the floor. Which two forces act by touching?")

Q("p_n1", "p_net", "easy", "low", "Forces of 5 N and 3 N act on a box in the SAME direction. The net force is:", ["8 N", "2 N", "15 N", "1.67 N"], 0,
  {1: "subtracts_same_direction"}, ["Same direction means the forces help each other.", "Add them.", "5 + 3 = 8 N."], "Same direction: add. 8 N.")
Q("p_n2", "p_net", "medium", "low", "Forces of 10 N to the right and 4 N to the left act on a box. The net force is:",
  ["6 N to the right", "14 N to the right", "6 N to the left", "40 N"], 0, {1: "adds_opposite", 2: "wrong_direction"},
  ["Opposite directions work against each other.", "Subtract the smaller from the bigger.", "10 − 4 = 6 N, in the direction of the bigger force (right)."],
  "10 − 4 = 6 N to the right.", pair="p_pn")
Q("p_n3", "p_net", "medium", "high",
  "Two children pull a rope in opposite directions. Seema pulls with 30 N towards the east and Tara pulls with 20 N towards the west. What is the net force on the rope?",
  ["10 N towards the east", "50 N towards the east", "10 N towards the west", "600 N"], 0, {1: "adds_opposite", 2: "wrong_direction"},
  ["They pull in opposite directions.", "Subtract: 30 − 20.", "10 N, towards the stronger side (east)."], "30 − 20 = 10 N to the east.",
  pair="p_pn", simple="30 N to the east and 20 N to the west. What is the net force?")
Q("p_n4", "p_net", "hard", "high",
  "Three forces act on a trolley along one straight line: 12 N to the right, 7 N to the right and 15 N to the left. What is the net force?",
  ["4 N to the right", "34 N to the right", "4 N to the left", "8 N to the right"], 0, {1: "adds_all", 2: "wrong_direction"},
  ["Group the forces by direction first.", "Right: 12 + 7 = 19 N. Left: 15 N.", "19 − 15 = 4 N to the right."], "19 N right − 15 N left = 4 N right.",
  simple="12 N right, 7 N right, 15 N left. What is the net force?")
Q("p_n5", "p_net", "hard", "low", "A box at rest has 8 N pushing it east and 8 N pushing it west. Which is true?",
  ["Net force is zero, so its motion does not change", "Net force is 16 N, so it moves", "Net force is 8 N, so it moves east", "No forces act on the box"], 0,
  {1: "adds_opposite", 2: "uses_one_force", 3: "zero_net_means_no_forces"},
  ["Both forces are acting.", "Equal forces in opposite directions cancel in their effect.", "Net force is zero because they are balanced."],
  "Balanced forces: net force is zero, but forces still act.")

Q("p_p1", "p_pressure", "easy", "low", "Pressure is calculated as:", ["Force ÷ Area", "Force × Area", "Area ÷ Force", "Force + Area"], 0,
  {1: "multiplies_quantities", 2: "inverts_ratio"}, ["Pressure is force on each unit of area.", "'On each' means divide.", "Pressure = Force ÷ Area."], "Pressure = force ÷ area.")
Q("p_p2", "p_pressure", "medium", "low", "A force of 100 N acts on an area of 4 m². The pressure is:", ["25 Pa", "400 Pa", "96 Pa", "0.04 Pa"], 0,
  {1: "multiplies_quantities", 2: "subtracts", 3: "inverts_ratio"}, ["Pressure = force ÷ area.", "100 ÷ 4.", "= 25 Pa."], "100 ÷ 4 = 25 Pa.", pair="p_pp")
Q("p_p3", "p_pressure", "medium", "high",
  "A box presses on a table with a force of 60 N through a surface of 3 square metres. How much pressure does the box put on the table?",
  ["20 Pa", "180 Pa", "57 Pa", "0.05 Pa"], 0, {1: "multiplies_quantities", 2: "subtracts", 3: "inverts_ratio"},
  ["Pressure = force ÷ area.", "Force is 60 N. Area is 3 m².", "60 ÷ 3 = 20 Pa."], "60 ÷ 3 = 20 Pa.", pair="p_pp", simple="Force 60 N, area 3 m². What is the pressure?")
Q("p_p4", "p_pressure", "hard", "high",
  "A nail has a sharp tip and a flat head. We hammer the flat head and the tip goes into the wood easily. Why?",
  ["The same force on a small area gives a large pressure", "The tip carries more force than the head", "Pressure does not depend on area", "The head has less force than the tip"], 0,
  {1: "more_force_at_tip", 2: "pressure_independent_of_area", 3: "more_force_at_tip"},
  ["The force along the nail is the same everywhere.", "The tip has a very small area.", "Small area means large pressure."],
  "Same force, small area → large pressure.", simple="Why does a sharp nail go into wood easily?")
Q("p_p5", "p_pressure", "hard", "low", "The force stays the same but the area becomes 2 times bigger. The pressure becomes:", ["Half", "Double", "The same", "Four times"], 0,
  {1: "area_direct", 2: "pressure_independent_of_area"}, ["Pressure = force ÷ area.", "A bigger area at the bottom makes the answer smaller.", "Double area gives half the pressure."],
  "Double the area → half the pressure.")

# ============================ BIOLOGY : Cell - The Basic Unit of Life ============================
Q("b_p1", "b_prior", "easy", "low", "Which instrument shows very small things bigger?", ["Microscope", "Telescope", "Thermometer", "Balance"], 0, {},
  ["It has a lens.", "It is used in a science lab to see tiny things.", "It is the microscope."], "A microscope magnifies tiny things.")
Q("b_p2", "b_prior", "medium", "low", "Which of these grows, needs food and reproduces?", ["Mango tree", "Stone", "Table", "Plastic toy"], 0, {},
  ["Which one is alive?", "Living things grow and reproduce.", "A mango tree."], "Living things grow, need food and reproduce.", pair="p_bp")
Q("b_p3", "b_prior", "medium", "high",
  "Priya sees a small green plant near the school gate. It was shorter last week and it needs water and sunlight. Is the plant living or non-living, and why?",
  ["Living, because it grows and needs food", "Non-living, because it does not move", "Non-living, because it is green", "Living, because it is small"], 0,
  {1: "movement_means_living"}, ["Does the plant grow?", "Growing and needing food are signs of life.", "Moving around is not needed to be alive."],
  "Growth and needing food show that it is living.", pair="p_bp", simple="A plant grows and needs water. Is it living or non-living?")

Q("b_d1", "b_discovery", "easy", "low", "The word 'cell' means:", ["A little room", "A small ball", "A tiny seed", "A thin sheet"], 0, {},
  ["It comes from Latin.", "Hooke saw box-like spaces in cork.", "A little room."], "'Cell' is Latin for a little room.")
Q("b_d2", "b_discovery", "medium", "low", "Who gave the name 'nucleus'?", ["Robert Brown", "Robert Hooke", "Louis Pasteur", "Charles Darwin"], 0,
  {1: "confuses_brown_hooke"}, ["It was seen in an orchid leaf.", "Two scientists have the first name Robert.", "Robert Brown named the nucleus; Hooke saw the cork cells."],
  "Robert Brown named the nucleus (1831).", pair="p_bd")
Q("b_d3", "b_discovery", "medium", "high",
  "In 1831, while studying the thin outer layer of an orchid leaf, a scientist noticed a round, slightly darker spot inside many cells and named it the nucleus. Who was the scientist?",
  ["Robert Brown", "Robert Hooke", "Louis Pasteur", "Charles Darwin"], 0, {1: "confuses_brown_hooke"},
  ["The date is 1831 and the leaf is an orchid.", "The spot he named is the nucleus.", "That was Robert Brown."], "Robert Brown, 1831.",
  pair="p_bd", simple="Who saw a dark round spot in orchid leaf cells and named it the nucleus?")
Q("b_d4", "b_discovery", "hard", "low", "The cork cells that Robert Hooke saw were:", ["Dead cells", "Living cells", "Animal cells", "Nerve cells"], 0, {},
  ["Cork comes from tree bark.", "Cork cells are empty box-like spaces.", "They are dead cells."], "Cork cells are dead cells.")
Q("b_d5", "b_discovery", "hard", "high",
  "Hooke saw only empty box-like spaces in cork, but an onion peel under a microscope shows cells with a dark spot inside. Why is there a difference?",
  ["Cork cells are dead and have lost their contents, but onion peel cells are living", "Onion cells are made of a different material", "Hooke's microscope was too weak to see onion cells", "Cork cells never have a nucleus"], 0, {},
  ["Think about dead and living cells.", "Dead cells are empty. Living cells have contents.", "The onion cells are living, so they show contents like the nucleus."],
  "Cork cells are dead (empty). Onion cells are living.", simple="Cork cells look empty but onion cells have a dark spot. Why?")

Q("b_pt1", "b_parts", "easy", "low", "The jelly-like material between the nucleus and the cell membrane is:", ["Cytoplasm", "Cell wall", "Nucleus", "Stomata"], 0,
  {1: "confuses_wall_membrane"}, ["It is inside the cell.", "It is jelly-like.", "That is the cytoplasm."], "Cytoplasm is the jelly-like material.")
Q("b_pt2", "b_parts", "medium", "low", "Which part gives strength and rigidity to plant cells?", ["Cell wall", "Cell membrane", "Cytoplasm", "Nucleus"], 0,
  {1: "confuses_wall_membrane"}, ["It is found only in plant cells.", "It is outside the membrane.", "The cell wall."], "The cell wall gives rigidity.", pair="p_bpt")
Q("b_pt3", "b_parts", "medium", "high",
  "Ravi looks at onion peel cells and cheek cells under a microscope. The onion cells show a clear thick outer layer outside the thin boundary, but the cheek cells do not. Which part is found only in the onion cells?",
  ["Cell wall", "Nucleus", "Cytoplasm", "Cell membrane"], 0, {3: "confuses_wall_membrane"},
  ["Onion is a plant. Cheek cells are animal cells.", "Which layer do only plant cells have?", "The cell wall."], "Only plant cells have a cell wall.",
  pair="p_bpt", simple="Onion cells have an extra outer layer. Cheek cells do not. What is it?")
Q("b_pt4", "b_parts", "hard", "low", "The cell membrane:",
  ["Allows only some substances to pass in and out", "Gives rigidity to the cell", "Is found only in plant cells", "Stores the food of the cell"], 0,
  {1: "confuses_wall_membrane", 2: "confuses_wall_membrane"}, ["It is the thin boundary of the cell.", "It is in all cells.", "It lets some things in and out."], "The membrane is selective.")
Q("b_pt5", "b_parts", "hard", "high",
  "A student says, 'The cell wall and the cell membrane are the same thing, because both are on the outside of the cell.' Which statement corrects the student best?",
  ["The cell wall is an extra layer outside the membrane in plant cells, giving rigidity", "Both are found in every kind of cell", "The cell membrane is outside the cell wall", "The cell wall lets only some substances pass"], 0,
  {1: "both_in_all_cells", 3: "confuses_wall_membrane"}, ["Which one is in every cell?", "The wall is an extra layer in plants.", "It is outside the membrane and gives strength."],
  "Wall: extra outer layer in plants. Membrane: in all cells.", simple="Are cell wall and cell membrane the same? What is the difference?")

Q("b_u1", "b_types", "easy", "low", "Amoeba is a:", ["Unicellular organism", "Multicellular organism", "Plant", "Non-living thing"], 0, {},
  ["'Uni' means one.", "Amoeba has a single cell.", "Unicellular."], "Amoeba is made of one cell.")
Q("b_u2", "b_types", "medium", "low", "An organism made of many cells is called:", ["Multicellular", "Unicellular", "Single-celled", "Non-cellular"], 0,
  {1: "many_processes_means_multicellular"}, ["'Multi' means many.", "Many cells.", "Multicellular."], "Multi = many.", pair="p_bu")
Q("b_u3", "b_types", "medium", "high",
  "A scientist sees a tiny pond organism under the microscope. It has only one cell, but it eats, breathes, grows and reproduces on its own. What type of organism is it?",
  ["Unicellular, since one cell does all the life processes", "Multicellular, since it does many life processes", "Non-living, since it has only one cell", "Multicellular, since it lives in a pond"], 0,
  {1: "many_processes_means_multicellular"}, ["Count the cells.", "One cell means unicellular.", "A single cell can do all life processes."],
  "One cell = unicellular.", pair="p_bu", simple="An organism has one cell and does all life processes. Unicellular or multicellular?")
Q("b_u4", "b_types", "hard", "high", "In a multicellular organism like a human, how are the basic life processes carried out?",
  ["By different types of cells doing different jobs", "By one cell doing everything", "By the nucleus alone", "By cells that are all exactly alike"], 0,
  {1: "one_cell_does_all", 3: "one_cell_does_all"}, ["Many cells are present.", "Cells specialise.", "Different cells do different jobs."], "Cells share the work.",
  simple="In humans, who does the work: one cell or different cells?")

Q("b_s1", "b_size", "easy", "low", "Which is the largest cell mentioned in the chapter?", ["Egg of an ostrich", "Human liver cell", "A bacterium", "Red blood cell"], 0, {},
  ["Think of a very big egg.", "A bird's egg is a single cell.", "The ostrich egg."], "The ostrich egg is the largest cell.")
Q("b_s2", "b_size", "medium", "low", "1 millimetre = how many micrometres?", ["1000", "100", "10", "10,000"], 0, {},
  ["Micro is very small.", "A millimetre is divided into thousands.", "1000."], "1 mm = 1000 micrometres.", pair="p_bs")
Q("b_s3", "b_size", "medium", "high", "A human nerve cell can be nearly 90 centimetres long. How many millimetres is that?",
  ["900", "9", "9,000", "90"], 0, {1: "divides", 3: "no_conversion"},
  ["1 cm = 10 mm.", "Going to the smaller unit gives a bigger number.", "90 × 10 = 900."], "90 cm × 10 = 900 mm.", pair="p_bs",
  simple="90 cm = how many mm?")
Q("b_s4", "b_size", "hard", "high", "Nina says, 'An elephant is bigger than a man because its cells are much bigger.' Is she right?",
  ["No, an elephant is bigger mainly because it has more cells", "Yes, elephant cells are much bigger than human cells", "Yes, big animals always have big cells", "No, elephants have fewer cells than humans"], 0,
  {1: "bigger_animal_bigger_cells", 2: "bigger_animal_bigger_cells"}, ["Compare number of cells, not size.", "Cells are about the same size in big and small animals.", "The elephant has more cells."],
  "Body size depends on how many cells, not how big they are.", simple="Does an elephant have bigger cells than a man, or more cells?")
Q("b_s5", "b_size", "hard", "low", "The size of an animal depends mainly on:", ["The number of cells", "The size of each cell", "The colour of the cells", "The shape of the nucleus"], 0,
  {1: "bigger_animal_bigger_cells"}, ["Think about counting.", "More cells make a bigger body.", "The number of cells."], "More cells, bigger animal.")

BY_ID = {q["id"]: q for q in BANK}


def questions_for(concept):
    return [q for q in BANK if q["concept"] == concept]


def public_question(q, simplified=False):
    """What the phone is allowed to see BEFORE answering: no answer, no tags."""
    return {"id": q["id"], "concept": q["concept"], "difficulty": q["difficulty"], "load": q["load"],
            "text": q["simple"] if (simplified and q["simple"]) else q["text"], "options": q["options"], "hints": q["hints"]}
