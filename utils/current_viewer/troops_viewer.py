import json
from flask import render_template, jsonify, Blueprint, Flask

def generate_data():
    return [
        {
            "text": "parent1",
            "nodes": [
                { "text": "child1" },
                { "text": "child2" },
                { "text": "child3" }
            ]
        },
        {
            "text": "parent2",
            "nodes": [
                { "text": "child4" },
                { "text": "child5" },
                { "text": "child6" }
            ]
        }
    ]

def generate_data_str():
    return json.dumps(generate_data())