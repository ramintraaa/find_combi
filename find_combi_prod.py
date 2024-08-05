import tkinter as tk
from tkinter import messagebox
import threading
import time
from collections import Counter

def find_combinations(dataset1, dataset2, progress_callback):
    def get_combinations(arr, target, used_values_count):
        # Dictionary to keep track of possible sums and their respective combinations
        dp = {0: []}
        for num in arr:
            new_entries = {}
            for sub_sum in dp:
                new_sum = sub_sum + num
                if new_sum <= target and used_values_count[num] > 0:
                    # Create a tentative combination to check if it's valid
                    tentative_combination = dp[sub_sum] + [num]
                    # Check if the tentative combination is valid by simulating its usage
                    valid_combination = True
                    temp_used_count = used_values_count.copy()
                    for val in tentative_combination:
                        temp_used_count[val] -= 1
                        if temp_used_count[val] < 0:
                            valid_combination = False
                            break
                    if valid_combination:
                        new_entries[new_sum] = tentative_combination
                        if new_sum == target:
                            # Confirm the valid combination and update the used values count
                            for val in tentative_combination:
                                used_values_count[val] -= 1
                            return tentative_combination  # Return exact match
            dp.update(new_entries)
        
        # Find the smallest combination if no exact match is found
        min_length_combination = None
        for possible_sum in dp:
            if possible_sum <= target:
                combination = dp[possible_sum]
                # Check if the combination is valid by simulating its usage
                valid_combination = True
                temp_used_count = used_values_count.copy()
                for val in combination:
                    temp_used_count[val] -= 1
                    if temp_used_count[val] < 0:
                        valid_combination = False
                        break
                if valid_combination:
                    if min_length_combination is None or len(combination) < len(min_length_combination):
                        min_length_combination = combination
        # Decrement the count of used values if a valid combination is found
        if min_length_combination:
            for val in min_length_combination:
                used_values_count[val] -= 1
        return min_length_combination

    results = {'dataset1_to_dataset2': {}, 'unused_smaller_values': [], 'unmatched_large_values': []}
    used_values_count = Counter(dataset2)

    for idx, target in enumerate(dataset1):
        progress_callback(f"Processing target {idx + 1} of {len(dataset1)}: {target:,}")
        combo = get_combinations(dataset2, target, used_values_count)
        if combo:
            results['dataset1_to_dataset2'][target] = combo
        else:
            results['dataset1_to_dataset2'][target] = "No match"
            results['unmatched_large_values'].append(target)

    for num, count in used_values_count.items():
        if count > 0:
            results['unused_smaller_values'].extend([num] * count)

    return results

def find_backward_combinations(unmatched_large_values, unused_smaller_values):
    def get_combinations(arr, target):
        dp = {0: []}
        for num in arr:
            new_entries = {}
            for sub_sum in dp:
                new_sum = sub_sum + num
                if new_sum <= target:
                    if new_sum not in dp or len(dp[new_sum]) > len(dp[sub_sum]) + 1:
                        new_entries[new_sum] = dp[sub_sum] + [num]
                    if new_sum == target:
                        return dp[sub_sum] + [num]  # Return exact match
            dp.update(new_entries)
        
        min_length_combination = None
        for possible_sum in dp:
            if possible_sum <= target:
                combination = dp[possible_sum]
                if min_length_combination is None or len(combination) < len(min_length_combination):
                    min_length_combination = combination
        return min_length_combination

    backward_results = {}
    for small_value in unused_smaller_values:
        combo = get_combinations(unmatched_large_values, small_value)
        if combo:
            backward_results[small_value] = combo
        else:
            backward_results[small_value] = "No match"
    
    return backward_results

def process_datasets():
    try:
        dataset1 = [abs(int(num.replace(',', '').strip())) for num in text_dataset1.get("1.0", tk.END).splitlines() if num]
        dataset2 = [abs(int(num.replace(',', '').strip())) for num in text_dataset2.get("1.0", tk.END).splitlines() if num]

        # Clear the elapsed time label
        timer_label.config(text="")

        # Start processing in a separate thread
        threading.Thread(target=process_datasets_in_thread, args=(dataset1, dataset2)).start()

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integers.")

def process_datasets_in_thread(dataset1, dataset2):
    start_time = time.time()  # Start the timer

    def update_progress(message):
        root.after(0, update_progress_label, message)

    results = find_combinations(dataset1, dataset2, update_progress)

    # Find backward combinations for unused smaller values and unmatched large values
    backward_results = find_backward_combinations(results['unmatched_large_values'], results['unused_smaller_values'])

    # After processing, update the output and progress
    root.after(0, update_output_text, results, backward_results)
    root.after(0, update_progress_label, "Processing completed.")
    total_time = time.time() - start_time
    root.after(0, update_timer_label, total_time)

def update_progress_label(message):
    progress_label.config(text=message)

def update_timer_label(elapsed_time):
    timer_label.config(text=f"Total time: {elapsed_time:.2f} seconds")

def update_output_text(results, backward_results):
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "\nCombinations\n")
    output_text.insert(tk.END, "---------------------\n")  # Divider line

    # Separate matched and unmatched results for dataset1
    matched_combinations = []
    unmatched_combinations = []

    for key, value in results['dataset1_to_dataset2'].items():
        formatted_key = f"{key:,}"  # Format the key with commas
        if isinstance(value, list):
            formatted_value = [f"[{num:,}]" for num in value]  # Format each number in the combination
            matched_combinations.append(f"{formatted_key}: {' '.join(formatted_value)}")
        else:
            unmatched_combinations.append(f"[{formatted_key}]")  # Only store the value in the unmatched list

    # Output matched combinations first
    for combination in matched_combinations:
        output_text.insert(tk.END, combination + "\n\n")  # Add extra newline for spacing

    # Output unmatched combinations at the end, if any
    if unmatched_combinations:
        output_text.insert(tk.END, "No Match: " + ' '.join(unmatched_combinations) + "\n\n")  # Join unmatched values

    output_text.insert(tk.END, "\n")  # Add space before backward combinations
    output_text.insert(tk.END, "Backward Combinations\n")
    output_text.insert(tk.END, "------------------------\n")  # Divider line

    # Separate matched and unmatched results for backward combinations
    matched_backward_combinations = []
    unmatched_backward_combinations = []

    for key, value in backward_results.items():
        formatted_key = f"{key:,}"  # Format the key with commas
        if isinstance(value, list):
            formatted_value = [f"[{num:,}]" for num in value]  # Format each number in the combination
            matched_backward_combinations.append(f"{formatted_key}: {' '.join(formatted_value)}")
        else:
            unmatched_backward_combinations.append(f"[{formatted_key}]")  # Only store the value in the unmatched list

    # Output matched backward combinations first
    for backward_combination in matched_backward_combinations:
        output_text.insert(tk.END, backward_combination + "\n\n")  # Add extra newline for spacing

    # Output unmatched backward combinations at the end, if any
    if unmatched_backward_combinations:
        output_text.insert(tk.END, "No Match: " + ' '.join(unmatched_backward_combinations) + "\n\n")  # Join unmatched values

    output_text.insert(tk.END, "\n")  # Add extra space after the output

root = tk.Tk()
root.title("Combination Finder (beta)")

label_dataset1 = tk.Label(root, text="Large Values (target)")
label_dataset1.grid(row=0, column=0, padx=10, pady=(10, 0))

text_dataset1 = tk.Text(root, width=50, height=20)
text_dataset1.grid(row=2, column=0, padx=10, pady=(0, 10))

label_dataset2 = tk.Label(root, text="Smaller Values")
label_dataset2.grid(row=0, column=1, padx=10, pady=(10, 0))

text_dataset2 = tk.Text(root, width=50, height=20)
text_dataset2.grid(row=2, column=1, padx=10, pady=(0, 10))

button_process = tk.Button(root, text="Find Combinations", command=process_datasets)
button_process.grid(row=3, column=0, columnspan=2, pady=10)

output_text = tk.Text(root, width=120, height=20)
output_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Label to show progress
progress_label = tk.Label(root, text="")
progress_label.grid(row=5, column=0, columnspan=2, pady=5)

# Label to show total time (this label will be hidden when processing new input)
timer_label = tk.Label(root, text="Total time: 0.00 seconds")
timer_label.grid(row=6, column=0, columnspan=2, pady=5)

root.mainloop()
