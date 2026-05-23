from flask import Flask, render_template, request, session, redirect, url_for
from solver import build_steps
from checker import is_equivalent

app = Flask(__name__)
app.secret_key = "replace_with_secure_secret_key"


@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        function_input = request.form.get("function", "").strip()

        if not function_input:
            error = "Please enter a function."
            return render_template("index.html", error=error)

        try:
            steps = build_steps(function_input)

            session["steps"] = steps
            session["current_step"] = 0
            session["function"] = function_input

            return redirect(url_for("question"))

        except Exception as e:
            error = f"Invalid function input: {str(e)}"

    return render_template("index.html", error=error)


@app.route("/question", methods=["GET", "POST"])
def question():
    steps = session.get("steps")
    current_step = session.get("current_step", 0)

    if not steps:
        return redirect(url_for("index"))

    if current_step >= len(steps):
        return redirect(url_for("result"))

    step = steps[current_step]

    message = None
    revealed_answer = None
    detailed_solution = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "hint":
            message = step["hint"]

        elif action == "show_answer":
            revealed_answer = step["answer"]

        elif action == "show_solution":
            detailed_solution = step["detailed_solution"]

        elif action == "submit":
            user_answer = request.form.get("answer", "").strip()

            if is_equivalent(user_answer, step["answer"], step["type"]):
                session["current_step"] = current_step + 1
                return redirect(url_for("question"))
            else:
                message = "Wrong answer."

    return render_template(
        "question.html",
        step=step,
        step_number=current_step + 1,
        total_steps=len(steps),
        message=message,
        revealed_answer=revealed_answer,
        detailed_solution=detailed_solution
    )


@app.route("/result")
def result():
    steps = session.get("steps")
    function = session.get("function")

    if not steps:
        return redirect(url_for("index"))

    return render_template("result.html", steps=steps, function=function)


if __name__ == "__main__":
    app.run(debug=True)