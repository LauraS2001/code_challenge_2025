import sys
from collections import defaultdict
import os

class Resource:
    def __init__(self, data):
        self.RI = int(data[0])
        self.RA = int(data[1])
        self.RP = int(data[2])
        self.RW = int(data[3])
        self.RM = int(data[4])
        self.RL = int(data[5])
        self.RU = int(data[6])
        self.RT = data[7]
        self.RE = int(data[8]) if len(data) > 8 else 0
        self.state = 'active'  # Possible states: active, downtime, obsolete
        self.turns_active = 0
        self.turns_downtime = 0
        self.remaining_life = self.RL

    def update_state(self):
        if self.state == 'active':
            self.turns_active += 1
            if self.turns_active >= self.RW:
                self.state = 'downtime'
                self.turns_active = 0
        elif self.state == 'downtime':
            self.turns_downtime += 1
            if self.turns_downtime >= self.RM:
                self.state = 'active'
                self.turns_downtime = 0

        self.remaining_life -= 1
        if self.remaining_life <= 0:
            self.state = 'obsolete'

def parse_input(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()

    D, R, T = map(int, lines[0].split())
    resources = [Resource(lines[i].split()) for i in range(1, R + 1)]

    turns = []
    for i in range(R + 1, R + 1 + T):
        TM, TX, TR = map(int, lines[i].split())
        turns.append({'TM': TM, 'TX': TX, 'TR': TR})

    return D, resources, turns

def write_output(file_path, purchases):
    with open(file_path, 'w') as f:
        for t, res in purchases.items():
            if res:
                f.write(f"{t} {len(res)} {' '.join(map(str, res))}\n")

def calculate_profit(n, turn, TR):
    if n < turn['TM']:
        return 0
    return min(n, turn['TX']) * TR

def main(input_path, output_path):
    D, resources, turns = parse_input(input_path)
    budget = D
    active_resources = []
    purchases = defaultdict(list)
    profits = []

    for t, turn in enumerate(turns):
        # --- Start of Turn ---
        affordable_resources = [r for r in resources if r.RA <= budget and r.state != 'obsolete']
        affordable_resources.sort(key=lambda x: (-x.RU / x.RA, x.RA))  # Maximizing efficiency per cost

        for res in affordable_resources:
            if budget >= res.RA:
                budget -= res.RA
                active_resources.append(res)
                purchases[t].append(res.RI)

        # --- Resource Update ---
        n_powered = 0
        periodic_cost = 0
        for res in active_resources:
            if res.state == 'active':
                n_powered += res.RU
                periodic_cost += res.RP
            res.update_state()

        # Remove obsolete resources
        active_resources = [r for r in active_resources if r.state != 'obsolete']

        # --- Calculate Profit ---
        profit = calculate_profit(n_powered, turn, turn['TR'])
        profits.append(profit)
        print(f"Turn {t+1}: Budget={budget}, Profit={profit}, Periodic Cost={periodic_cost}, Active Resources={len(active_resources)}")

        # --- Update Budget ---
        budget += profit - periodic_cost

    # calculate total profit as the sum of all profits
    score = sum(profits)
    print(f"Total Profit: {score}")

    write_output(output_path, purchases)

if __name__ == "__main__":
    io_dir = os.getcwd() + "/input/"
    # process all input files in the dir
    for file in os.listdir(io_dir):
        if file.endswith(".txt"):
            input_path = io_dir + file
            output_path = os.getcwd() + "/output/output_" + file
            # make dir if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            main(input_path, output_path)