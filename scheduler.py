"""Filter the master session list down to a student's personal schedule."""

from __future__ import annotations

CORE_COURSES: list[str] = ["CDA", "BDM", "BE", "PM", "SM", "HRM", "CRF"]
ALL_ELECTIVES: list[str] = ["SAAPM", "EMABE", "FRM", "CMF", "PRO", "IBC", "CSLBA"]

COURSE_NAMES: dict[str, str] = {
    "CDA":   "Categorical Data Analysis",
    "BDM":   "Business Data Mining",
    "BE":    "Business Economics",
    "PM":    "Project Management",
    "SM":    "Strategic Management",
    "HRM":   "Human Resource Management",
    "CRF":   "Corporate Finance",
    "SAAPM": "Selected Aspects of Advanced Predictive Modelling",
    "EMABE": "Econometric Methods with Applications in Business & Economics",
    "FRM":   "Financial Risk Management",
    "CMF":   "Computational Finance",
    "PRO":   "Pricing and Revenue Optimisation",
    "IBC":   "Intercultural Business Communication",
    "CSLBA": "Causality in Statistical Learning for Business Applications",
}

INSTRUCTORS: dict[str, str] = {
    "CDA":   "Prof. Sabyasachi Mukhopadhyay",
    "BDM":   "Prof. Uttam Kumar Sarkar / Prof. Vimal Kumar M",
    "BE":    "Prof. Tanika Chakraborty / Prof. Parthapratim Pal",
    "PM":    "Prof. Megha Sharma",
    "SM":    "Prof. Latasri Hazarika",
    "HRM":   "Prof. Randhir Kumar",
    "CRF":   "Prof. Vivek Rajvanshi",
    "SAAPM": "Prof. Manisha Chakrabarty",
    "EMABE": "Prof. Manisha Chakrabarty",
    "FRM":   "Prof. Samit Paul",
    "CMF":   "Prof. Vivek Rajvanshi",
    "PRO":   "Prof. Sumanta Basu",
    "IBC":   "Prof. Apoorva Bharadwaj",
    "CSLBA": "Prof. Prajamitra Bhuyan",
}


def get_schedule(all_sessions: list[dict], selected_electives: list[str]) -> list[dict]:
    keep = set(CORE_COURSES) | set(selected_electives)
    filtered = [s for s in all_sessions if s["course"] in keep]
    filtered.sort(key=lambda s: (s["date"], s["start"]))
    return filtered
