from flask import Flask, request, render_template
from itertools import combinations

app = Flask(__name__)

def find_combinations(dataset1, dataset2):
    def get_combinations(arr, target):
        for r in range(1, len(arr) + 1):
            for combo in combinations(set(arr), r):  # Use set to ensure uniqueness
                if sum(combo) == target:
                    return combo
        return None

    results = {'dataset1_to_dataset2': {}, 'dataset2_to_dataset1': {}}

    # Check combinations from dataset2 that sum up to a number in dataset1
    for target in dataset1:
        combo = get_combinations(dataset2, target)
        if combo:
            results['dataset2_to_dataset1'][target] = combo
        else:
            results['dataset2_to_dataset1'][target] = "No match"

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_datasets():
    try:
        dataset1 = [abs(int(num.replace(',', '').strip())) for num in request.form['dataset1'].splitlines() if num]
        dataset2 = [abs(int(num.replace(',', '').strip())) for num in request.form['dataset2'].splitlines() if num]

        results = find_combinations(dataset1, dataset2)

        return render_template('index.html', results=results)  # Pass results to template
    except ValueError:
        return render_template('index.html', result="Please enter valid integers.")

if __name__ == '__main__':
    app.run(debug=True)
