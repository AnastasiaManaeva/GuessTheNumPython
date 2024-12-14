from logging import disable

from flask import Flask, render_template, request, redirect, url_for, session
import random
import math

app = Flask(__name__)
app.secret_key = 'Kalitaev'


@app.route('/', methods=['GET', 'POST'])
def home():
    warning = None

    if request.method == 'POST':
        range_a = request.form.get('rangeA')
        range_b = request.form.get('rangeB')

        if range_a and range_b:
            try:
                A = int(range_a)
                B = int(range_b)

                if A >= B:
                    warning = 'Пожалуйста, введите корректные мин. и макс. значения.'
                    return render_template('index.html', warning=warning)

                session['secret_number'] = random.randint(A, B)
                session['max_attempts'] = (B - A + 1).bit_length()
                max_attempts = session.get('max_attempts')
                session['attempts'] = max_attempts
                session['history'] = []
                history = session.get('history')

                return redirect(url_for('game', history=history, range_a=range_a, range_b=range_b))

            except ValueError:
                warning = 'Пожалуйста, введите корректные числовые значения.'
                return render_template('index.html', warning=warning)
        else:
            warning = 'Пожалуйста, заполните оба поля.'
            return render_template('index.html', warning=warning)

    return render_template('index.html', warning=warning)


@app.route('/restart', methods=['POST'])
def restart():
    session.pop('secret_number', None)
    session.pop('attempts', None)
    session.pop('max_attempts', None)
    session.pop('history', None)
    session.pop('feedback', None)

    return redirect(url_for('home'))


@app.route('/game', methods=['GET', 'POST'])
def game():
    feedback = session.get('feedback', '')
    range_a = request.args.get('range_a')
    range_b = request.args.get('range_b')
    session['range_a'] = range_a
    session['range_b'] = range_b

    if request.method == 'POST':
        user_guess = request.form.get('userGuess')

        if user_guess is not None and session.get('secret_number') is not None:
            user_guess_value = int(user_guess)
            attempts = session.get('attempts', 0)
            attempts -= 1
            session['attempts'] = attempts
            history = session.get('history', [])
            secret_number = session['secret_number']

            print(range_b)
            print(user_guess_value)
            print(range_a)
            print(int(range_b) > user_guess_value > int(range_a))

            if int(range_b) > user_guess_value > int(range_a):
                if user_guess_value < secret_number:
                    feedback = f'Загаданное число больше {user_guess_value}'
                    session['feedback'] = feedback
                    history.append(f'больше {user_guess_value}')
                elif user_guess_value > secret_number:
                    feedback = f'Загаданное число меньше {user_guess_value}'
                    session['feedback'] = feedback
                    history.append(f'меньше {user_guess_value}')
                elif user_guess_value == secret_number:
                    feedback = f'Поздравляем! Вы угадали число {secret_number}'
                    session['feedback'] = feedback
                    disabled = True
                    return render_template('game.html', disabled=disabled, feedback=feedback, attempts_left=0,
                                           history=session.get('history'), range_a=range_a, range_b=range_b)
            else:
                feedback = f'Число не входит в диапазон заданных значений'
                session['feedback'] = feedback
                attempts += 1
                session['attempts'] = attempts

            if attempts <= 0:
                feedback = f'Вы исчерпали все попытки! Загаданное число было {secret_number}.'
                session['feedback'] = feedback
                disabled = True
                return render_template('game.html', disabled=disabled, feedback=feedback, attempts_left=0,
                                       history=session.get('history'), range_a=range_a, range_b=range_b)
            session['history'] = history
        else:
            feedback = "Ошибка: введите корректное число."
    session['feedback'] = feedback
    return render_template('game.html', feedback=feedback, attempts_left=session.get('attempts'),
                       history=session.get('history'), range_a=range_a, range_b=range_b)


if __name__ == '__main__':
    app.run(debug=True)