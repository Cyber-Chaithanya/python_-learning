from __future__ import annotations

import contextlib
import io
import os
import re
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, FancyArrowPatch, Polygon
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
ASSETS = OUT / "diagrams"
DOCX_PATH = OUT / "Python_OOP_Complete_Master_Guide.docx"
NAVY = "15324B"
TEAL = "168C8C"
ORANGE = "E99838"
PALE = "EAF4F4"
INK = "263746"


def box(ax, xy, text, color="#168c8c", width=2.0, height=0.75, fontsize=10):
    x, y = xy
    p = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.08,rounding_size=0.12",
        linewidth=1.5,
        edgecolor=color,
        facecolor="white",
    )
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color="#15324b")


def arrow(ax, start, end, color="#168c8c", label=None):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.6,
            color=color,
            connectionstyle="arc3,rad=0.0",
        )
    )
    if label:
        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2 + 0.12,
            label,
            ha="center",
            fontsize=8,
            color="#40566b",
        )


def save_diagram(name, title, nodes, edges, xlim=(0, 10), ylim=(0, 6)):
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.set_title(title, fontsize=17, weight="bold", color=f"#{NAVY}")
    for n in nodes:
        box(ax, n["xy"], n["text"], n.get("color", f"#{TEAL}"), n.get("w", 2.0), n.get("h", 0.75), n.get("fs", 10))
    for e in edges:
        arrow(ax, e[0], e[1], e[2] if len(e) > 2 else f"#{TEAL}", e[3] if len(e) > 3 else None)
    fig.tight_layout()
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def save_project_flowchart(name, title, action, noun):
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title(title, fontsize=15, weight="bold", color=f"#{NAVY}")

    def oval(x, y, text):
        shape = Ellipse((x, y), 1.8, 0.65, facecolor="white", edgecolor=f"#{ORANGE}", linewidth=1.6)
        ax.add_patch(shape)
        ax.text(x, y, text, ha="center", va="center", fontsize=9, color=f"#{NAVY}")

    def process(x, y, text, width=3.0):
        shape = FancyBboxPatch(
            (x - width / 2, y - 0.38),
            width,
            0.76,
            boxstyle="round,pad=0.08,rounding_size=0.08",
            facecolor="white",
            edgecolor=f"#{TEAL}",
            linewidth=1.5,
        )
        ax.add_patch(shape)
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5, color=f"#{NAVY}")

    def io_shape(x, y, text, width=2.7):
        shape = Polygon(
            [(x - width / 2 + 0.25, y - 0.38), (x + width / 2, y - 0.38),
             (x + width / 2 - 0.25, y + 0.38), (x - width / 2, y + 0.38)],
            closed=True,
            facecolor="white",
            edgecolor=f"#{TEAL}",
            linewidth=1.5,
        )
        ax.add_patch(shape)
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5, color=f"#{NAVY}")

    def decision(x, y, text):
        shape = Polygon(
            [(x, y + 0.62), (x + 1.25, y), (x, y - 0.62), (x - 1.25, y)],
            closed=True,
            facecolor="white",
            edgecolor=f"#{ORANGE}",
            linewidth=1.6,
        )
        ax.add_patch(shape)
        ax.text(x, y, text, ha="center", va="center", fontsize=8, color=f"#{NAVY}")

    def connect(start, end, label=None):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                                     linewidth=1.3, color=f"#{TEAL}"))
        if label:
            ax.text((start[0] + end[0]) / 2 + 0.14,
                    (start[1] + end[1]) / 2, label, fontsize=7, color=f"#{NAVY}")

    oval(5, 9, "Start")
    io_shape(5, 7.7, f"Receive {noun}")
    decision(5, 6.1, "Valid?")
    process(5, 4.5, action, 3.5)
    io_shape(5, 2.9, "Show result")
    oval(5, 1.4, "End")
    io_shape(8.2, 5.2, "Show validation error", 2.7)
    connect((5, 8.67), (5, 8.1))
    connect((5, 7.3), (5, 6.73))
    connect((5, 5.47), (5, 4.9), "Yes")
    connect((6.25, 6.1), (6.85, 5.2))
    ax.text(6.5, 6.35, "No", fontsize=7, color=f"#{NAVY}")
    connect((5, 4.1), (5, 3.3))
    connect((5, 2.5), (5, 1.75))
    connect((8.2, 4.82), (8.2, 1.4))
    connect((8.2, 1.4), (5.9, 1.4))
    fig.tight_layout()
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def make_diagrams():
    ASSETS.mkdir(parents=True, exist_ok=True)
    diagrams = {}
    diagrams["mind_map"] = save_diagram(
        "oop_mind_map",
        "OOP: the big picture",
        [
            {"xy": (5, 3), "text": "OBJECT-ORIENTED\nPROGRAMMING", "w": 2.7, "h": 1.0},
            {"xy": (1.8, 4.7), "text": "Classes\nblueprints"},
            {"xy": (5, 5), "text": "Objects\nstate + behavior"},
            {"xy": (8.2, 4.7), "text": "Encapsulation\nprotect invariants"},
            {"xy": (1.8, 1.3), "text": "Inheritance\nreuse / specialize"},
            {"xy": (5, 1.0), "text": "Polymorphism\nsame call, varied result"},
            {"xy": (8.2, 1.3), "text": "Composition\nobjects work together"},
        ],
        [
            ((4.2, 3.55), (2.5, 4.3)),
            ((5, 3.55), (5, 4.5)),
            ((5.8, 3.55), (7.5, 4.3)),
            ((4.2, 2.45), (2.5, 1.7)),
            ((5, 2.45), (5, 1.45)),
            ((5.8, 2.45), (7.5, 1.7)),
        ],
    )
    diagrams["class_object"] = save_diagram(
        "class_and_objects",
        "One class can describe many independent objects",
        [
            {"xy": (5, 4.8), "text": "Class: Car\nbrand, year, drive()", "w": 3.0, "h": 1.0},
            {"xy": (2.3, 1.8), "text": "car_a\nbrand = 'Nova'\nyear = 2025", "w": 2.5, "h": 1.25},
            {"xy": (5, 1.8), "text": "car_b\nbrand = 'Orbit'\nyear = 2024", "w": 2.5, "h": 1.25},
            {"xy": (7.7, 1.8), "text": "car_c\nbrand = 'Pine'\nyear = 2026", "w": 2.5, "h": 1.25},
        ],
        [((4.4, 4.25), (2.8, 2.5)), ((5, 4.25), (5, 2.5)), ((5.6, 4.25), (7.2, 2.5))],
    )
    diagrams["inheritance"] = save_diagram(
        "inheritance_tree",
        "Inheritance: specialized classes build on a base class",
        [
            {"xy": (5, 4.8), "text": "Vehicle\nmove()", "w": 2.0},
            {"xy": (2.4, 1.7), "text": "Car\nhonk()", "w": 2.0},
            {"xy": (5, 1.7), "text": "Bicycle\npedal()", "w": 2.0},
            {"xy": (7.6, 1.7), "text": "Bus\nboard()", "w": 2.0},
        ],
        [((4.4, 4.4), (2.8, 2.15)), ((5, 4.4), (5, 2.15)), ((5.6, 4.4), (7.2, 2.15))],
    )
    diagrams["polymorphism"] = save_diagram(
        "polymorphism",
        "One interface, different behavior",
        [
            {"xy": (5, 4.8), "text": "for alert in alerts:\n    alert.describe()", "w": 3.3},
            {"xy": (2, 1.7), "text": "LoginAlert\ndescribe() → login details", "w": 2.6},
            {"xy": (5, 1.7), "text": "MalwareAlert\ndescribe() → file details", "w": 2.6},
            {"xy": (8, 1.7), "text": "NetworkAlert\ndescribe() → host details", "w": 2.6},
        ],
        [((4.1, 4.4), (2.7, 2.2)), ((5, 4.4), (5, 2.2)), ((5.9, 4.4), (7.3, 2.2))],
    )
    diagrams["encapsulation"] = save_diagram(
        "encapsulation",
        "Encapsulation: callers use a safe public interface",
        [
            {"xy": (1.8, 3), "text": "Caller\naccount.withdraw(20)", "w": 2.5},
            {"xy": (5, 3), "text": "BankAccount\nbalance + rules\nvalidate before update", "w": 3.2, "h": 1.2},
            {"xy": (8.2, 3), "text": "Valid state\nbalance never below 0", "w": 2.5},
        ],
        [((3.05, 3), (3.35, 3)), ((6.65, 3), (6.95, 3))],
    )
    diagrams["abstraction"] = save_diagram(
        "abstraction",
        "Abstraction: use a contract without knowing every detail",
        [
            {"xy": (5, 4.8), "text": "PaymentMethod\nabstract pay(amount)", "w": 3.1},
            {"xy": (2.5, 1.7), "text": "CardPayment\nchecks card + pays", "w": 2.6},
            {"xy": (7.5, 1.7), "text": "CashPayment\nchecks cash + pays", "w": 2.6},
        ],
        [((4.2, 4.4), (2.9, 2.15)), ((5.8, 4.4), (7.1, 2.15))],
    )
    diagrams["composition"] = save_diagram(
        "composition",
        "Composition: a cart contains and uses product objects",
        [
            {"xy": (2.2, 3), "text": "ShoppingCart", "w": 2.2},
            {"xy": (5, 4.5), "text": "CartItem\nProduct + quantity", "w": 2.4},
            {"xy": (8, 4.5), "text": "Product\nname + price", "w": 2.1},
            {"xy": (5, 1.5), "text": "CartItem\nProduct + quantity", "w": 2.4},
            {"xy": (8, 1.5), "text": "Product\nname + price", "w": 2.1},
        ],
        [
            ((3.25, 3.25), (3.9, 4.25), f"#{TEAL}", "has"),
            ((3.25, 2.75), (3.9, 1.75), f"#{TEAL}", "has"),
            ((6.2, 4.5), (6.95, 4.5), f"#{ORANGE}", "refers to"),
            ((6.2, 1.5), (6.95, 1.5), f"#{ORANGE}", "refers to"),
        ],
    )
    diagrams["lifecycle"] = save_diagram(
        "object_lifecycle",
        "Creating an object: Python allocates, then initializes",
        [
            {"xy": (1.6, 3), "text": "Car('Nova', 2025)", "w": 2.0},
            {"xy": (4.1, 3), "text": "__new__()\ncreates instance", "w": 2.1},
            {"xy": (6.8, 3), "text": "__init__()\nsets attributes", "w": 2.1},
            {"xy": (9.1, 3), "text": "Ready object\ncar.brand = 'Nova'", "w": 2.2},
        ],
        [((2.6, 3), (3.0, 3)), ((5.2, 3), (5.7, 3)), ((7.9, 3), (8.0, 3))],
        (0, 10),
        (0, 6),
    )
    flowcharts = [
        ("student_flow", "Student manager: add, calculate, display", "Store student", "student details and marks"),
        ("bank_flow", "Bank account: validate, then change balance", "Update balance and history", "deposit or withdrawal"),
        ("library_flow", "Library: borrow only an available book", "Update book availability", "borrow or return request"),
        ("cart_flow", "Shopping cart: update items, then total", "Update cart quantity", "product and quantity"),
        ("security_flow", "Alert manager: validate, store, filter", "Store and filter alert", "alert details"),
    ]
    for name, title, action, noun in flowcharts:
        diagrams[name] = save_project_flowchart(name, title, action, noun)
    project_classes = [
        (
            "student_classes",
            "Student manager: class responsibilities",
            [
                {"xy": (2.5, 3), "text": "Student\nname · marks\naverage() · report()", "w": 3.0, "h": 1.25},
                {"xy": (7.5, 3), "text": "Student list\nmany Student objects", "w": 3.0, "h": 1.0},
            ],
            [((4.0, 3), (6.0, 3), f"#{TEAL}", "contains")],
        ),
        (
            "bank_classes",
            "Bank: account state and transaction record",
            [
                {"xy": (2.5, 3), "text": "BankAccount\nowner · balance\n deposit() · withdraw()", "w": 3.2, "h": 1.25},
                {"xy": (7.5, 3), "text": "History\nsuccessful transactions", "w": 3.0, "h": 1.0},
            ],
            [((4.1, 3), (6.0, 3), f"#{TEAL}", "records")],
        ),
        (
            "library_classes",
            "Library: manages a collection of Book objects",
            [
                {"xy": (2.5, 3), "text": "Library\nadd · borrow · return", "w": 3.0, "h": 1.0},
                {"xy": (7.5, 3), "text": "Book\ntitle · author\navailability", "w": 2.8, "h": 1.1},
            ],
            [((4.0, 3), (6.1, 3), f"#{TEAL}", "stores")],
        ),
        (
            "cart_classes",
            "Cart: product references and quantities",
            [
                {"xy": (1.8, 3), "text": "ShoppingCart\nadd · remove · total", "w": 2.8, "h": 1.05},
                {"xy": (5.0, 3), "text": "items\nProduct → quantity", "w": 2.5, "h": 1.0},
                {"xy": (8.2, 3), "text": "Product\nname · price", "w": 2.3, "h": 0.9},
            ],
            [((3.2, 3), (3.75, 3), f"#{TEAL}", "contains"), ((6.25, 3), (7.0, 3), f"#{ORANGE}", "refers to")],
        ),
        (
            "security_classes",
            "Alert manager: validated records can be filtered",
            [
                {"xy": (1.8, 3), "text": "AlertManager\nadd · by_severity", "w": 2.8, "h": 1.05},
                {"xy": (5.0, 3), "text": "SecurityAlert\ntitle · severity · source", "w": 3.0, "h": 1.0},
                {"xy": (8.3, 3), "text": "describe()\nshared operation", "w": 2.5, "h": 1.0},
            ],
            [((3.2, 3), (3.5, 3), f"#{TEAL}", "stores"), ((6.5, 3), (7.0, 3), f"#{ORANGE}", "calls")],
        ),
    ]
    for name, title, nodes, edges in project_classes:
        diagrams[name] = save_diagram(name, title, nodes, edges, (0, 10), (0, 6))
    return diagrams


CHAPTERS = [
    {
        "part": "PART 1 · BUILDING THE FOUNDATION",
        "title": "Introduction to Programming and OOP",
        "topics": [
            ("Programming and Python", "Programming means writing precise instructions a computer can follow. A programming language gives people a readable way to express those instructions. Python is a general-purpose language known for readable syntax; it is used in education, automation, web services, science, and defensive security tooling."),
            ("Procedural programming", "A procedural program is organized mainly as steps and functions. This is an excellent fit for short scripts and simple transformations. As a program grows, related data and the functions that operate on it can become scattered."),
            ("What OOP adds", "Object-Oriented Programming groups related data (state) and operations (behavior) into objects. A class describes the kind of object; each object holds its own state. OOP is a way to organize programs, not a requirement for every Python task."),
            ("Why use it—and when not to", "OOP can make a large domain easier to model, reuse, test, and extend. It also adds structure and vocabulary; for a five-line calculation, a function may be clearer. Choose the simplest design that keeps the program understandable."),
            ("Procedural versus OOP", "Procedural style emphasizes operations; OOP emphasizes collaborating objects. Neither style is automatically faster or better. Python supports both, and real programs often combine functions and classes."),
        ],
        "code": """class Counter:
    def __init__(self):
        self.value = 0

    def add_one(self):
        self.value += 1


counter = Counter()
counter.add_one()
print(counter.value)""",
        "output": "1",
        "walk": "Counter is the class, counter is one object. add_one changes that object's value. The same task could be written with a plain integer and a function; the class becomes helpful when the counter needs more state or behavior.",
        "diagram": "mind_map",
        "analogy": "A recipe card is a plan; the baked cake is a finished thing. A class is like the recipe and an object is a particular cake made from it.",
        "mistake": "Starting every tiny script with several classes can hide a simple solution. Prefer a function or a few statements until there is a clear group of state and behavior.",
        "terms": "Programming language: a notation for instructions. Procedure: an ordered set of steps. OOP: organizing state and behavior around objects. State: the data an object currently holds.",
    },
    {
        "part": "PART 1 · BUILDING THE FOUNDATION",
        "title": "Understanding Classes and Objects",
        "topics": [
            ("A class is a description", "A class defines what data and operations instances of a kind can have. It is not itself a car, student, or phone; it describes how such objects behave."),
            ("An object is an instance", "An object is a particular value created from a class. Many objects can use the same class while keeping different instance attributes."),
            ("Identity and independent state", "Each object has an identity: it is a particular object in memory. Two cars can have equal data yet remain separate objects. Changing one object's instance attribute does not normally change another's."),
            ("Attributes and behavior", "An attribute is a named value associated with an object or class. A method is a function defined on a class that describes behavior. A phone's model is data; calling phone.call() is behavior."),
            ("Student, car, and phone models", "A Student could have a name and marks; a Car a brand and year; a Phone a model and battery level. Model only information and actions that matter to the program."),
        ],
        "code": """class Car:
    def __init__(self, brand, year):
        self.brand = brand
        self.year = year


car_a = Car("Nova", 2025)
car_b = Car("Orbit", 2024)
print(car_a.brand, car_a.year)
print(car_b.brand, car_b.year)
print(car_a is car_b)""",
        "output": "Nova 2025\nOrbit 2024\nFalse",
        "walk": "Car describes a kind of object. Calling Car(...) creates one instance and passes its values to __init__. car_a and car_b refer to distinct objects, so `is` is False.",
        "diagram": "class_object",
        "analogy": "A school form is a template. Each completed student record is an object with its own name and class.",
        "mistake": "Writing `car = Car` stores the class itself. Use parentheses, such as `car = Car('Nova', 2025)`, to make an instance.",
        "terms": "Class: a definition used to create instances. Instance: an object created from a class. Identity: which particular object something is. Attribute: a named value.",
    },
    {
        "part": "PART 1 · BUILDING THE FOUNDATION",
        "title": "Attributes, Methods, and Object State",
        "topics": [
            ("Instance attributes", "An instance attribute belongs to one object. Assign it through self inside a method, or through the object from outside. Each object can hold a different value."),
            ("Class attributes", "A class attribute is defined directly in the class body and is looked up through the class or instances. It is useful for genuinely shared facts such as a common tax rate, not per-student marks."),
            ("Methods and state changes", "An instance method receives the object as its first argument by convention, then can read or update its attributes. A method that updates state should make the change clear and keep the object valid."),
            ("Class data versus per-object data", "If a mutable list is placed directly on a class, all instances can see and mutate that same list. Put per-object collections in __init__ so every instance receives its own list."),
        ],
        "code": """class Student:
    school = "Maple School"

    def __init__(self, name):
        self.name = name
        self.marks = []

    def add_mark(self, mark):
        self.marks.append(mark)


ada = Student("Ada")
lin = Student("Lin")
ada.add_mark(95)
print(ada.name, ada.marks, ada.school)
print(lin.name, lin.marks, lin.school)""",
        "output": "Ada [95] Maple School\nLin [] Maple School",
        "walk": "school is shared class information; name and marks belong to each student. Creating `marks` inside __init__ gives Ada and Lin separate lists.",
        "diagram": "class_object",
        "analogy": "A classroom has one shared school name but each student's notebook is personal. Shared facts belong to the class; individual facts belong to each instance.",
        "mistake": "Do not put `marks = []` in the class body if each student needs different marks. That creates one shared list.",
        "terms": "Instance attribute: per-object data. Class attribute: class-level data. Method: function defined in a class. State: current attribute values.",
    },
    {
        "part": "PART 2 · THE CORE OF PYTHON OOP",
        "title": "The __init__() Method and Constructors",
        "topics": [
            ("Initializing a useful object", "__init__ is an initializer: Python calls it after a new instance has been allocated. It commonly sets the attributes that make an object ready to use."),
            ("Parameters and defaults", "Initializer parameters let each instance start with different data. A default parameter makes an argument optional when that default is meaningful. Avoid mutable defaults such as `items=[]`; use None or a fresh list instead."),
            ("Creation versus initialization", "Technically, __new__ creates and returns the instance; __init__ initializes it. Most everyday classes should implement __init__ only. __new__ is an advanced hook used in special cases such as immutable subclasses."),
            ("Lifecycle", "The call `Car('Nova', 2025)` asks Python to construct an instance and then initialize it. The resulting reference can be stored in a variable and used to call methods."),
        ],
        "code": """class Car:
    def __init__(self, brand, year=2025):
        self.brand = brand
        self.year = year


new_car = Car("Nova")
older_car = Car("Orbit", 2022)
print(new_car.brand, new_car.year)
print(older_car.brand, older_car.year)""",
        "output": "Nova 2025\nOrbit 2022",
        "walk": "Python sends `brand` and `year` into __init__. The first object uses the default year, while the second supplies one explicitly.",
        "diagram": "lifecycle",
        "analogy": "A factory first makes an empty product shell, then configures it with a model and serial number. __new__ is the rare creation hook; __init__ sets it up.",
        "mistake": "The method name must be exactly `__init__` with two underscores on each side. `__init` is a different name and will not be called automatically.",
        "terms": "__init__: initializer method. __new__: method that creates an instance. Default argument: a value used when a caller omits an argument. Constructor is often used informally for object setup.",
    },
    {
        "part": "PART 2 · THE CORE OF PYTHON OOP",
        "title": "Understanding self Properly",
        "topics": [
            ("What self means", "self refers to the particular instance on which an instance method is called. Python supplies it when you write `object.method(...)`. The name self is conventional, not a reserved keyword."),
            ("Attribute access", "Use `self.name` to access the object's name. A local variable called name exists only while a function runs; `self.name` is stored on the object and can be used by later method calls."),
            ("Binding a method", "When `student.describe()` is called, Python binds student as the method's first argument. The method definition includes the self parameter so it can work with that specific instance."),
            ("Why omission fails", "Without the first parameter, an instance method's automatic instance argument has nowhere to go, usually causing a TypeError. Use self as the first parameter for ordinary instance methods."),
        ],
        "code": """class Student:
    def __init__(self, name):
        self.name = name

    def greet(self, greeting):
        return f"{greeting}, I am {self.name}."


student = Student("Ada")
print(student.greet("Hello"))""",
        "output": "Hello, I am Ada.",
        "walk": "student.greet('Hello') is conceptually like calling Student.greet(student, 'Hello'). self is Ada's student object; greeting is the ordinary argument.",
        "diagram": "class_object",
        "analogy": "When a shop assistant says “this order,” the word this identifies the current order. self plays that role inside an instance method.",
        "mistake": "A method written as `def greet():` will fail when called as `student.greet()` because Python still supplies the instance. Add `self`.",
        "terms": "self: conventional name for the current instance parameter. Bound method: a method connected to a particular instance. Local variable: a temporary name inside a function.",
    },
    {
        "part": "PART 2 · THE CORE OF PYTHON OOP",
        "title": "Instance, Class, and Static Methods",
        "topics": [
            ("Instance methods", "An instance method's first parameter is usually self. Use it when behavior needs the current object's attributes or needs to change that object."),
            ("Class methods", "A method decorated with @classmethod receives the class as its first parameter, conventionally cls. It can read class-level information or serve as an alternative constructor that respects subclasses."),
            ("Static methods", "A @staticmethod receives no automatic self or cls. Use it for a small utility closely related to the class concept but not requiring object or class state."),
            ("Choosing the method type", "If behavior needs one object's state, choose an instance method. If it needs the class or constructs an instance through cls, choose a class method. If it needs neither, a static method or module-level function may be clearer."),
        ],
        "code": """class Temperature:
    unit = "C"

    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, value):
        return cls((value - 32) * 5 / 9)

    @staticmethod
    def is_valid(value):
        return isinstance(value, (int, float))


temp = Temperature.from_fahrenheit(68)
print(round(temp.celsius))
print(Temperature.is_valid(20))""",
        "output": "20\nTrue",
        "walk": "The class method converts Fahrenheit and creates an instance through cls. The static method checks a value without needing a particular Temperature object.",
        "diagram": None,
        "analogy": "Instance method: ask one student for their score. Class method: ask the school class to make a student record. Static method: use a related calculator that needs no student's data.",
        "mistake": "Do not forget @classmethod or cls: without the decorator Python does not supply the class. Do not use @staticmethod when the method needs self.",
        "terms": "@classmethod and @staticmethod are decorators. Decorator: syntax that modifies or registers a function's behavior. cls: conventional class-method parameter.",
    },
    {
        "part": "PART 2 · THE CORE OF PYTHON OOP",
        "title": "Encapsulation and Data Protection",
        "topics": [
            ("Encapsulation", "Encapsulation places related state and behavior together and provides a clear interface for using them. A bank account can expose deposit and withdraw rather than asking callers to edit its balance carelessly."),
            ("Python visibility conventions", "A public name has no leading underscore. A leading underscore, such as `_balance`, signals “internal use; callers should not rely on this.” Python does not enforce strict private access."),
            ("Name mangling", "A double-leading underscore such as `__pin` triggers name mangling, which helps avoid accidental name clashes in subclasses. It is not a security boundary and can still be accessed deliberately."),
            ("Properties and validation", "@property lets code use attribute-like access while a method controls reading or assignment. A setter can reject invalid data so an object remains in a valid state."),
            ("Encapsulation versus abstraction", "Encapsulation concerns bundling state and behavior and controlling access. Abstraction concerns showing essential operations while hiding implementation details. They often work together but are not synonyms."),
        ],
        "code": """class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, amount):
        if amount < 0:
            raise ValueError("balance cannot be negative")
        self._balance = amount

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount


account = BankAccount(50)
account.deposit(25)
print(account.balance)""",
        "output": "75",
        "walk": "The property validates initial balance assignments and provides a readable public balance. deposit checks its own rule before changing the internal attribute.",
        "diagram": "encapsulation",
        "analogy": "A vending machine shows buttons and accepts payment, but users do not reach inside to directly change its inventory counters.",
        "mistake": "Do not claim `_balance` is truly private. It is a convention; the goal is clear API design, not secrecy.",
        "terms": "Encapsulation: group state and behavior with a controlled interface. Property: managed attribute access. Name mangling: renaming of double-leading-underscore attributes. Invariant: rule that should remain true.",
    },
    {
        "part": "PART 2 · THE CORE OF PYTHON OOP",
        "title": "Inheritance",
        "topics": [
            ("Base and derived classes", "Inheritance creates a specialized class from a base class. The child inherits usable behavior and can add or replace behavior. Think “Car is a Vehicle,” not merely “Car uses a Vehicle.”"),
            ("Common shapes", "Single inheritance has one direct parent; multilevel inheritance forms a chain; hierarchical inheritance has multiple children from one parent; multiple inheritance has more than one base class."),
            ("Overriding and super()", "A subclass overrides a method by defining the same method name. `super()` delegates to the next implementation in the method resolution order, allowing a subclass to extend parent behavior without naming the parent directly."),
            ("MRO and the diamond", "Python computes a Method Resolution Order (MRO) to decide where to find methods. In a diamond-shaped hierarchy, C3 linearization gives a consistent order and cooperative super() calls proceed through it."),
            ("Inheritance or composition?", "Use inheritance for a genuine substitutable “is-a” relationship. If a class merely uses another object (“has-a”), composition is often simpler and more flexible."),
        ],
        "code": """class Vehicle:
    def __init__(self, brand):
        self.brand = brand

    def move(self):
        return f"{self.brand} moves"


class Car(Vehicle):
    def move(self):
        return f"{super().move()} on four wheels"


car = Car("Nova")
print(car.move())
print(Car.mro()[0].__name__, Car.mro()[1].__name__)""",
        "output": "Nova moves on four wheels\nCar Vehicle",
        "walk": "Car inherits Vehicle's initializer. Its move method overrides Vehicle.move and calls the parent implementation with super before adding its detail. mro() shows lookup order.",
        "diagram": "inheritance",
        "analogy": "A car is a vehicle and can be used wherever a vehicle is expected. A car has an engine; that relationship is usually modeled by holding an Engine object, not inheriting from Engine.",
        "mistake": "Avoid deep inheritance trees and subclasses that cannot honor the behavior promised by the parent. Prefer a composed helper when the relationship is “has-a.”",
        "terms": "Base/parent class: class being extended. Derived/child class: subclass. Override: replace inherited method behavior. MRO: ordered lookup path. super(): cooperative next-class access.",
    },
    {
        "part": "PART 2 · THE CORE OF PYTHON OOP",
        "title": "Polymorphism",
        "topics": [
            ("One operation, varied behavior", "Polymorphism means that a common operation can work with different kinds of objects, with each object providing appropriate behavior. For example, different alerts can each describe themselves."),
            ("Overriding and duck typing", "Overriding supplies a subclass-specific implementation. Duck typing is Python's practice of caring about supported operations rather than requiring an object's declared class. They are related tools but not identical concepts."),
            ("Functions and loops", "A function can accept any object that supports the operations it uses. This keeps callers simple and lets new compatible classes work without rewriting the loop."),
            ("Operator overloading", "Special methods such as __add__ and __len__ let custom objects participate in familiar operations. Implement an operation only when its meaning for the type is clear."),
            ("Overloading terminology", "Python does not offer traditional signature-based method overloading like some languages. Re-defining the same method name in a class replaces the earlier definition; optional arguments or singledispatch patterns are alternatives."),
        ],
        "code": """class LoginAlert:
    def describe(self):
        return "Login alert: review sign-in activity"


class FileAlert:
    def describe(self):
        return "File alert: review the flagged file"


def print_alert(alert):
    print(alert.describe())


for item in (LoginAlert(), FileAlert()):
    print_alert(item)""",
        "output": "Login alert: review sign-in activity\nFile alert: review the flagged file",
        "walk": "print_alert needs only an object with describe(). Both alert types meet that expectation and choose their own message.",
        "diagram": "polymorphism",
        "analogy": "A play button means “start” on a music player and a video player, even though each device starts different media.",
        "mistake": "Polymorphism is not simply “many classes.” The key is a shared operation or interface with behavior suitable to each object.",
        "terms": "Polymorphism: one interface usable with different implementations. Duck typing: compatibility based on supported behavior. Operator overloading: defining how standard operators work for a type.",
    },
    {
        "part": "PART 2 · THE CORE OF PYTHON OOP",
        "title": "Abstraction and Abstract Classes",
        "topics": [
            ("Essential behavior, hidden detail", "Abstraction exposes what a user of a class needs to do and leaves implementation details behind the interface. A driver uses a steering wheel and pedals without needing the engine's internal design."),
            ("Abstract contracts", "The abc module provides ABC and @abstractmethod. An abstract base class can define required methods; Python normally prevents instantiating it until a concrete subclass implements them."),
            ("Abstraction and encapsulation", "Abstraction simplifies what callers need to know. Encapsulation groups state and behavior and controls access to that state. One design can use both."),
            ("When useful", "Use an abstract base class when several implementations must honor a meaningful contract and the shared contract improves clarity. For a small one-off script, a simple function or duck-typed object may be enough."),
        ],
        "code": """from abc import ABC, abstractmethod


class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount):
        raise NotImplementedError


class CashPayment(PaymentMethod):
    def pay(self, amount):
        return f"Paid ${amount:.2f} in cash"


print(CashPayment().pay(12))""",
        "output": "Paid $12.00 in cash",
        "walk": "PaymentMethod documents the required pay operation. CashPayment fulfills it, so it can be instantiated. PaymentMethod itself is incomplete.",
        "diagram": "abstraction",
        "analogy": "A USB socket specifies how a device connects; a camera and keyboard can implement the connection differently.",
        "mistake": "A subclass that forgets an inherited abstract method remains abstract and cannot normally be instantiated.",
        "terms": "Abstraction: expose essential operations and hide detail. ABC: abstract base class. @abstractmethod: marks a method subclasses are expected to implement.",
    },
    {
        "part": "PART 3 · ADVANCED OBJECT BEHAVIOR",
        "title": "Special or Magic Methods",
        "topics": [
            ("Dunder methods", "Methods with double underscores at both ends are special methods. Python calls many of them in response to ordinary syntax, such as str(obj), len(obj), comparison, addition, or calling an object."),
            ("Useful methods", "__init__ initializes. __str__ provides a friendly display. __repr__ aims for a useful developer representation. __len__ supports len(). __eq__ defines equality. __add__ defines +. __call__ makes an instance callable."),
            ("Use the operation, not usually the dunder call", "Call `str(book)`, `len(shelf)`, or `left + right`; Python routes these operations to the corresponding special methods. Implementations should obey expected conventions, including useful return types."),
            ("Equality and representation", "A class should define equality only when its notion of equal values is meaningful. A useful repr helps debugging; a useful str helps people reading output."),
        ],
        "code": """class Book:
    def __init__(self, title):
        self.title = title

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Book({self.title!r})"

    def __len__(self):
        return len(self.title)


book = Book("Python")
print(str(book))
print(repr(book))
print(len(book))""",
        "output": "Python\nBook('Python')\n6",
        "walk": "str(book) calls __str__, repr(book) calls __repr__, and len(book) calls __len__. All three special methods return the type expected by their operation.",
        "diagram": None,
        "analogy": "A remote's power button is ordinary to the user; inside, a specific circuit responds. Special methods connect familiar Python operations to a class's response.",
        "mistake": "Returning a number from __str__ is invalid: __str__ must return a string. Use len(obj) rather than obj.__len__() in normal code.",
        "terms": "Dunder: informal name for double-underscore method. __repr__: developer-oriented representation. __str__: readable string. Operator overloading: special-method behavior for operators.",
    },
    {
        "part": "PART 3 · ADVANCED OBJECT BEHAVIOR",
        "title": "Composition, Aggregation, and Association",
        "topics": [
            ("Objects that work together", "Association is a broad relationship where objects know about or use each other. Aggregation often describes a group holding references to independently meaningful objects. Composition describes a stronger “part of” relationship."),
            ("Has-a versus is-a", "A library has books; a shopping cart has cart items. A Car is a Vehicle. Use composition for has-a and inheritance for a well-founded is-a relationship."),
            ("Ownership is a design idea", "Python references do not automatically enforce UML-style ownership. A part can be shared, retained elsewhere, or outlive a container if another reference exists. Define lifetime and ownership expectations in the program design."),
            ("Why composition is flexible", "A cart can use a pricing strategy or product objects without inheriting their behavior. Components can be replaced, tested, and reused independently."),
        ],
        "code": """class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Cart:
    def __init__(self):
        self.products = []

    def add(self, product):
        self.products.append(product)

    def total(self):
        return sum(product.price for product in self.products)


cart = Cart()
cart.add(Product("Notebook", 3.50))
cart.add(Product("Pen", 1.50))
print(f"${cart.total():.2f}")""",
        "output": "$5.00",
        "walk": "Cart stores references to Product objects and asks each for its price. Product does not inherit from Cart; the relationship is has-a.",
        "diagram": "composition",
        "analogy": "A school class roster is associated with students. A toolbox contains tools, but a tool can also be taken out and used elsewhere. These relations have different ownership strengths.",
        "mistake": "Do not present composition and aggregation as automatically enforced Python ownership rules. They are design descriptions of relationships.",
        "terms": "Association: objects are related. Aggregation: weaker whole-part relationship. Composition: stronger whole-part design. Has-a: object contains or uses another object. Is-a: subtype relationship.",
    },
    {
        "part": "PART 3 · ADVANCED OBJECT BEHAVIOR",
        "title": "Object References, Identity, and Copying",
        "topics": [
            ("Names refer to objects", "A Python variable is a name bound to an object, not a box that automatically contains an independent copy. Assigning `second = first` makes both names refer to the same object."),
            ("Identity and equality", "`is` asks whether two references point to the same object. `==` asks whether values are equal according to their equality behavior. Use `is None` for the None singleton; usually use == for values."),
            ("Mutable and immutable values", "Lists and dictionaries are mutable; they can change in place. Integers and strings are immutable values. Aliasing a mutable object means a change through one name can be seen through another."),
            ("Shallow and deep copy", "copy.copy makes a shallow copy: the outer container is new, but nested objects may still be shared. copy.deepcopy recursively copies nested data as far as supported. Deep copying can be expensive or inappropriate for resources."),
        ],
        "code": """import copy

first = [[1], [2]]
shallow = copy.copy(first)
deep = copy.deepcopy(first)
shallow[0].append(9)
print(first)
print(deep)
print(first is shallow, first == shallow)""",
        "output": "[[1, 9], [2]]\n[[1], [2]]\nFalse True",
        "walk": "The shallow copy has a new outer list but shares its nested lists with first, so the append is visible in first. The deep copy has independent nested lists.",
        "diagram": None,
        "analogy": "Two students can share the same notebook (aliasing) or each receive a copied notebook. A photocopy of a folder cover alone still points to the same pages inside (shallow copy).",
        "mistake": "Do not use `is` to compare numbers or strings for value equality. Use == unless you explicitly mean object identity.",
        "terms": "Reference: a way to access an object. Aliasing: multiple names refer to one object. Mutable: can change in place. Shallow copy: copies outer container. Deep copy: recursively copies nested structure.",
    },
    {
        "part": "PART 3 · ADVANCED OBJECT BEHAVIOR",
        "title": "Properties, Validation, and Better Class Design",
        "topics": [
            ("Properties as a stable interface", "@property makes a method appear attribute-like. You can later add validation or computed behavior without changing callers from `student.age` to `student.get_age()`."),
            ("Setters, deleters, and read-only values", "A property setter validates updates; a deleter can define whether removal is allowed. A property with no setter is read-only through that interface, though Python's conventions do not make all state inaccessible."),
            ("Maintain valid state", "Validate at the boundary where data enters the object. Raise a clear exception for invalid input rather than silently storing a value that breaks later operations."),
            ("Design for maintainability", "Give a class a focused responsibility, meaningful names, and a small public interface. Keep implementation details replaceable and avoid exposing mutable internals unnecessarily."),
        ],
        "code": """class Student:
    def __init__(self, age):
        self.age = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("age must be a non-negative integer")
        self._age = value


student = Student(15)
student.age = 16
print(student.age)""",
        "output": "16",
        "walk": "Both initialization and later assignment pass through the same setter. Valid ages are stored as _age; invalid values raise ValueError.",
        "diagram": "encapsulation",
        "analogy": "A school office accepts a student's age only after checking it is sensible; the student record stays valid after every update.",
        "mistake": "A setter that assigns `self.age = value` calls itself repeatedly. Store in a differently named internal attribute, such as `_age`.",
        "terms": "Property: controlled attribute-like access. Setter: property method for assignment. Read-only property: property without setter. Invariant: a condition the class preserves.",
    },
    {
        "part": "PART 3 · ADVANCED OBJECT BEHAVIOR",
        "title": "Dataclasses and Type Hints",
        "topics": [
            ("Reducing repetitive code", "A plain data record often needs an initializer, representation, and equality behavior. @dataclass can generate these methods from declared fields."),
            ("Annotations and fields", "Type hints document intended types and help editors and static checkers. Python generally does not enforce annotations at runtime. field() configures a dataclass field; default_factory creates a fresh value for each instance."),
            ("Mutable default trap", "Do not use a shared list as a default field value. Use `field(default_factory=list)` to give every instance a new list."),
            ("Choosing a dataclass", "Dataclasses are useful for records that mostly hold data. A regular class is suitable when initialization, invariants, or behavior needs a more tailored design."),
        ],
        "code": """from dataclasses import dataclass, field


@dataclass
class Student:
    name: str
    marks: list[int] = field(default_factory=list)


ada = Student("Ada")
lin = Student("Lin")
ada.marks.append(95)
print(ada)
print(lin.marks)""",
        "output": "Student(name='Ada', marks=[95])\n[]",
        "walk": "The decorator generates an initializer and useful representation. The default_factory gives ada and lin independent lists. `list[int]` documents the intended element type.",
        "diagram": None,
        "analogy": "A standard form automatically fills common labels and formatting; the data class generates repetitive record methods from field declarations.",
        "mistake": "Annotations are not a runtime validation system. If values must be checked, add explicit validation or use a suitable validation library.",
        "terms": "@dataclass: decorator that generates methods. Annotation: type or meaning hint. field(): field configuration. default_factory: callable that creates a fresh default.",
    },
    {
        "part": "PART 3 · ADVANCED OBJECT BEHAVIOR",
        "title": "Exception Handling Inside Classes",
        "topics": [
            ("Exceptions signal errors", "An exception is an object that reports an unusual condition. Classes should reject invalid actions clearly instead of returning misleading success values."),
            ("Handling and raising", "try contains risky work; except handles selected exception types; else runs when no exception occurred; finally runs whether or not an exception occurred. Use raise to report a violated rule."),
            ("Meaningful custom errors", "A custom exception can name a domain failure, such as InsufficientFundsError. Derive it from Exception or an appropriate built-in exception and document when it is raised."),
            ("Valid object states", "Check a deposit amount before updating a balance. Validate first, then mutate. This avoids leaving an object partly updated after failure."),
        ],
        "code": """class InsufficientFundsError(Exception):
    pass


class Account:
    def __init__(self, balance=0):
        self.balance = balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise InsufficientFundsError("not enough funds")
        self.balance -= amount


account = Account(40)
try:
    account.withdraw(50)
except InsufficientFundsError as error:
    print(error)
print(account.balance)""",
        "output": "not enough funds\n40",
        "walk": "The withdrawal detects insufficient funds before changing balance. The caller catches the specific exception and the account remains unchanged.",
        "diagram": None,
        "analogy": "A cashier refuses a withdrawal that exceeds the account balance and explains why; the balance is not partially changed.",
        "mistake": "Avoid a bare `except:` that hides unrelated bugs. Catch only errors the code can meaningfully handle.",
        "terms": "Exception: object representing an error condition. raise: signal an exception. try/except: handle expected errors. Custom exception: domain-specific exception class.",
    },
    {
        "part": "PART 3 · ADVANCED OBJECT BEHAVIOR",
        "title": "Iterators, Generators, and Context Managers",
        "topics": [
            ("Iteration protocol", "An iterator provides one value at a time. __iter__ returns an iterator; __next__ returns the next value and raises StopIteration when finished. A for loop handles the protocol for you."),
            ("Generators", "A generator function uses yield to produce values lazily. The next value is created when requested, which can avoid storing a whole sequence."),
            ("Context managers", "A context manager defines setup and cleanup around a `with` block using __enter__ and __exit__. This is useful for files and other resources that must be released reliably."),
            ("Keep the feature appropriate", "Use built-in iteration and context managers where possible. Custom protocols are useful when the object naturally represents a sequence or managed resource."),
        ],
        "code": """class CountUpTo:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        self.current += 1
        return self.current


print(list(CountUpTo(3)))""",
        "output": "[1, 2, 3]",
        "walk": "iter() obtains the iterator and each next() call advances current. Once it reaches limit, StopIteration tells the list constructor to stop.",
        "diagram": None,
        "analogy": "A ticket dispenser hands out one numbered ticket each time someone asks. A context manager is like borrowing a library room and ensuring it is locked after use.",
        "mistake": "An iterator that never raises StopIteration can make loops run forever. Ensure the end condition is correct.",
        "terms": "Iterable: object that can provide an iterator. Iterator: object that yields successive values. Generator: iterator-producing function using yield. Context manager: object that manages a with-block lifecycle.",
    },
    {
        "part": "PART 3 · ADVANCED OBJECT BEHAVIOR",
        "title": "SOLID Principles and Clean OOP Design",
        "topics": [
            ("S — Single Responsibility", "A class should have one coherent reason to change. Analogy: a librarian organizes books; a separate printer prints receipts. A class that validates students, saves files, and formats reports is hard to change safely."),
            ("O — Open/Closed", "Design so new behavior can often be added without rewriting stable code. Prefer adding a new alert type that implements describe() over editing a long if/elif chain for every new type."),
            ("L — Liskov Substitution", "A subtype should work anywhere its base type is expected without surprising failures. If a subclass changes a promised operation's meaning or preconditions, callers cannot safely substitute it."),
            ("I — Interface Segregation", "Prefer small, focused interfaces to one large interface that forces classes to implement irrelevant methods. A simple printer should not need scan() and fax() just because another machine has them."),
            ("D — Dependency Inversion", "High-level policy should depend on a small abstraction rather than a concrete detail where that reduces coupling. A report can receive a saver object with a save() method instead of constructing a file backend inside itself."),
            ("Guidelines, not laws", "SOLID is a set of design heuristics, not Python language rules. Apply a principle when it clarifies likely change; do not add layers without a real need."),
        ],
        "code": """class ConsoleSaver:
    def save(self, text):
        print(f"Saved: {text}")


class Report:
    def __init__(self, saver):
        self.saver = saver

    def publish(self, text):
        self.saver.save(text)


Report(ConsoleSaver()).publish("Weekly summary")""",
        "output": "Saved: Weekly summary",
        "walk": "Report depends on the small save() behavior, not on a specific storage implementation. A different saver can be supplied without changing Report.",
        "diagram": None,
        "analogy": "A charger uses a standard plug shape rather than being permanently attached to one power station; an interface keeps components replaceable.",
        "mistake": "Do not turn every two-line program into a framework to satisfy SOLID. The aim is change-friendly code, not maximum abstraction.",
        "terms": "Responsibility: a coherent job owned by a module or class. Interface: the operations a collaborator promises. Dependency: a component another component uses. Coupling: how strongly components rely on details.",
    },
    {
        "part": "PART 4 · PUTTING EVERYTHING INTO PRACTICE",
        "title": "Complete OOP Mini Projects",
        "topics": [
            ("Project 1 — Student management", "Store student identity and marks; calculate averages; reject invalid marks; create several independent student records."),
            ("Project 2 — Bank account simulator", "Deposit and withdraw safely, retain transaction history, and raise a domain-specific error for an insufficient balance."),
            ("Project 3 — Library manager", "Model books and a library; borrow only available titles; return a borrowed title; keep the book and library responsibilities distinct."),
            ("Project 4 — Online shopping cart", "Represent products and quantities; add, remove, and total items. A cart contains line items referring to products."),
            ("Project 5 — Defensive security alert manager", "Represent validated alerts of different severities and types; use polymorphic descriptions and filter records. This is a defensive record-keeping example, not an attack workflow."),
            ("Build-test-improve loop", "For each project: clarify inputs, model objects, implement one method at a time, run normal and invalid cases, then consider extensions. No database or external service is needed."),
        ],
        "code": """class SecurityAlert:
    def __init__(self, title, severity):
        allowed = {"low", "medium", "high"}
        if severity not in allowed:
            raise ValueError("unsupported severity")
        self.title = title
        self.severity = severity

    def describe(self):
        return f"[{self.severity.upper()}] {self.title}"


alerts = [SecurityAlert("Repeated login failures", "medium")]
for alert in alerts:
    print(alert.describe())""",
        "output": "[MEDIUM] Repeated login failures",
        "walk": "The class validates a security record's severity. The list stores multiple objects; a loop calls the common describe() behavior. All examples are safe, defensive record handling.",
        "diagram": "security_flow",
        "analogy": "An incident desk receives standardized reports, checks that each severity is valid, and lets different report types describe their findings.",
        "mistake": "A record of an alert is not itself a detection system. Do not confuse modeling a report with inspecting systems or performing security actions.",
        "terms": "Validation: checking input rules. Transaction history: ordered record of changes. Polymorphism: common operation supported by varied types. Defensive security: protecting and monitoring authorized systems.",
    },
    {
        "part": "PART 5 · REVISION AND MASTERY",
        "title": "OOP Comparison and Revision",
        "topics": [
            ("Class versus object", "A class describes a kind of instance; an object is one concrete instance. One class can create many distinct objects."),
            ("Attribute versus method", "An attribute stores or exposes a value; a method performs an operation. An instance method typically receives self."),
            ("Method and data comparisons", "Instance attributes belong to one object; class attributes belong to the class. self refers to an instance; cls conventionally refers to the class. Instance, class, and static methods receive different automatic arguments."),
            ("Design comparisons", "Encapsulation groups data and controlled behavior; abstraction hides implementation behind essential operations. Inheritance is is-a; composition is has-a. Overriding changes inherited behavior; Python does not generally select methods by overloaded signatures."),
            ("Identity and records", "`is` tests identity; `==` tests equality. A regular class permits custom behavior; a dataclass reduces boilerplate for records."),
        ],
        "code": """class Lamp:
    kind = "LED"

    def __init__(self, room):
        self.room = room

    def label(self):
        return f"{self.kind} lamp in {self.room}"


desk_lamp = Lamp("study")
print(desk_lamp.label())
print(desk_lamp is Lamp("study"))
print(desk_lamp.room == "study")""",
        "output": "LED lamp in study\nFalse\nTrue",
        "walk": "kind is a class attribute, room is an instance attribute, label is an instance method. Constructing a second Lamp makes a different identity even though its room value matches.",
        "diagram": "mind_map",
        "analogy": "Use this chapter as a map: class is the plan, object is the thing, and each design principle describes a different way objects cooperate.",
        "mistake": "Do not equate equal data with identical objects. The final two comparisons deliberately test different questions.",
        "terms": "Review the glossary and comparison table in the final revision guide; explain each pair in your own words and give one code example.",
    },
    {
        "part": "PART 5 · REVISION AND MASTERY",
        "title": "Common Beginner Mistakes",
        "topics": [
            ("Method and initializer spelling", "Forgetting self causes argument-count errors. Misspelling __init__ means initialization does not run. Use exact names and test by constructing an object."),
            ("Classes, attributes, and indentation", "A class is not an instance. Indentation defines Python blocks. Distinguish class-wide data from per-instance state, especially mutable values."),
            ("Inheritance and privacy assumptions", "Use super() cooperatively and inherit only for a true substitutable is-a relationship. An underscore is a convention, not strict privacy."),
            ("Returns, references, and complexity", "Printing displays text; returning sends a value back to a caller. Assignment aliases objects rather than copying them. Avoid adding classes when functions are simpler."),
        ],
        "code": """class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value


counter = Counter()
result = counter.increment()
print(result)
print(counter.value)""",
        "output": "1\n1",
        "walk": "increment updates object state and also returns the new value. The caller can store the result. Without return, result would be None even though a print inside the method might display a value.",
        "diagram": None,
        "analogy": "A display screen shows a result to a person; a returned value hands it back to another part of the program. They are different pathways.",
        "mistake": "Avoid mutable class attributes for per-object state, `is` for value comparisons, and broad except clauses that hide programming errors.",
        "terms": "Return value: result given back to the caller. Print: output to a stream. Aliasing: multiple names for one object. super(): next implementation in MRO.",
    },
    {
        "part": "PART 5 · REVISION AND MASTERY",
        "title": "Practice Workbook",
        "topics": [
            ("How to practice", "Try each prompt before reading the answer key. For output questions, trace object creation, method calls, and mutations in order. For code tasks, run normal and invalid cases."),
            ("Explain before you code", "For design problems, list the objects, their responsibilities, the data each owns, and the messages they need to exchange. A short sketch prevents unnecessary inheritance."),
            ("Use the answer key to learn", "An answer key gives one reasonable solution, not the only possible design. Compare reasoning and test alternative implementations."),
        ],
        "code": """class Score:
    def __init__(self, points):
        self.points = points

    def passed(self):
        return self.points >= 50


print(Score(72).passed())""",
        "output": "True",
        "walk": "Score stores points; passed answers a question about that object's state. Predict the Boolean first, then compare it with the output.",
        "diagram": None,
        "analogy": "Practice is like learning a sport: first watch a demonstration, then predict and perform, and finally check feedback.",
        "mistake": "Do not read the answer key before attempting the task. The recall attempt is part of learning.",
        "terms": "Prediction: reason about output without running. Debugging: locate and correct an error. Challenge: a task combining several concepts.",
    },
    {
        "part": "PART 5 · REVISION AND MASTERY",
        "title": "Final Master Revision Guide",
        "topics": [
            ("One-page cheat sheet", "class defines instances · object owns state · self is the current instance · __init__ initializes · methods define behavior · properties validate access · inheritance is-a · composition has-a · polymorphism shares an operation · exceptions report invalid actions."),
            ("Glossary and syntax", "Review the glossary, syntax reference, decorators, and special-method table at the end. In Python, naming conventions communicate intent; only language keywords are reserved."),
            ("Self-assessment", "Can you create and explain a class, preserve valid state, choose composition or inheritance, predict object identity, handle invalid input, and test a small OOP program? If not, revisit the matching chapter."),
            ("14-day revision plan", "Days 1–2: classes, objects, state. Days 3–4: self, initialization, method types. Days 5–6: properties and exceptions. Days 7–8: inheritance, polymorphism, abstraction. Days 9–10: composition, references, copying. Days 11–12: dataclasses, protocols, SOLID. Day 13: build one project. Day 14: workbook review and self-explanation."),
        ],
        "code": """class Reminder:
    def __init__(self, topic):
        self.topic = topic

    def remember(self):
        return f"Blueprint → object; state + behavior: {self.topic}"


print(Reminder("OOP").remember())""",
        "output": "Blueprint → object; state + behavior: OOP",
        "walk": "Use this final reminder as a compact mental model: classes describe, objects hold state, methods act, and collaborating objects make a program.",
        "diagram": "mind_map",
        "analogy": "Revisit the map before an exam: recognize the main concepts first, then connect each one to an example and a program.",
        "mistake": "Memorizing terms without writing or tracing code is fragile. Explain one example aloud and modify it to check understanding.",
        "terms": "Cheat sheet: compact reference. Glossary: definitions of key terms. Revision plan: spaced review schedule.",
    },
]


PROJECTS = [
    {
        "name": "Project 1 — Student Management System",
        "problem": "Maintain multiple student records and calculate each student's average and result.",
        "requirements": "Store name and marks; accept only marks from 0 through 100; calculate average; display a pass/follow-up message; create multiple students.",
        "code": """class Student:
    def __init__(self, name, marks):
        if not name.strip():
            raise ValueError("name cannot be blank")
        if not marks or any(not 0 <= mark <= 100 for mark in marks):
            raise ValueError("marks must be from 0 to 100")
        self.name = name
        self.marks = list(marks)

    def average(self):
        return sum(self.marks) / len(self.marks)

    def report(self):
        result = "Pass" if self.average() >= 50 else "Needs practice"
        return f"{self.name}: average {self.average():.1f} — {result}"


students = [
    Student("Mira", [82, 90, 76]),
    Student("Noah", [45, 54, 49]),
]
for student in students:
    print(student.report())""",
        "output": "Mira: average 82.7 — Pass\nNoah: average 49.3 — Needs practice",
        "diagram": "student_flow",
        "class_diagram": "student_classes",
        "walk": "Each Student owns a fresh marks list. average calculates from that object's marks; report formats the average and uses a simple threshold. Invalid records fail before creation completes.",
        "test": "Try an empty name, an empty marks list, a mark of 101, and two students with different marks. Confirm one record never changes another.",
        "challenge": "Add a method that returns the highest mark, and a class that stores students and finds a student by name.",
    },
    {
        "name": "Project 2 — Bank Account Simulator",
        "problem": "Model deposits, withdrawals, current balance, and a transaction history while preventing invalid actions.",
        "requirements": "Reject negative starting balances and non-positive transactions; reject withdrawals larger than the balance; record each successful transaction.",
        "code": """class InsufficientFundsError(Exception):
    pass


class BankAccount:
    def __init__(self, owner, balance=0):
        if balance < 0:
            raise ValueError("starting balance cannot be negative")
        self.owner = owner
        self._balance = balance
        self.history = []

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount
        self.history.append(f"deposit +{amount:.2f}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self._balance:
            raise InsufficientFundsError("not enough funds")
        self._balance -= amount
        self.history.append(f"withdraw -{amount:.2f}")


account = BankAccount("Mira", 100)
account.deposit(25)
account.withdraw(40)
print(account.balance)
print(account.history)""",
        "output": "85\n['deposit +25.00', 'withdraw -40.00']",
        "diagram": "bank_flow",
        "class_diagram": "bank_classes",
        "walk": "The account validates before mutating. `_balance` is internal by convention and exposed through a read-only property. Each successful transaction adds an entry to history.",
        "test": "Test valid deposit and withdrawal, zero amount, a negative amount, and insufficient funds. Confirm failed transactions do not alter balance or history.",
        "challenge": "Add a transfer method that withdraws from one account and deposits to another, handling failure without losing funds.",
    },
    {
        "name": "Project 3 — Library Management System",
        "problem": "Track a collection of books and whether each one is available to borrow.",
        "requirements": "Book objects hold title, author, and availability; Library can add, borrow, and return books; reject unknown or unavailable titles.",
        "code": """class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.available = True


class Library:
    def __init__(self):
        self.books = {}

    def add(self, book):
        self.books[book.title] = book

    def borrow(self, title):
        book = self.books.get(title)
        if book is None:
            raise KeyError("book not found")
        if not book.available:
            raise ValueError("book is already borrowed")
        book.available = False
        return book

    def return_book(self, title):
        book = self.books.get(title)
        if book is None:
            raise KeyError("book not found")
        if book.available:
            raise ValueError("book was not borrowed")
        book.available = True


library = Library()
library.add(Book("The Blue Planet", "A. Rao"))
borrowed = library.borrow("The Blue Planet")
print(borrowed.title, borrowed.available)
library.return_book("The Blue Planet")
print(library.books["The Blue Planet"].available)""",
        "output": "The Blue Planet False\nTrue",
        "diagram": "library_flow",
        "class_diagram": "library_classes",
        "walk": "Library stores references to Book instances. Borrow changes the selected book's state; returning changes it back. The library and book have distinct responsibilities.",
        "test": "Borrow once, try borrowing again, return once, try returning again, and request a missing title.",
        "challenge": "Add a search method that returns available titles containing a chosen word.",
    },
    {
        "name": "Project 4 — Online Shopping Cart",
        "problem": "Represent products and quantities, allow cart updates, and calculate a total.",
        "requirements": "Product validates non-negative price; cart combines quantities for the same product; reject non-positive quantities; calculate total from item lines.",
        "code": """class Product:
    def __init__(self, name, price):
        if price < 0:
            raise ValueError("price cannot be negative")
        self.name = name
        self.price = price


class ShoppingCart:
    def __init__(self):
        self.items = {}

    def add(self, product, quantity=1):
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.items[product] = self.items.get(product, 0) + quantity

    def remove(self, product, quantity=1):
        if quantity <= 0 or self.items.get(product, 0) < quantity:
            raise ValueError("invalid removal quantity")
        remaining = self.items[product] - quantity
        if remaining:
            self.items[product] = remaining
        else:
            del self.items[product]

    def total(self):
        return sum(product.price * quantity
                   for product, quantity in self.items.items())


pen = Product("Pen", 1.50)
cart = ShoppingCart()
cart.add(pen, 3)
cart.remove(pen)
print(f"${cart.total():.2f}")""",
        "output": "$3.00",
        "diagram": "cart_flow",
        "class_diagram": "cart_classes",
        "walk": "ShoppingCart holds Product references and quantities. add and remove check quantities; total multiplies each product price by the quantity.",
        "test": "Add the same product twice, remove part and all of its quantity, and try invalid removal and a negative-price product.",
        "challenge": "Add a discount method or a separate pricing policy without placing checkout logic in Product.",
    },
    {
        "name": "Project 5 — Defensive Cybersecurity Alert Manager",
        "problem": "Store and summarize defensive security alerts with a validated severity and source.",
        "requirements": "Represent alert records; support specialized descriptions; filter by severity; use safe static example data only.",
        "code": """class SecurityAlert:
    ALLOWED = {"low", "medium", "high", "critical"}

    def __init__(self, title, severity, source):
        if severity not in self.ALLOWED:
            raise ValueError("invalid severity")
        if not title.strip() or not source.strip():
            raise ValueError("title and source are required")
        self.title = title
        self.severity = severity
        self.source = source

    def describe(self):
        return f"[{self.severity.upper()}] {self.title} ({self.source})"

class EndpointAlert(SecurityAlert):
    def describe(self):
        return f"{super().describe()} — review endpoint inventory"


class AlertManager:
    def __init__(self):
        self.alerts = []

    def add(self, alert):
        self.alerts.append(alert)

    def by_severity(self, severity):
        return [alert for alert in self.alerts
                if alert.severity == severity]


manager = AlertManager()
manager.add(SecurityAlert("Repeated login failures", "medium", "lab-log"))
manager.add(EndpointAlert("Outdated endpoint", "medium", "inventory"))
for alert in manager.by_severity("medium"):
    print(alert.describe())""",
        "output": "[MEDIUM] Repeated login failures (lab-log)\n[MEDIUM] Outdated endpoint (inventory) — review endpoint inventory",
        "diagram": "security_flow",
        "class_diagram": "security_classes",
        "walk": "SecurityAlert validates an incident record; EndpointAlert specializes its description while preserving the base behavior with super(). AlertManager stores and filters both types through a shared describe() operation. This is defensive data modeling using fictional local examples, not instructions for unauthorized activity.",
        "test": "Test each allowed severity, an invalid severity, blank fields, and filtering when no alerts match.",
        "challenge": "Create a subclass for a different alert category that overrides describe(), then display mixed alert types through the same method.",
    },
]

PROJECT_ALGORITHMS = {
    "Project 1": [
        "Receive a student's name and marks.",
        "Reject blank names, empty marks, or marks outside 0–100.",
        "Create one Student object per valid record.",
        "Compute the average from that object's marks and display its report.",
    ],
    "Project 2": [
        "Create an account with a non-negative starting balance.",
        "Receive a deposit or withdrawal request.",
        "Validate amount and available funds before changing state.",
        "Update the balance and append a transaction only after success.",
    ],
    "Project 3": [
        "Add Book objects to the Library collection.",
        "Find the requested title and verify it is available.",
        "Mark it borrowed or returned only when the requested transition is valid.",
        "Report the resulting availability or a clear error.",
    ],
    "Project 4": [
        "Receive a Product and positive quantity.",
        "Update that product's cart quantity.",
        "For removal, ensure the requested quantity exists before changing it.",
        "Calculate total as the sum of price multiplied by quantity.",
    ],
    "Project 5": [
        "Receive fictional alert fields from an authorized local record source.",
        "Validate title, source, and severity against the allowed set.",
        "Store the alert object in the manager.",
        "Filter by severity and call each matching object's describe method.",
    ],
}

SOLID_CASES = [
    {
        "principle": "Single Responsibility Principle (SRP)",
        "bad": """class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def average(self):
        return sum(self.marks) / len(self.marks)

    def report(self):
        return f"{self.name}: {self.average():.1f}"

    def email_message(self):
        return f"Sending report for {self.name}"


student = Student("Ada", [80, 90])
print(student.report(), student.email_message())""",
        "good": """class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def average(self):
        return sum(self.marks) / len(self.marks)

class ReportWriter:
    def save(self, student, path):
        return f"Prepared report for {student.name} at {path}"


student = Student("Ada", [80, 90])
writer = ReportWriter()
print(f"{student.name}: {student.average():.1f}")
print(writer.save(student, "report.txt"))""",
        "bad_output": "Ada: 85.0 Sending report for Ada",
        "good_output": "Ada: 85.0\nPrepared report for Ada at report.txt",
        "lesson": "The first class has record, file, and messaging responsibilities. Separate the student model from output work. Useful when unrelated reasons for change are accumulating in one class.",
    },
    {
        "principle": "Open/Closed Principle (OCP)",
        "bad": """class Alert:
    def __init__(self, kind):
        self.kind = kind

def describe(alert):
    if alert.kind == "login":
        return "Review sign-in activity"
    if alert.kind == "file":
        return "Review the flagged file"
    return "Review network activity"


print(describe(Alert("login")))""",
        "good": """class LoginAlert:
    def describe(self):
        return "Review sign-in activity"

class FileAlert:
    def describe(self):
        return "Review the flagged file"

def describe(alert):
    return alert.describe()

for alert in (LoginAlert(), FileAlert()):
    print(describe(alert))""",
        "bad_output": "Review sign-in activity",
        "good_output": "Review sign-in activity\nReview the flagged file",
        "lesson": "Adding each kind requires editing a growing conditional. A shared operation lets a new compatible class add behavior without rewriting the caller. Useful when new variants are expected.",
    },
    {
        "principle": "Liskov Substitution Principle (LSP)",
        "bad": """class Bird:
    def fly(self):
        return "flying"

class Penguin(Bird):
    def fly(self):
        raise RuntimeError("cannot fly")


print(Bird().fly())
print("A caller that assumes every Bird can fly will fail for Penguin.")""",
        "good": """class Bird:
    def move(self):
        return "moving"

class FlyingBird(Bird):
    def fly(self):
        return "flying"

class Penguin(Bird):
    def swim(self):
        return "swimming"
        

print(FlyingBird().fly())
print(Penguin().move(), Penguin().swim())""",
        "bad_output": "flying\nA caller that assumes every Bird can fly will fail for Penguin.",
        "good_output": "flying\nmoving swimming",
        "lesson": "Code expecting every Bird to fly breaks for Penguin. Keep the base promise broad, or model flying as a more specific capability. Useful when subclasses must work anywhere the base is accepted.",
    },
    {
        "principle": "Interface Segregation Principle (ISP)",
        "bad": """class OfficeMachine:
    def print(self):
        return "printed"

    def scan(self):
        return "scan not supported"

    def fax(self):
        return "fax not supported"


device = OfficeMachine()
print(device.print(), device.scan(), device.fax())""",
        "good": """class Printer:
    def print(self, page):
        return "printed"

class Scanner:
    def scan(self, page):
        return "scanned"


print(Printer().print("page"), Scanner().scan("page"))""",
        "bad_output": "printed scan not supported fax not supported",
        "good_output": "printed scanned",
        "lesson": "A small device can support only the capability it has. Focused interfaces prevent meaningless methods. Useful when classes are forced to implement operations they never use.",
    },
    {
        "principle": "Dependency Inversion Principle (DIP)",
        "bad": """class FileSaver:
    def __init__(self, path):
        self.path = path

    def write(self, text):
        return f"Saved {text} to {self.path}"

class Report:
    def publish(self, text):
        return FileSaver("report.txt").write(text)


print(Report().publish("Weekly summary"))""",
        "good": """class Report:
    def __init__(self, saver):
        self.saver = saver

    def publish(self, text):
        return self.saver.save(text)

class ConsoleSaver:
    def save(self, text):
        return f"Saved: {text}"


print(Report(ConsoleSaver()).publish("Weekly summary"))""",
        "bad_output": "Saved Weekly summary to report.txt",
        "good_output": "Saved: Weekly summary",
        "lesson": "Report constructs one concrete file detail, so replacing storage or testing is harder. Pass an object with a small save() operation. Useful when high-level policy needs replaceable external details.",
    },
]

MISTAKE_CASES = [
    ("Forgetting self", "class Greeter:\n    def greet():\n        return 'hello'\n# Greeter().greet() raises TypeError", "class Greeter:\n    def greet(self):\n        return 'hello'\nprint(Greeter().greet())", "Python supplies the current instance to an instance method."),
    ("Misspelling __init__", "class Pet:\n    def _init_(self, name):\n        self.name = name\n# Pet('Milo').name raises AttributeError", "class Pet:\n    def __init__(self, name):\n        self.name = name\nprint(Pet('Milo').name)", "Use exactly two underscores on each side of init."),
    ("Confusing class and object", "class Lamp:\n    def __init__(self):\n        self.on = False\nlamp = Lamp\n# lamp.on is not an instance attribute", "class Lamp:\n    def __init__(self):\n        self.on = False\nlamp = Lamp()\nprint(lamp.on)", "Parentheses create an instance."),
    ("Incorrect indentation", "class Box:\n    def open(self):\n    print('open')", "class Box:\n    def open(self):\n        print('open')", "The method body must be indented inside the method."),
    ("Mixing class and instance data", "class Player:\n    score = 0\n# Updating Player.score changes shared class data", "class Player:\n    def __init__(self):\n        self.score = 0\nfirst = Player()\nsecond = Player()\nfirst.score += 1", "Put per-player state on each instance."),
    ("Sharing a mutable class list", "class Team:\n    members = []\n# Every team appends to the same list", "class Team:\n    def __init__(self):\n        self.members = []\n", "Create a fresh list in __init__ for each team."),
    ("Misusing super()", "class Parent:\n    def __init__(self, name): self.name = name\nclass Child(Parent):\n    def __init__(self, name):\n        super().__init__()", "class Parent:\n    def __init__(self, name): self.name = name\nclass Child(Parent):\n    def __init__(self, name):\n        super().__init__(name)", "Pass the arguments the parent initializer requires."),
    ("Inheriting for a has-a relationship", "class Engine:\n    pass\nclass Car(Engine):\n    pass", "class Engine:\n    pass\nclass Car:\n    def __init__(self):\n        self.engine = Engine()", "A car has an engine; it is not an engine."),
    ("Assuming underscore means private", "class User:\n    def __init__(self):\n        self._name = 'Ada'\n# _name is still accessible by convention", "class User:\n    def __init__(self, name):\n        self._name = name\n    @property\n    def name(self):\n        return self._name", "Treat underscore as an internal-use convention and expose a clear interface."),
    ("Forgetting to return", "class Score:\n    def double(self, value):\n        value * 2\nresult = Score().double(4)\nprint(result)  # None", "class Score:\n    def double(self, value):\n        return value * 2\nprint(Score().double(4))", "An expression is not returned automatically."),
    ("Confusing print with return", "class Greeter:\n    def greet(self):\n        print('hello')\nmessage = Greeter().greet()\n# message is None", "class Greeter:\n    def greet(self):\n        return 'hello'\nprint(Greeter().greet())", "Use return to give a value to the caller; print is for visible output."),
    ("Misunderstanding references", "first = [1, 2]\nsecond = first\nsecond.append(3)\n# first is also changed", "first = [1, 2]\nsecond = first.copy()\nsecond.append(3)\nprint(first, second)", "Assignment creates another reference. Copy when an independent outer list is needed."),
    ("Overcomplicating a simple task", "class Doubler:\n    def double(self, value):\n        return value * 2\nprint(Doubler().double(4))", "def double(value):\n    return value * 2\nprint(double(4))", "A plain function is clearer when no object state or family of behavior is needed."),
]

EXTRA_EXAMPLES = [
    (
        "Diamond inheritance and MRO",
        """class Root:
    def ping(self):
        print("Root")

class Left(Root):
    def ping(self):
        print("Left")
        super().ping()

class Right(Root):
    def ping(self):
        print("Right")
        super().ping()

class Child(Left, Right):
    def ping(self):
        print("Child")
        super().ping()

Child().ping()
print(" -> ".join(cls.__name__ for cls in Child.mro()[:4]))""",
        "Child\nLeft\nRight\nRoot\nChild -> Left -> Right -> Root",
        "Each implementation calls super(), so Python follows the cooperative MRO once through the diamond rather than repeating Root.",
    ),
    (
        "Special methods for equality, addition, and calling",
        """class Number:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Number) and self.value == other.value

    def __add__(self, other):
        return Number(self.value + other.value)

    def __call__(self):
        return self.value

print(Number(2) == Number(2))
print((Number(2) + Number(3)).value)
print(Number(4)())""",
        "True\n5\n4",
        "The ordinary operations ==, +, and calling an instance route to __eq__, __add__, and __call__. The methods return values with suitable meanings.",
    ),
    (
        "Generator and context-manager protocols",
        """def squares(limit):
    for number in range(1, limit + 1):
        yield number * number

class Session:
    def __enter__(self):
        print("start")
        return self

    def __exit__(self, exc_type, exc, traceback):
        print("close")
        return False

print(list(squares(3)))
with Session():
    print("inside")""",
        "[1, 4, 9]\nstart\ninside\nclose",
        "yield produces each square when requested. The with statement calls __enter__, runs the block, then calls __exit__ even if the block exits with an exception; returning False does not suppress it.",
    ),
]

SUPPLEMENTAL_EXAMPLES = [
    (
        1,
        "The same task in procedural and OOP styles",
        """def average(marks):
    return sum(marks) / len(marks)


students = [
    {"name": "Mira", "marks": [80, 90]},
    {"name": "Noah", "marks": [60, 70]},
]
for student in students:
    print(f"{student['name']}: {average(student['marks']):.1f}")


class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def average(self):
        return sum(self.marks) / len(self.marks)


learners = [Student("Mira", [80, 90]), Student("Noah", [60, 70])]
for learner in learners:
    print(f"{learner.name}: {learner.average():.1f}")""",
        "Mira: 85.0\nNoah: 65.0\nMira: 85.0\nNoah: 65.0",
        "Both versions solve the same problem. The first keeps records as dictionaries and behavior in a function. The second groups each student's data and average behavior in a Student object. For a tiny task either is fine; grouping can help as the model gains rules and operations.",
    ),
    (
        2,
        "Mobile phones: same class, separate object state",
        """class MobilePhone:
    def __init__(self, model, battery):
        self.model = model
        self.battery = battery

    def call(self, minutes):
        self.battery -= minutes
        return f"{self.model}: {minutes}-minute call"


phone_a = MobilePhone("Nova Mini", 90)
phone_b = MobilePhone("Orbit Max", 70)
print(phone_a.call(10))
print(phone_a.battery, phone_b.battery)""",
        "Nova Mini: 10-minute call\n80 70",
        "MobilePhone is the class. Each phone is a separate object with its own model and battery. Calling one phone changes its instance state without changing the other phone.",
    ),
    (
        7,
        "Double underscore and name mangling",
        """class Locker:
    def __init__(self, code):
        self.__code = code

    def accepts(self, candidate):
        return candidate == self.__code


locker = Locker("demo-code")
print(locker.accepts("demo-code"))
print(locker._Locker__code)""",
        "True\ndemo-code",
        "Python rewrites __code to a class-qualified attribute name to reduce accidental clashes. The second line deliberately shows that this is not a privacy or secrecy boundary; never store real secrets this way.",
    ),
    (
        8,
        "Single, multilevel, hierarchical, and multiple inheritance",
        """class Device:
    pass

class Phone(Device):
    pass

class Rechargeable:
    def charge(self):
        return "charging"

class SmartPhone(Phone, Rechargeable):
    pass

class Tablet(Device):
    pass

print("single:", issubclass(Phone, Device))
print("multilevel:", issubclass(SmartPhone, Device))
print("hierarchical:", issubclass(Tablet, Device))
print("multiple:", len(SmartPhone.__bases__) == 2)""",
        "single: True\nmultilevel: True\nhierarchical: True\nmultiple: True",
        "Phone has one base (single). SmartPhone extends Phone, which extends Device (multilevel). Phone and Tablet share Device (hierarchical). SmartPhone has Phone and Rechargeable as bases (multiple). Keep multiple inheritance small and cooperative.",
    ),
    (
        14,
        "A property setter and deleter",
        """class Profile:
    def __init__(self, nickname):
        self.nickname = nickname

    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, value):
        if not value.strip():
            raise ValueError("nickname cannot be blank")
        self._nickname = value

    @nickname.deleter
    def nickname(self):
        self._nickname = None


profile = Profile("Mira")
del profile.nickname
print(profile.nickname)""",
        "None",
        "The setter validates assignments; the deleter defines what `del profile.nickname` means for this class. Here it resets the value rather than removing the internal field.",
    ),
    (
        16,
        "try, except, else, and finally",
        """def percentage(raw):
    try:
        value = int(raw)
        result = 100 / value
    except (ValueError, ZeroDivisionError) as error:
        print(f"error: {type(error).__name__}")
    else:
        print(f"result: {result:.1f}")
    finally:
        print("finished")


percentage("4")
percentage("0")""",
        "result: 25.0\nfinished\nerror: ZeroDivisionError\nfinished",
        "except handles the selected errors. else runs only when try succeeds. finally runs after either path, making it suitable for cleanup that must happen reliably.",
    ),
    (
        17,
        "A managed resource with the with statement",
        """from io import StringIO


with StringIO("first line\\nsecond line\\n") as stream:
    print(stream.readline().strip())

print(stream.closed)""",
        "first line\nTrue",
        "The with block acquires the in-memory stream; leaving the block closes it automatically, including when an exception occurs. Real files use the same pattern: `with open(path) as file:`.",
    ),
]


CONCEPT_QUESTIONS = [
    "Define a class and an object in one sentence each.",
    "Why can two instances of the same class have different state?",
    "What is the difference between an instance attribute and a class attribute?",
    "What does self refer to inside an instance method?",
    "Is self a Python keyword? Explain.",
    "What is the difference between __new__ and __init__?",
    "When is a class method useful?",
    "What does a leading underscore communicate in Python?",
    "What does name mangling do, and what does it not do?",
    "Explain encapsulation and abstraction without treating them as synonyms.",
    "Give an example of an is-a relationship and a has-a relationship.",
    "What does method overriding mean?",
    "What is the purpose of super()?",
    "What is method resolution order?",
    "Explain polymorphism using a method shared by two classes.",
    "How is duck typing different from inheritance?",
    "Why does a class with an unimplemented abstract method remain abstract?",
    "What does __len__ allow an object to support?",
    "What is the difference between association and composition?",
    "What does is test, and what does == test?",
    "What is aliasing?",
    "How does a shallow copy differ from a deep copy?",
    "Why use default_factory for a list field in a dataclass?",
    "Why should a class raise an exception before changing invalid state?",
    "What is one case where a function is clearer than a class?",
]

OUTPUT_QUESTIONS = [
    ("class Box:\n    def __init__(self, value): self.value = value\nfirst = Box(3)\nsecond = Box(7)\nprint(first.value + second.value)", "10"),
    ("class Tally:\n    def __init__(self): self.n = 0\n    def add(self): self.n += 1\nt = Tally()\nt.add()\nt.add()\nprint(t.n)", "2"),
    ("class Plant:\n    kind = 'fern'\na = Plant()\nb = Plant()\na.kind = 'rose'\nprint(a.kind, b.kind, Plant.kind)", "rose fern fern"),
    ("class A:\n    def name(self): return 'A'\nclass B(A):\n    def name(self): return 'B'\nprint(B().name())", "B"),
    ("class Item:\n    def __init__(self, name): self.name = name\none = Item('pen')\ntwo = one\nprint(one is two)", "True"),
    ("class Word:\n    def __init__(self, text): self.text = text\n    def __len__(self): return len(self.text)\nprint(len(Word('cat')))", "3"),
    ("class Score:\n    def __init__(self, n): self.n = n\n    def passed(self): return self.n >= 50\nprint(Score(49).passed())", "False"),
    ("class Base:\n    value = 4\nclass Child(Base): pass\nprint(Child.value)", "4"),
    ("class C:\n    def __init__(self): self.items = []\na = C(); b = C(); a.items.append(1)\nprint(a.items, b.items)", "[1] []"),
    ("class Label:\n    def __str__(self): return 'ready'\nprint(str(Label()))", "ready"),
    ("class A:\n    def f(self): return 'a'\nclass B(A): pass\nprint(B().f())", "a"),
    ("class A:\n    def __init__(self, x=2): self.x = x\nprint(A().x, A(5).x)", "2 5"),
    ("class P:\n    def __init__(self, x): self.x = x\np = P(4)\nprint(p.x == 4, p is P(4))", "True False"),
    ("class Add:\n    def __add__(self, other): return 'together'\nprint(Add() + Add())", "together"),
    ("class C:\n    def __init__(self): self.x = 1\nc = C()\nc.x = 8\nprint(c.x)", "8"),
]

CODING_QUESTIONS = [
    ("Create a `Book` class with a title and author.", "Define __init__(self, title, author) and store both values as instance attributes."),
    ("Add a method to `Book` that returns a readable label.", "Return a formatted string using self.title and self.author."),
    ("Create two `Student` objects with independent mark lists.", "Create each list in __init__; append to one student's list and verify the other stays empty."),
    ("Write a `Rectangle` class that calculates area.", "Store width and height; return width * height from an area method."),
    ("Add validation to reject a negative rectangle side.", "Raise ValueError before assigning a negative width or height."),
    ("Create a class attribute shared by every `Employee` instance.", "Declare a constant such as company_name in the class body."),
    ("Write a class method that constructs a `Point` from a pair.", "Use @classmethod def from_pair(cls, pair): return cls(pair[0], pair[1])."),
    ("Write a static method that checks whether a value is positive.", "Return value > 0 from a @staticmethod; decide whether numeric validation is also needed."),
    ("Create a read-only property for a circle's diameter.", "Expose a property that computes 2 * radius and do not define a setter."),
    ("Create `Animal` and `Bird` classes; let Bird extend an inherited description.", "Override the method in Bird and use super() to retain the base message."),
    ("Create two payment classes with the same `pay` method and use them in a loop.", "Implement pay in each class and call it on each object without type-specific branching."),
    ("Create an abstract `Shape` with an abstract `area` method.", "Subclass ABC, decorate area with @abstractmethod, and implement it in concrete shapes."),
    ("Implement __str__ for a `Student` object.", "Return a human-readable string; ensure it is a str."),
    ("Create a shopping cart that totals product price times quantity.", "Store product/quantity entries and sum their extended prices."),
    ("Create a custom iterator yielding numbers from 1 through n.", "Implement __iter__ and __next__; raise StopIteration after n."),
    ("Create a dataclass for a to-do item with a fresh tags list per instance.", "Use @dataclass and tags: list[str] = field(default_factory=list)."),
    ("Raise a custom `OutOfStockError` when an item cannot be borrowed.", "Define an exception subclass and raise it before changing availability."),
    ("Use composition to model a computer containing a processor object.", "Give Computer a Processor instance attribute and delegate a suitable operation."),
    ("Write a defensive alert class that rejects an unsupported severity.", "Validate membership in a fixed allowed set and raise ValueError."),
    ("Build a small class with an `add` operation and test both success and invalid input.", "Validate before changing state; assert the expected result and exception."),
]

CODING_SOLUTIONS = [
    ("""class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author


print(Book("Python", "A. Rao").title)""", "Python", "The initializer stores both values on each Book instance."),
    ("""class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def label(self):
        return f"{self.title} by {self.author}"


print(Book("Python", "A. Rao").label())""", "Python by A. Rao", "label reads this instance's attributes and returns a string."),
    ("""class Student:
    def __init__(self, name):
        self.name = name
        self.marks = []


ada = Student("Ada")
lin = Student("Lin")
ada.marks.append(95)
print(ada.marks, lin.marks)""", "[95] []", "The fresh list is created inside __init__, so each student owns a different list."),
    ("""class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


print(Rectangle(4, 3).area())""", "12", "The area method uses the dimensions stored on the same object."),
    ("""class Rectangle:
    def __init__(self, width, height):
        if width < 0 or height < 0:
            raise ValueError("sides cannot be negative")
        self.width = width
        self.height = height


print(Rectangle(4, 3).width)""", "4", "Both values are checked before either becomes object state; invalid dimensions raise ValueError."),
    ("""class Employee:
    company_name = "Maple Labs"

    def __init__(self, name):
        self.name = name


print(Employee("Ada").company_name)""", "Maple Labs", "company_name is shared class information; name belongs to each instance."),
    ("""class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_pair(cls, pair):
        return cls(pair[0], pair[1])


point = Point.from_pair((2, 5))
print(point.x, point.y)""", "2 5", "The class method receives cls and creates the instance through it."),
    ("""class NumberCheck:
    @staticmethod
    def is_positive(value):
        return value > 0


print(NumberCheck.is_positive(4))""", "True", "The check needs neither per-object state nor class state, so it is static."),
    ("""class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def diameter(self):
        return self.radius * 2


print(Circle(3).diameter)""", "6", "The property computes a read-only value from radius without a setter."),
    ("""class Animal:
    def describe(self):
        return "An animal"

class Bird(Animal):
    def describe(self):
        return f"{super().describe()} that can be a bird"


print(Bird().describe())""", "An animal that can be a bird", "Bird overrides describe and extends the parent behavior with super()."),
    ("""class CardPayment:
    def pay(self, amount):
        return f"card: {amount}"

class CashPayment:
    def pay(self, amount):
        return f"cash: {amount}"


for method in (CardPayment(), CashPayment()):
    print(method.pay(10))""", "card: 10\ncash: 10", "Both classes offer pay, so the loop can use either without checking its concrete type."),
    ("""from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        raise NotImplementedError

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2


print(Square(4).area())""", "16", "Shape declares the contract; Square implements area and can then be instantiated."),
    ("""class Student:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Student: {self.name}"


print(Student("Mira"))""", "Student: Mira", "__str__ must return a human-readable string."),
    ("""class Product:
    def __init__(self, price):
        self.price = price

class Cart:
    def __init__(self):
        self.items = []

    def add(self, product, quantity):
        self.items.append((product, quantity))

    def total(self):
        return sum(product.price * quantity for product, quantity in self.items)


cart = Cart()
cart.add(Product(2.5), 2)
print(cart.total())""", "5.0", "The cart composes product references with quantities and computes extended prices."),
    ("""class CountUp:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        self.current += 1
        return self.current


print(list(CountUp(3)))""", "[1, 2, 3]", "The iterator advances its state and ends by raising StopIteration."),
    ("""from dataclasses import dataclass, field

@dataclass
class Task:
    title: str
    tags: list[str] = field(default_factory=list)


one = Task("read")
two = Task("write")
one.tags.append("school")
print(one.tags, two.tags)""", "['school'] []", "default_factory provides a new mutable list for each task."),
    ("""class OutOfStockError(Exception):
    pass

class Shelf:
    def __init__(self, count):
        self.count = count

    def borrow(self):
        if self.count == 0:
            raise OutOfStockError("no copies available")
        self.count -= 1
        return self.count


print(Shelf(2).borrow())""", "1", "The domain exception is raised before an unavailable item could change state."),
    ("""class Processor:
    def start(self):
        return "processor started"

class Computer:
    def __init__(self, processor):
        self.processor = processor

    def start(self):
        return self.processor.start()


computer = Computer(Processor())
print(computer.start())""", "processor started", "Computer has a Processor and delegates work to it: composition, not inheritance."),
    ("""class SecurityAlert:
    ALLOWED = {"low", "medium", "high"}

    def __init__(self, severity):
        if severity not in self.ALLOWED:
            raise ValueError("unsupported severity")
        self.severity = severity


print(SecurityAlert("high").severity)""", "high", "The class checks the allowed values before storing severity."),
    ("""class Accumulator:
    def __init__(self):
        self.value = 0

    def add(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.value += amount
        return self.value


counter = Accumulator()
assert counter.add(3) == 3
try:
    counter.add(0)
except ValueError as error:
    print(counter.value, str(error))""", "3 amount must be positive", "The assertion tests success; invalid input raises a clear error without changing the stored value."),
]


DEBUG_QUESTIONS = [
    ("class Cat:\n    def __init(name):\n        name = name\nc = Cat('Milo')\nprint(c.name)", "Add self to __init__ and assign self.name = name."),
    ("class Dog:\n    def __init__(self, name):\n        self.name = name\nd = Dog\nprint(d.name)", "Create an instance with Dog('Rex'); d currently refers to the class."),
    ("class Box:\n    def __init__(self):\n        self.items = []\n    def add(self, item):\n        self.items.append(item)\nb = Box()\nprint(b.add(2))", "The method changes state but returns None. Print b.items or explicitly return the updated list/value."),
    ("class A:\n    def __init__(self):\n        self.value = 1\n    def get(self):\n        return value\nprint(A().get())", "Use self.value; value is not a local variable in get."),
    ("class Team:\n    members = []\n    def add(self, name): self.members.append(name)", "For independent teams, define self.members = [] in __init__."),
    ("class Parent:\n    def __init__(self, name): self.name = name\nclass Child(Parent):\n    def __init__(self, name): self.name = name", "Calling super().__init__(name) is a clearer way to reuse parent initialization when it fits."),
    ("class A:\n    def __init__(self, value): self.value = value\na = A(1)\nb = a\nb.value = 9\nprint(a.value)", "Output is 9 because a and b alias the same object. Copy explicitly if independent state is required."),
    ("class Account:\n    def __init__(self): self.balance = 0\n    def deposit(self, amount): self.balance += amount\nAccount().deposit(-5)", "Validate amount > 0 before changing balance and raise ValueError for an invalid deposit."),
    ("class Greeting:\n    def __str__(self): return 5\nprint(Greeting())", "__str__ must return a string; return '5' rather than integer 5."),
    ("class Lamp:\n    def __init__(self): self.on = False\n    def switch_on(self): self.on = True\nlamp = Lamp\nlamp.switch_on()", "Instantiate with lamp = Lamp() before calling an instance method."),
]

DEBUG_SOLUTIONS = [
    ("""class Cat:
    def __init__(self, name):
        self.name = name


cat = Cat("Milo")
print(cat.name)""", "Milo", "The initializer needs self and must assign the value to self.name."),
    ("""class Dog:
    def __init__(self, name):
        self.name = name


dog = Dog("Rex")
print(dog.name)""", "Rex", "Dog without parentheses refers to the class; Dog('Rex') creates an instance."),
    ("""class Box:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)


box = Box()
box.add(2)
print(box.items)""", "[2]", "add mutates state but has no return statement; print the state rather than the method result."),
    ("""class A:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


print(A(3).get())""", "3", "The instance attribute must be accessed through self inside get."),
    ("""class Team:
    def __init__(self):
        self.members = []

    def add(self, name):
        self.members.append(name)


first = Team()
second = Team()
first.add("Ada")
print(first.members, second.members)""", "['Ada'] []", "The per-team list is initialized on each object rather than shared as a class attribute."),
    ("""class Parent:
    def __init__(self, name):
        self.name = name

class Child(Parent):
    def __init__(self, name):
        super().__init__(name)


print(Child("Mira").name)""", "Mira", "super().__init__ must receive the required name argument."),
    ("""first = [1, 2]
second = first.copy()
second.append(3)
print(first, second)""", "[1, 2] [1, 2, 3]", "copy creates a separate outer list for these scalar elements; simple assignment would alias the same list."),
    ("""class Account:
    def __init__(self):
        self.balance = 0

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount


account = Account()
account.deposit(5)
print(account.balance)""", "5", "Validate before mutating so invalid deposits cannot make the balance negative."),
    ("""class Greeting:
    def __str__(self):
        return "5"


print(Greeting())""", "5", "__str__ must return a string, not an integer."),
    ("""class Lamp:
    def __init__(self):
        self.on = False

    def switch_on(self):
        self.on = True


lamp = Lamp()
lamp.switch_on()
print(lamp.on)""", "True", "Instantiate Lamp before invoking its instance method."),
]

OUTPUT_EXPLANATIONS = [
    "first.value is 3 and second.value is 7; the program adds the two independent attributes.",
    "The same Tally object is incremented twice, so n moves from 0 to 2.",
    "Assigning a.kind creates an instance attribute that shadows the class value; b and Plant still see the class value.",
    "B supplies its own name method, so method lookup finds that override first.",
    "second and first are aliases for the same Box instance.",
    "len(obj) calls Word.__len__, which returns the number of characters in 'cat'.",
    "49 is below the inclusive threshold of 50, so passed returns False.",
    "Child inherits the class attribute value from Base.",
    "Each C initializer creates a distinct list; only a.items receives the append.",
    "str(Label()) invokes __str__ and prints the returned string.",
    "B inherits A.f unchanged, so the method returns 'a'.",
    "The first instance uses the default x=2; the second uses the supplied x=5.",
    "p.x == 4 compares values and is True; p is P(4) compares two distinct instances and is False.",
    "The + operator invokes Add.__add__, which returns the string 'together'.",
    "The assignment changes the same object's x attribute from 1 to 8.",
]

DESIGN_QUESTIONS = [
    ("A school needs student records with subject marks. What classes and responsibilities would you choose?", "A Student can own identity and marks and calculate its average; a roster/School can manage a collection if collection operations are needed."),
    ("A library lends books to members. Which objects need relationships?", "Library manages books; Book tracks availability; Member can represent a borrower. Keep lending rules in a focused service or library method."),
    ("A game has many characters with different ways to move. How could polymorphism help?", "Define a common move operation and let each character implement its own movement; the game loop calls move() on each."),
    ("A cart includes products and quantities. Why is composition preferable to inheritance?", "A cart has products; it is not a product. Store product references and quantity data."),
    ("A bank account must not become negative. Where should validation happen?", "In the account's withdrawal operation before the balance is changed; expose a clear error for invalid requests."),
    ("Several file formats can export a report. How could abstraction help?", "Define a small exporter contract or shared export operation; provide one implementation per format."),
    ("A security team records alerts from different sources. How can one report them safely?", "Normalize validated fields in alert objects, expose a shared describe method, and keep examples defensive and authorized."),
    ("A phone has a battery component. How would you model that relationship?", "Phone contains or refers to a Battery object: a has-a relationship modeled with composition."),
    ("A class has five unrelated jobs. What would you do?", "Split responsibilities into focused collaborators and have a coordinating component depend on their small interfaces."),
    ("A tiny script doubles a number once. Should it use an OOP hierarchy?", "Probably not; a plain function is clearer until there is meaningful object state or a family of behaviors."),
]

CHALLENGES = [
    ("Build a school system with Student, Course, and Enrollment objects; enforce that a student cannot enroll twice in the same course.", "Use a set or search in Course/Enrollment state, validate before inserting, and keep identity rules explicit."),
    ("Create a shape collection that totals area for circles and rectangles without checking each concrete type in the loop.", "Give each shape an area method and sum shape.area(); each class supplies its own calculation."),
    ("Design a bank transfer that is safe if the receiving account rejects a deposit.", "Validate both accounts and amount before mutation; define a clear transaction approach and preserve balances if an operation fails."),
    ("Build a defensive alert application with polymorphic alert types, validation, filtering, and a replaceable output sink.", "Use a base contract or duck typing, validate records, filter by fields, and inject a small writer collaborator."),
    ("Model a library with multiple copies of a title, a borrower, and a return history; explain object relationships.", "Use BookCopy instances and borrower references or loan records; distinguish titles from physical copies and document lifecycle."),
]


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_text(cell, text, bold=False, color=INK, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "Aptos"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def add_page_field(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])


def set_keep(paragraph):
    paragraph.paragraph_format.keep_together = True


def add_callout(doc, label, text, color=TEAL):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    cell = table.cell(0, 0)
    shade(cell, "F0F6F6" if color == TEAL else "FFF5E8")
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Inches(0.08)
    r = p.add_run(f"{label}  ")
    r.bold = True
    r.font.color.rgb = RGBColor.from_string(color)
    p.add_run(text)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_code(doc, code, label="PYTHON CODE"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(label)
    r.bold = True
    r.font.size = Pt(8)
    r.font.color.rgb = RGBColor.from_string(TEAL)
    table = doc.add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    shade(cell, "F3F6F8")
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.left_indent = Inches(0.06)
    for i, line in enumerate(code.rstrip().splitlines()):
        if i:
            p.add_run().add_break()
        run = p.add_run(line or " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor.from_string("203040")


def add_body(doc, text):
    p = doc.add_paragraph(text, style="Body Text")
    p.paragraph_format.widow_control = True
    return p


def add_bullets(doc, lines):
    for line in lines:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2)
        p.add_run(line)


def add_numbered(doc, lines):
    for line in lines:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(3)
        p.add_run(line)


def add_diagram(doc, path, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(6.0))
    cap = doc.add_paragraph(caption, style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    set_keep(p)
    return p


def add_toc_field(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-2" \\h \\z \\u '
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Open in Word and choose Update Table to populate page numbers."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, placeholder, end])


def build_doc(diagrams):
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.7)
    section.top_margin = Inches(0.68)
    section.bottom_margin = Inches(0.68)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08
    for name, size, color in [
        ("Title", 34, NAVY),
        ("Heading 1", 22, NAVY),
        ("Heading 2", 14, TEAL),
        ("Heading 3", 11, ORANGE),
    ]:
        style = styles[name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(5)
    styles["Caption"].font.name = "Aptos"
    styles["Caption"].font.size = Pt(8.5)
    styles["Caption"].font.italic = True
    styles["Body Text"].font.name = "Aptos"
    styles["Body Text"].font.size = Pt(10.5)

    header = section.header.paragraphs[0]
    header.text = "PYTHON OOP  |  COMPLETE MASTER GUIDE"
    header.style = styles["Caption"]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Learn by modeling • explaining • building     |     ")
    add_page_field(footer)

    # Cover
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(120)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("PYTHON")
    r.bold = True
    r.font.size = Pt(20)
    r.font.color.rgb = RGBColor.from_string(TEAL)
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("OBJECT-ORIENTED\nPROGRAMMING")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Complete Master Guide")
    r.font.size = Pt(24)
    r.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    r = p.add_run("From your first class to confident, clean Python design")
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor.from_string(INK)
    doc.add_paragraph()
    add_diagram(doc, diagrams["class_object"], "One blueprint; many independent objects.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("A beginner-friendly textbook with runnable code, diagrams, projects, and practice")
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor.from_string(TEAL)
    doc.add_page_break()

    add_heading(doc, "How to Use This Book", 1)
    add_body(doc, "Read one idea at a time. Start with the analogy, study the definition, then trace the complete program line by line. Cover the output and predict it before checking. Run the code in Python 3.11 or later, change one value, and observe what changes.")
    add_bullets(doc, [
        "CONCEPT and REAL-WORLD EXAMPLE introduce an idea before its code.",
        "PYTHON CODE is complete and designed to run as shown; EXPECTED OUTPUT is kept separate.",
        "COMMON MISTAKE highlights a likely beginner error and a reliable correction.",
        "PRACTICE TIME appears before a separate answer key so you can attempt work first.",
        "Project diagrams use simplified flow; the code is the exact executable behavior.",
        "This book uses fictional, defensive cybersecurity examples only.",
    ])
    add_callout(doc, "LEARNING LOOP", "Read → predict → run → change → explain. If you can teach a concept in your own words and modify its example, you are learning it.")

    add_heading(doc, "Contents", 1)
    p = doc.add_paragraph()
    add_toc_field(p)
    add_body(doc, "The clickable Word table of contents is a field. In Microsoft Word, right-click it and select Update Field → Update entire table to populate headings and page numbers. A manual chapter map follows for readers whose viewer does not update fields.")
    for i, ch in enumerate(CHAPTERS, 1):
        doc.add_paragraph(f"Chapter {i:02d}  {ch['title']}")
    doc.add_page_break()
    add_heading(doc, "The OOP Map", 1)
    add_diagram(doc, diagrams["mind_map"], "The central ideas connect: define objects, protect valid state, and make collaborators work together.")
    add_body(doc, "The book progresses from the idea of a class and object to the behaviors that make object-oriented programs useful. Advanced features are introduced only after their basic pieces.")

    active_part = None
    for index, chapter in enumerate(CHAPTERS, 1):
        if chapter["part"] != active_part:
            active_part = chapter["part"]
            doc.add_page_break()
            add_heading(doc, active_part, 1)
        doc.add_page_break()
        add_heading(doc, f"Chapter {index}: {chapter['title']}", 1)
        add_callout(doc, "START HERE", chapter["topics"][0][1][:300])
        for title, text in chapter["topics"]:
            add_heading(doc, title, 2)
            add_body(doc, text)
        add_callout(doc, "REAL-WORLD EXAMPLE", chapter["analogy"])
        if chapter["diagram"]:
            add_diagram(doc, diagrams[chapter["diagram"]], f"Figure: {chapter['title']} — use the arrows and labels to connect the idea to the code.")
        add_heading(doc, "Python syntax and runnable example", 2)
        add_code(doc, chapter["code"])
        add_heading(doc, "Expected output", 3)
        add_code(doc, chapter["output"], "OUTPUT")
        add_heading(doc, "Code walkthrough", 3)
        add_body(doc, chapter["walk"])
        if index == 6:
            add_heading(doc, "Choose the method type", 3)
            method_table = doc.add_table(rows=1, cols=3)
            method_table.style = "Light Shading Accent 1"
            for cell, text in zip(method_table.rows[0].cells, ["Method", "Automatic first argument", "Best fit"]):
                set_cell_text(cell, text, True, "FFFFFF", 8)
                shade(cell, NAVY)
            for row in [
                ("Instance", "self", "Uses one object's state"),
                ("Class", "cls", "Uses class state or alternate constructor"),
                ("Static", "none", "Related utility needs neither object nor class"),
            ]:
                for cell, text in zip(method_table.add_row().cells, row):
                    set_cell_text(cell, text, False, INK, 8)
        if index == 8:
            add_heading(doc, "The diamond and cooperative MRO", 2)
            add_body(doc, "A diamond appears when two intermediate classes inherit from the same base and a child inherits from both. Python uses C3 linearization to produce one consistent MRO. When each method calls super(), control follows that MRO, so the shared base can be reached once.")
            extra = EXTRA_EXAMPLES[0]
            add_code(doc, extra[1], extra[0].upper())
            add_code(doc, extra[2], "EXPECTED OUTPUT")
            add_body(doc, extra[3])
        if index == 11:
            extra = EXTRA_EXAMPLES[1]
            add_heading(doc, "Equality, addition, and callable objects", 2)
            add_code(doc, extra[1], extra[0].upper())
            add_code(doc, extra[2], "EXPECTED OUTPUT")
            add_body(doc, extra[3])
        if index == 17:
            extra = EXTRA_EXAMPLES[2]
            add_heading(doc, "Generator and context-manager example", 2)
            add_code(doc, extra[1], extra[0].upper())
            add_code(doc, extra[2], "EXPECTED OUTPUT")
            add_body(doc, extra[3])
        if index == 18:
            add_heading(doc, "Five principles: problem, improved design, and use", 2)
            for case in SOLID_CASES:
                add_heading(doc, case["principle"], 3)
                add_body(doc, "Poorly designed example:")
                add_code(doc, case["bad"], "LESS FLEXIBLE DESIGN")
                add_code(doc, case["bad_output"], "EXAMPLE OUTPUT")
                add_body(doc, "One improved direction:")
                add_code(doc, case["good"], "MORE FOCUSED DESIGN")
                add_code(doc, case["good_output"], "EXPECTED OUTPUT")
                add_body(doc, case["lesson"])
        if index == 21:
            add_heading(doc, "Incorrect code and corrected code", 2)
            for title, bad, good, explanation in MISTAKE_CASES:
                add_heading(doc, title, 3)
                add_body(doc, "Problematic example:")
                add_code(doc, bad, "INCORRECT")
                add_body(doc, "Correction:")
                add_code(doc, good, "CORRECTED")
                add_body(doc, explanation)
        for chapter_number, title, code, output, explanation in SUPPLEMENTAL_EXAMPLES:
            if index == chapter_number:
                add_heading(doc, title, 2)
                add_code(doc, code, "COMPLETE COMPARISON EXAMPLE")
                add_code(doc, output, "EXPECTED OUTPUT")
                add_body(doc, explanation)
        add_heading(doc, "Connect the analogy to the code", 3)
        add_body(doc, f"In this example, {chapter['analogy']} The Python class and object show the same relationship in executable form.")
        add_callout(doc, "COMMON MISTAKE", chapter["mistake"], ORANGE)
        add_heading(doc, "Key terms", 3)
        add_body(doc, chapter["terms"])
        add_heading(doc, "Remember this", 3)
        add_bullets(doc, [
            chapter["topics"][0][0] + ": know what it means and when it helps.",
            "Trace the example by identifying each object, its state, and the method called.",
            "Choose the simplest design that makes changes safe and understandable.",
        ])
        add_heading(doc, "Practice time", 3)
        add_numbered(doc, [
            f"Easy: Define {chapter['topics'][0][0].lower()} in your own words.",
            f"Understanding: Explain how the example would change if there were two objects.",
            f"Coding: Modify the program to add one new value or behavior and print the result.",
            "Challenge: Name one invalid input or edge case and explain how you would test it.",
        ])

    doc.add_page_break()
    add_heading(doc, "Chapter Practice — Answer Hints", 1)
    add_body(doc, "These are model answer directions for the short practice prompts in each chapter. Your exact implementation may differ; focus on correct reasoning and a testable result.")
    for index, chapter in enumerate(CHAPTERS, 1):
        add_heading(doc, f"Chapter {index}: {chapter['title']}", 2)
        add_numbered(doc, [
            f"Easy: {chapter['topics'][0][1]}",
            "Understanding: A second instance has its own identity and normally its own instance state. Shared class data is the exception when explicitly used.",
            f"Coding: Extend the example around {chapter['topics'][0][0].lower()}; add one well-named attribute or method and print its result.",
            f"Challenge: {chapter['mistake']} A good test includes one ordinary value and one boundary or invalid case.",
        ])

    doc.add_page_break()
    add_heading(doc, "Chapter 19 Project Lab — Five Complete Mini Projects", 1)
    add_body(doc, "Each project is intentionally dependency-free. The code can be copied into a .py file and run with Python 3.11+. Begin with the requirement, inspect the flow diagram, then run the program and test an invalid case.")
    for project in PROJECTS:
        doc.add_page_break()
        add_heading(doc, project["name"], 2)
        add_callout(doc, "PROBLEM", project["problem"])
        add_heading(doc, "Requirements", 3)
        add_body(doc, project["requirements"])
        add_heading(doc, "Algorithm", 3)
        add_numbered(doc, PROJECT_ALGORITHMS[project["name"].split(" — ")[0]])
        add_diagram(doc, diagrams[project["class_diagram"]], f"Class diagram: {project['name']} — responsibilities and object relationships.")
        add_diagram(doc, diagrams[project["diagram"]], f"Flowchart: {project['name']} — simplified request-to-result path.")
        add_heading(doc, "Complete source code", 3)
        add_code(doc, project["code"])
        add_heading(doc, "Sample output", 3)
        add_code(doc, project["output"], "EXPECTED OUTPUT")
        add_heading(doc, "Walkthrough", 3)
        add_body(doc, project["walk"])
        add_heading(doc, "Testing examples", 3)
        add_body(doc, project["test"])
        add_callout(doc, "MODIFICATION CHALLENGE", project["challenge"])
        add_callout(doc, "DESIGN NOTE", "Class diagram in words: each named class owns the data and behavior described above; arrows in the flowchart show the order of actions, not hidden external services.")

    doc.add_page_break()
    add_heading(doc, "Quick Comparison Tables", 1)
    comparisons = [
        ("Class", "Object", "description / template", "particular instance with identity and state"),
        ("Attribute", "Method", "named data or computed value", "operation defined on a class"),
        ("Instance attribute", "Class attribute", "per-object data", "class-level data; beware shared mutables"),
        ("self", "cls", "current instance parameter", "current class parameter by convention"),
        ("Instance method", "Class method", "uses self", "@classmethod receives cls"),
        ("Class method", "Static method", "uses class; often alternate constructor", "no automatic self/cls"),
        ("Encapsulation", "Abstraction", "bundle state/behavior; manage access", "expose essentials; hide implementation"),
        ("Inheritance", "Composition", "is-a specialization", "has-a collaborator relationship"),
        ("Overriding", "Overloading", "subclass replaces inherited method", "Python does not dispatch by signature in the usual OOP sense"),
        ("is", "==", "identity", "equality according to value behavior"),
        ("Shallow copy", "Deep copy", "new outer container, nested references shared", "recursively copies nested structure when supported"),
        ("Regular class", "Dataclass", "custom control and behavior", "convenient generated record methods"),
    ]
    table = doc.add_table(rows=1, cols=4)
    table.style = "Light Shading Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, text in zip(table.rows[0].cells, ["Concept A", "Concept B", "A", "B"]):
        set_cell_text(cell, text, True, "FFFFFF", 8)
        shade(cell, NAVY)
    set_repeat_table_header(table.rows[0])
    for row in comparisons:
        cells = table.add_row().cells
        for cell, text in zip(cells, row):
            set_cell_text(cell, text, False, INK, 8)

    doc.add_page_break()
    add_heading(doc, "Chapter 22 Workbook — Exercises", 1)
    add_body(doc, "Attempt the questions before consulting the answer key. For output questions, predict exact output including spaces and line breaks. For debugging, state the error and make the smallest correct change.")
    add_heading(doc, "A. 25 conceptual questions", 2)
    add_numbered(doc, CONCEPT_QUESTIONS)
    add_heading(doc, "B. 15 output-prediction questions", 2)
    for i, (code, _) in enumerate(OUTPUT_QUESTIONS, 1):
        add_heading(doc, f"Output {i}", 3)
        add_code(doc, code, "PREDICT THE OUTPUT")
        add_body(doc, "Write the exact output before checking the answer key.")
    add_heading(doc, "C. 20 coding exercises", 2)
    add_numbered(doc, [q for q, _ in CODING_QUESTIONS])
    add_heading(doc, "D. 10 debugging exercises", 2)
    for i, (code, _) in enumerate(DEBUG_QUESTIONS, 1):
        add_heading(doc, f"Debug {i}", 3)
        add_code(doc, code, "FIND AND FIX THE PROBLEM")
    add_heading(doc, "E. 10 real-world design questions", 2)
    add_numbered(doc, [q for q, _ in DESIGN_QUESTIONS])
    add_heading(doc, "F. 5 combined-concept challenges", 2)
    add_numbered(doc, [q for q, _ in CHALLENGES])

    doc.add_page_break()
    add_heading(doc, "Chapter 22 Answer Key and Explanations", 1)
    add_heading(doc, "A. Conceptual answers", 2)
    answers = [
        "A class describes a kind; an object is one particular instance.",
        "Each instance has its own attributes, so different values can be stored independently.",
        "Instance attributes belong to one object; class attributes are found on the class and can be shared.",
        "self refers to the instance on which the bound method was called.",
        "No. self is a conventional parameter name, not a reserved keyword.",
        "__new__ creates and returns an instance; __init__ initializes that already-created instance.",
        "When behavior needs the class or an alternate constructor should use cls.",
        "It signals an internal-use convention; it does not enforce strict privacy.",
        "It changes the attribute name to reduce accidental subclass clashes; it is not a security lock.",
        "Encapsulation groups state and behavior and manages access; abstraction exposes essentials and hides details.",
        "Example: Car is a Vehicle (is-a); Car has an Engine object (has-a).",
        "A subclass defines a method with the inherited method's name to provide specialized behavior.",
        "super() calls the next implementation in the MRO, supporting cooperative inheritance.",
        "MRO is Python's ordered method lookup path for a class and its bases.",
        "Different alert classes can each implement describe(), and callers can invoke describe() uniformly.",
        "Duck typing checks supported behavior; inheritance describes a declared subtype relationship.",
        "It still lacks required behavior, so it cannot normally be instantiated.",
        "It lets len(obj) ask the object for its length.",
        "Association is a general relationship; composition describes a stronger whole-part design.",
        "is tests whether references identify the same object; == tests equality.",
        "Aliasing means multiple names refer to one object.",
        "A shallow copy makes a new outer object but may share nested values; a deep copy recursively copies nested structures.",
        "default_factory creates a fresh list per instance instead of sharing one mutable list.",
        "Checking first prevents a failed action from leaving partial or invalid state.",
        "A one-time calculation or simple transformation with no meaningful state is often clearer as a function.",
    ]
    add_numbered(doc, answers)

    add_heading(doc, "B. Output answers", 2)
    for i, ((code, answer), explanation) in enumerate(zip(OUTPUT_QUESTIONS, OUTPUT_EXPLANATIONS), 1):
        add_heading(doc, f"Output {i}", 3)
        add_code(doc, answer, "ANSWER")
        add_body(doc, explanation)
    add_heading(doc, "C. Coding exercise model solutions", 2)
    add_body(doc, "These are runnable example solutions. Other implementations are valid if they meet the stated requirements and preserve the same invariants.")
    for i, ((question, _), (code, output, explanation)) in enumerate(zip(CODING_QUESTIONS, CODING_SOLUTIONS), 1):
        add_heading(doc, f"Exercise {i}: {question}", 3)
        add_code(doc, code, "MODEL SOLUTION")
        add_code(doc, output, "EXPECTED OUTPUT")
        add_body(doc, explanation)
    add_heading(doc, "D. Debugging corrections", 2)
    for i, ((bad, prompt), (code, output, explanation)) in enumerate(zip(DEBUG_QUESTIONS, DEBUG_SOLUTIONS), 1):
        add_heading(doc, f"Debug {i}", 3)
        add_body(doc, "Original problem:")
        add_code(doc, bad, "INCORRECT")
        add_body(doc, prompt)
        add_code(doc, code, "CORRECTED")
        add_code(doc, output, "EXPECTED OUTPUT")
        add_body(doc, explanation)
    add_heading(doc, "E. Design answer guides", 2)
    add_numbered(doc, [answer for _, answer in DESIGN_QUESTIONS])
    add_heading(doc, "F. Challenge solution approaches", 2)
    add_numbered(doc, [answer for _, answer in CHALLENGES])

    doc.add_page_break()
    add_heading(doc, "Chapter 23 Final Master Revision Guide", 1)
    add_heading(doc, "One-page OOP cheat sheet", 2)
    add_callout(doc, "REMEMBER", "Class = blueprint; object = instance; attributes = state; methods = behavior; self = current instance; __init__ = initialization; property = managed attribute; inheritance = is-a; composition = has-a; polymorphism = common operation, varied behavior.")
    add_heading(doc, "Complete glossary", 2)
    glossary = [
        ("Abstraction", "Expose essential operations while hiding implementation details."),
        ("Abstract base class", "A class that describes a contract and may contain abstract methods."),
        ("Aggregation", "A whole-part design relationship with relatively independent parts."),
        ("Aliasing", "Two or more names referring to the same object."),
        ("Attribute", "A named value associated with an object or class."),
        ("Class", "A definition from which instances can be created."),
        ("Class attribute", "An attribute defined on a class rather than separately per instance."),
        ("Class method", "A method decorated with @classmethod and conventionally receiving cls."),
        ("Composition", "A stronger whole-part relationship, typically implemented with object references."),
        ("Dataclass", "A class decorated with @dataclass to generate common data-record methods."),
        ("Duck typing", "Using an object based on the operations it supports."),
        ("Encapsulation", "Grouping state and behavior and presenting a controlled interface."),
        ("Exception", "An object used to report an error or unusual condition."),
        ("Identity", "The distinction of one particular object from another."),
        ("Inheritance", "Creating a specialized class from one or more base classes."),
        ("Instance", "An object created from a class."),
        ("Instance attribute", "A value associated with one particular object."),
        ("Instance method", "A method that conventionally receives the current instance as self."),
        ("Invariant", "A condition that a well-designed object keeps true."),
        ("MRO", "The method resolution order used to search classes for attributes."),
        ("Method", "A function defined in a class and accessed through the class or its instances."),
        ("Mutable", "Able to change in place."),
        ("Object", "A value with identity, type, and associated state or behavior."),
        ("Polymorphism", "Using a common operation with objects that provide different implementations."),
        ("Property", "A managed attribute interface defined with @property."),
        ("Reference", "A way a name or object can access another object."),
        ("Shallow copy", "A copy of an outer object that may share nested references."),
        ("Special method", "A method such as __len__ that Python uses to implement an operation."),
        ("Static method", "A @staticmethod with no automatic instance or class argument."),
        ("Type hint", "An annotation describing intended value types; not generally runtime enforcement."),
    ]
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = "Light Shading Accent 1"
    for cell, text in zip(tbl.rows[0].cells, ["Term", "Meaning"]):
        set_cell_text(cell, text, True, "FFFFFF", 8)
        shade(cell, NAVY)
    set_repeat_table_header(tbl.rows[0])
    for term, meaning in glossary:
        cells = tbl.add_row().cells
        set_cell_text(cells[0], term, True, NAVY, 8)
        set_cell_text(cells[1], meaning, False, INK, 8)

    add_heading(doc, "Syntax reference", 2)
    add_code(doc, """class Name:
    shared_value = "class attribute"

    def __init__(self, value):
        self.value = value

    def instance_method(self):
        return self.value

    @classmethod
    def from_value(cls, value):
        return cls(value)

    @staticmethod
    def helper(value):
        return value

    @property
    def display(self):
        return str(self.value)""")
    add_heading(doc, "Important keywords and built-ins", 2)
    keyword_rows = [
        ("class", "Define a class."),
        ("def", "Define a function or method."),
        ("self", "Conventional parameter name for an instance; not a Python keyword."),
        ("return", "Send a value back to the caller."),
        ("super()", "Access the next implementation in the method resolution order."),
        ("is", "Test object identity; commonly used with None."),
        ("raise", "Raise an exception."),
        ("try / except / else / finally", "Handle errors and define success and cleanup paths."),
        ("for / in", "Iterate over an iterable."),
        ("with", "Use a context manager around a block."),
        ("yield", "Produce a value from a generator function."),
        ("isinstance(value, Type)", "Check whether a value is an instance of a type or its subclass."),
        ("len(value)", "Ask an object for its length via __len__."),
        ("sum(values)", "Add numeric values from an iterable."),
        ("property", "Built-in decorator used to define a property interface."),
        ("ABC / abstractmethod", "Names from abc for abstract base class contracts; not Python keywords."),
    ]
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = "Light Shading Accent 1"
    for cell, text in zip(tbl.rows[0].cells, ["Keyword / built-in", "Purpose"]):
        set_cell_text(cell, text, True, "FFFFFF", 8)
        shade(cell, NAVY)
    set_repeat_table_header(tbl.rows[0])
    for name, purpose in keyword_rows:
        cells = tbl.add_row().cells
        set_cell_text(cells[0], name, True, TEAL, 8)
        set_cell_text(cells[1], purpose, False, INK, 8)
    add_heading(doc, "Important decorators and special methods", 2)
    method_rows = [
        ("@property", "managed attribute read"),
        ("@classmethod", "method receives cls"),
        ("@staticmethod", "no automatic first argument"),
        ("@dataclass", "generate common record methods"),
        ("__init__", "initialize an instance"),
        ("__str__ / __repr__", "human / developer representation"),
        ("__len__", "support len(obj)"),
        ("__eq__", "define equality behavior"),
        ("__add__", "define + behavior"),
        ("__iter__ / __next__", "iteration protocol"),
        ("__enter__ / __exit__", "context-manager protocol"),
    ]
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = "Light Shading Accent 1"
    for cell, text in zip(tbl.rows[0].cells, ["Name", "Purpose"]):
        set_cell_text(cell, text, True, "FFFFFF", 8)
        shade(cell, NAVY)
    for name, purpose in method_rows:
        cells = tbl.add_row().cells
        set_cell_text(cells[0], name, True, TEAL, 8)
        set_cell_text(cells[1], purpose, False, INK, 8)

    add_heading(doc, "Self-assessment checklist", 2)
    add_bullets(doc, [
        "I can distinguish a class from an instance and explain object identity.",
        "I can use self, initialize state, and choose instance/class/static methods.",
        "I can validate state with methods and properties and raise clear exceptions.",
        "I can explain inheritance, overriding, super(), MRO, and polymorphism.",
        "I can choose composition when an object has another object.",
        "I can reason about aliases, mutability, equality, and copying.",
        "I can write a small project, test invalid cases, and explain its design.",
    ])
    add_heading(doc, "14-day revision plan", 2)
    add_numbered(doc, [
        "Days 1–2: classes, objects, attributes, methods, and state.",
        "Days 3–4: __init__, self, class methods, and static methods.",
        "Days 5–6: encapsulation, properties, validation, and exceptions.",
        "Days 7–8: inheritance, super(), MRO, polymorphism, and abstraction.",
        "Days 9–10: composition, references, identity, mutability, and copying.",
        "Days 11–12: special methods, dataclasses, iterators, and SOLID.",
        "Day 13: complete a mini project and test invalid input.",
        "Day 14: answer workbook questions and explain the OOP map aloud.",
    ])

    # Make document metadata informative and update fields when opened in Word.
    doc.core_properties.title = "Python OOP Complete Master Guide"
    doc.core_properties.subject = "Beginner-to-intermediate object-oriented programming in Python"
    doc.core_properties.author = "OpenAI"
    settings = doc.settings.element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)
    doc.save(DOCX_PATH)


def verify_code_examples():
    examples = [(f"chapter {i}: {c['title']}", c["code"], c["output"]) for i, c in enumerate(CHAPTERS, 1)]
    examples.extend((p["name"], p["code"], p["output"]) for p in PROJECTS)
    examples.extend((name, code, output) for name, code, output, _ in EXTRA_EXAMPLES)
    examples.extend((f"chapter {chapter}: {title}", code, output)
                    for chapter, title, code, output, _ in SUPPLEMENTAL_EXAMPLES)
    examples.extend((f"output exercise {i}", code, answer)
                    for i, (code, answer) in enumerate(OUTPUT_QUESTIONS, 1))
    examples.extend((f"coding model solution {i}", code, output)
                    for i, (code, output, _) in enumerate(CODING_SOLUTIONS, 1))
    examples.extend((f"debug correction {i}", code, output)
                    for i, (code, output, _) in enumerate(DEBUG_SOLUTIONS, 1))
    for case in SOLID_CASES:
        examples.append((f"{case['principle']} poor example", case["bad"], case["bad_output"]))
        examples.append((f"{case['principle']} improved example", case["good"], case["good_output"]))
    for title, _, corrected, _ in MISTAKE_CASES:
        compile(corrected, f"corrected mistake: {title}", "exec")
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(corrected, f"corrected mistake: {title}", "exec"), {"__name__": "__main__"})
    results = []
    for name, code, expected in examples:
        compile(code, name, "exec")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exec(compile(code, name, "exec"), {"__name__": "__main__"})
        actual = stdout.getvalue().strip()
        if actual != expected.strip():
            raise AssertionError(f"{name} output mismatch:\nexpected={expected!r}\nactual={actual!r}")
        results.append(name)
    return results


def verify_project_behavior():
    environments = []
    for project in PROJECTS:
        environment = {"__name__": "__main__"}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(project["code"], project["name"], "exec"), environment)
        environments.append(environment)

    student = environments[0]["Student"]
    first = student("A", [80])
    second = student("B", [70])
    first.marks.append(90)
    assert second.marks == [70]
    for args in [("", [80]), ("A", []), ("A", [101])]:
        try:
            student(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Student accepted invalid data: {args!r}")

    account = environments[1]["BankAccount"]("Test", 10)
    for action in [lambda: account.deposit(0), lambda: account.withdraw(11)]:
        previous_balance = account.balance
        previous_history = list(account.history)
        try:
            action()
        except (ValueError, environments[1]["InsufficientFundsError"]):
            assert account.balance == previous_balance
            assert account.history == previous_history
        else:
            raise AssertionError("BankAccount accepted an invalid transaction")

    library = environments[2]["Library"]()
    book = environments[2]["Book"]("Test", "Writer")
    library.add(book)
    library.borrow("Test")
    try:
        library.borrow("Test")
    except ValueError:
        assert not book.available
    else:
        raise AssertionError("Library allowed a second borrow")

    cart = environments[3]["ShoppingCart"]()
    product = environments[3]["Product"]("Test", 2)
    for action in [lambda: cart.add(product, 0), lambda: cart.remove(product)]:
        previous_total = cart.total()
        try:
            action()
        except ValueError:
            assert cart.total() == previous_total
        else:
            raise AssertionError("ShoppingCart accepted an invalid quantity")

    alert = environments[4]["SecurityAlert"]
    try:
        alert("Invalid", "urgent", "test")
    except ValueError:
        pass
    else:
        raise AssertionError("SecurityAlert accepted an unsupported severity")
    endpoint_alert = environments[4]["EndpointAlert"]("Inventory", "low", "test")
    assert "endpoint inventory" in endpoint_alert.describe()
    return len(environments)


def verify_document(diagrams, examples_run):
    if not DOCX_PATH.exists() or DOCX_PATH.stat().st_size < 100_000:
        raise AssertionError("DOCX missing or unexpectedly small")
    reopened = Document(DOCX_PATH)
    text = "\n".join(p.text for p in reopened.paragraphs)
    tables_text = "\n".join(cell.text for table in reopened.tables for row in table.rows for cell in row.cells)
    all_text = text + "\n" + tables_text
    required = [c["title"] for c in CHAPTERS]
    missing = [title for title in required if title not in all_text]
    if missing:
        raise AssertionError(f"Missing chapter headings: {missing}")
    if len(reopened.inline_shapes) < len(diagrams):
        raise AssertionError("Some generated diagrams were not embedded")
    expected_examples = (
        len(CHAPTERS) + len(PROJECTS) + len(EXTRA_EXAMPLES)
        + len(SUPPLEMENTAL_EXAMPLES) + len(OUTPUT_QUESTIONS)
        + len(CODING_SOLUTIONS) + len(DEBUG_SOLUTIONS) + len(SOLID_CASES) * 2
    )
    if len(examples_run) != expected_examples:
        raise AssertionError("Not all source examples were run")
    if re.search(r"\b(TODO|PLACEHOLDER|INSERT TEXT HERE)\b", all_text, re.I):
        raise AssertionError("Placeholder text found")
    if len(reopened.tables) < 4:
        raise AssertionError("Expected comparison/reference tables missing")
    if len(all_text.split()) < 20_000:
        raise AssertionError("Textbook content is unexpectedly short")
    required_terms = [
        "procedural and OOP styles", "multilevel", "hierarchical", "multiple",
        "Mobile phones: same class", "Important keywords and built-ins",
        "__new__", "__repr__", "__eq__", "__add__", "__call__",
        "default_factory", "try, except, else, and finally",
        "association", "aggregation", "composition",
        "property setter and deleter", "The diamond and cooperative MRO",
        "model solutions", "Corrected",
    ]
    missing_terms = [term for term in required_terms if term.lower() not in all_text.lower()]
    if missing_terms:
        raise AssertionError(f"Required curriculum content missing: {missing_terms}")
    expected_counts = {
        "chapter answer sections": len(CHAPTERS),
        "coding model solutions": len(CODING_SOLUTIONS),
        "output answer explanations": len(OUTPUT_EXPLANATIONS),
        "debug corrected solutions": len(DEBUG_SOLUTIONS),
        "project algorithms": len(PROJECT_ALGORITHMS),
    }
    if any(count != expected for count, expected in [
        (len(CODING_SOLUTIONS), len(CODING_QUESTIONS)),
        (len(OUTPUT_EXPLANATIONS), len(OUTPUT_QUESTIONS)),
        (len(DEBUG_SOLUTIONS), len(DEBUG_QUESTIONS)),
        (len(PROJECT_ALGORITHMS), len(PROJECTS)),
    ]):
        raise AssertionError(f"Question/answer count mismatch: {expected_counts}")
    if not all((ASSETS / name).exists() for name in [
        "student_flow.png", "bank_flow.png", "library_flow.png", "cart_flow.png",
        "security_flow.png", "oop_mind_map.png", "class_and_objects.png",
        "inheritance_tree.png", "polymorphism.png", "encapsulation.png",
        "abstraction.png", "composition.png", "object_lifecycle.png",
    ]):
        raise AssertionError("One or more required diagram assets are missing")
    return {
        "paragraphs": len(reopened.paragraphs),
        "tables": len(reopened.tables),
        "embedded_diagrams": len(reopened.inline_shapes),
        "styles": len(reopened.styles),
        "bytes": DOCX_PATH.stat().st_size,
    }


def main():
    OUT.mkdir(exist_ok=True)
    diagrams = make_diagrams()
    examples_run = verify_code_examples()
    project_checks = verify_project_behavior()
    build_doc(diagrams)
    report = verify_document(diagrams, examples_run)
    print(f"Created: {DOCX_PATH}")
    print(f"Chapters: {len(CHAPTERS)}")
    print(f"Mini projects: {len(PROJECTS)}")
    print(f"Workbook exercise groups: 25 conceptual, 15 output, 20 coding, 10 debugging, 10 design, 5 challenges")
    print(f"Runnable examples verified: {len(examples_run)}")
    print(f"Project behavior-validation suites passed: {project_checks}")
    print(f"Diagrams embedded: {report['embedded_diagrams']}")
    print(f"Document: {report['bytes']} bytes; {report['paragraphs']} paragraphs; {report['tables']} tables")
    print("Visual PDF rendering: not available (LibreOffice/soffice not installed)")


if __name__ == "__main__":
    main()
