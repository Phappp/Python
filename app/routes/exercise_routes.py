from app.controllers.exercise_controller import exercise_bp

def register_exercise_routes(app):
    app.register_blueprint(exercise_bp) 