
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.extend(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    """
    Validates and stores the answer for the current question to Django session.
    """
    if not current_question_id:
        session["answers"] = []
    if not answer:
        return False, "Error: Empty answer provided."

    session.setdefault("answers", []).append(answer.lower())
    session.save()

    return True, ""


def get_next_question(current_question_id):
    """
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    """
    if not current_question_id:
        current_question_id = 1

    total_number_of_questions = len(PYTHON_QUESTION_LIST)
    if current_question_id > total_number_of_questions:
        return None, -1

    question_data = PYTHON_QUESTION_LIST[current_question_id - 1]
    next_question_id = current_question_id + 1

    response_data_list = [question_data["question_text"]]
    response_data_list.extend(question_data["options"])

    return response_data_list, next_question_id


def generate_final_response(session):
    """
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    """
    total_score = 0
    user_answers = session.get("answers", [])
    # Since 1st response is just random string
    if len(user_answers) > 0:
        user_answers = user_answers[1:]
    for index, question in enumerate(PYTHON_QUESTION_LIST):
        user_answer = user_answers[index]
        if user_answer.lower() == question["answer"].lower():
            total_score += 1

    final_response = f"Your Python knowledge score is: {total_score}"
    return final_response
