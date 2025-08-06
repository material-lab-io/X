#!/usr/bin/env python3
"""Test PlantUML generation only"""

from gemini_dynamic_generator import GeminiDynamicGenerator

# Simple PlantUML test
plantuml_code = """@startuml
Alice -> Bob: Hello
Bob --> Alice: Hi!
@enduml"""

api_key = "AIzaSyC2ZSm7_G9TxUSSrGaOJ2x0ouTDGhGyd9s"
gen = GeminiDynamicGenerator(api_key)

print(f"Testing PlantUML with code:\n{plantuml_code}")
result = gen.generate_plantuml_diagram(plantuml_code)
print(f"Result: {result}")