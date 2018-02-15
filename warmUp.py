#!/usr/bin/env python3
# warmUp.py - Start the day with a mini quiz that adjusts to your
# understanding of the material over time.

import datetime
import numpy as np
import random
import sqlite3

# Build probability model based on date last seen and understanding
def prob_model(cur, tool, num_questions):
    ids = []
    calleds = []
    understandings = []
    components = []
    
    cur.execute("SELECT {}_id, called, understanding FROM {}".format(tool, tool))
    raw_data = cur.fetchall()    
    for i in range(len(raw_data)):
        ids.append(raw_data[i][0])
        calleds.append(raw_data[i][1])
        understandings.append(raw_data[i][2])
    
    # Loop through rows, weighting each question
    for i in range(len(ids)):
        # Increase probability of topics with a weaker understanding
        # If question has no history, make it highly probable
        understanding = understandings[i]
        if understanding == "l":
            weight = 3
        elif understanding == "m":
            weight = 2
        elif understanding == "h":
            weight = 1
        else:
            weight = 1000000
        # Increase probability for topics that haven't been seen lately
        # If question has no history, make it highly probable
        try:
            last_seen = datetime.datetime.strptime(calleds[i], "%Y-%m-%d %H:%M:%S")
            time_diff = datetime.datetime.today().timestamp()-last_seen.timestamp()
        except:
            time_diff = 1000000
        # Combine weighting for understanding & datetime
        component = time_diff * weight
        components.append(component)
    # Use weights to create a probability np array
    prob_arr = np.array(components, dtype=float) / sum(components)
    
    # Select the questions based on the probability array
    chosen_ids = np.random.choice(ids, size=num_questions, replace=False, p=prob_arr)
    
    return chosen_ids

def call_question(cur, tool, chosen_id):
    
    # Call question and its answer
    cur.execute("SELECT {}_id, area, concept, explanation, note FROM {} WHERE {}_id={};".format(tool, tool, tool, chosen_id))
    results = cur.fetchone()
    chosen_id = results[0]
    area = results[1]
    concept = results[2]
    explanation = results[3]
    note = results[4]
    
    # Print question and wait
    print("\nWhat can you tell me about this prompt?")
    print("{}\n{}\n".format(area, concept))
    input("Press enter when you're ready...\n")

    # Reveal the explanation
    print(explanation)
    print(note)
    
    # Prompt user for understanding on scale of l/m/h and store
    new_understanding = input("\nHow well do you understand this? (l/m/h)")
    now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    
    cur.execute("UPDATE {} SET called=?, understanding=? WHERE {}_id=?;".format(tool, tool), (now, new_understanding, chosen_id))
    cur.execute("INSERT INTO calls(tool, prompt, date, understanding) VALUES(?,?,?,?);", (tool, chosen_id, now, new_understanding))

def main():
    # Prompt user for topic and length of quiz
    tool = input("Which tool? Python or Excel\n").lower()
    num_questions = int(input("How many questions?\n"))
    
    # Connect to SQLite db
    conn = sqlite3.connect("warmUp.db")
    cur = conn.cursor()
    
    # Select primary keys of questions
    chosen_ids = prob_model(cur, tool, num_questions)
    
    # Call the questions
    for i in chosen_ids:
        call_question(cur, tool, i)

    conn.commit()

if __name__ == '__main__':
    main()
