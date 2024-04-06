from flask import Blueprint, jsonify

tasks_bp = Blueprint("tasks",__name__)

@celery.task
def add(x, y):
    return x + y

@tasks_bp.route("/run_task")
def run_task():
    result = add.delay(3, 5) 
    return jsonify({"task_id": result.id})