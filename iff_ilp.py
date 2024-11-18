# Import PuLP library
import pulp

# Define the graph data
V = [1, 2, 3, 4, 5]  # List of vertices
T = 5  # Total time steps
root = 1  # Starting node where the fire begins

# Adjacency list (make sure it matches your graph)
Adj = {
    1: [2, 3],
    2: [1, 3, 4],
    3: [1, 2, 5],
    4: [2, 5],
    5: [3, 4]
}

# Create the ILP problem instance
prob = pulp.LpProblem("InfectiousDefenceFirefighter", pulp.LpMaximize)

# Decision Variables
# Burning state B[t][v]
B = pulp.LpVariable.dicts("B", [(t, v) for t in range(T+1) for v in V], cat='Binary')

# Defended state D[t][v]
D = pulp.LpVariable.dicts("D", [(t, v) for t in range(T+1) for v in V], cat='Binary')

# Defend action A[t][v] (no action at time 0)
A = pulp.LpVariable.dicts("A", [(t, v) for t in range(1, T+1) for v in V], cat='Binary')

# Objective Function: Maximize the number of saved vertices at time T
prob += pulp.lpSum(1 - B[T, v] for v in V), "Total_Saved_Vertices"

# Constraints

# Initial Conditions
for v in V:
    if v == root:
        prob += B[0, v] == 1, f"Initial_Burning_{v}"
    else:
        prob += B[0, v] == 0, f"Initial_Not_Burning_{v}"
    prob += D[0, v] == 0, f"Initial_Not_Defended_{v}"

# Defend Action Constraints
for t in range(1, T+1):
    # At most one defend action per time step
    prob += pulp.lpSum(A[t, v] for v in V) <= 1, f"Defend_Action_Limit_{t}"
    for v in V:
        # Cannot defend a vertex that is already burning or defended
        prob += A[t, v] <= 1 - B[t-1, v] - D[t-1, v], f"Defend_Action_Valid_{t}_{v}"

# State Transitions
for t in range(1, T+1):
    for v in V:
        # Burning State Update
        prob += B[t, v] >= B[t-1, v], f"Burning_Persistence_{t}_{v}"
        for u in Adj[v]:
            prob += B[t, v] >= B[t-1, u] - D[t-1, v], f"Fire_Spread_{t}_{v}_{u}"

        # Defended State Update
        prob += D[t, v] >= D[t-1, v], f"Defended_Persistence_{t}_{v}"
        prob += D[t, v] >= A[t, v], f"Defend_Action_Effect_{t}_{v}"
        for u in Adj[v]:
            prob += D[t, v] >= D[t-1, u] - B[t-1, v], f"Defense_Spread_{t}_{v}_{u}"

        # Exclusive States Constraint
        prob += B[t, v] + D[t, v] <= 1, f"Exclusive_States_{t}_{v}"

# Exclusive States Constraint at time 0
for v in V:
    prob += B[0, v] + D[0, v] <= 1, f"Exclusive_States_0_{v}"

# Solve the problem
prob.solve()

# Output the results
print(f"Status: {pulp.LpStatus[prob.status]}")
print(f"Objective Value (Total Saved Vertices): {int(pulp.value(prob.objective))}\n")

# print("Defend Actions:")
# for t in range(1, T+1):
#     actions = [v for v in V if pulp.value(A[t, v]) == 1]
#     print(f"Time {t}: Defend {actions}")

# print("\nBurning States:")
# for t in range(T+1):
#     burning = [v for v in V if pulp.value(B[t, v]) == 1]
#     print(f"Time {t}: Burning {burning}")

# print("\nDefended States:")
# for t in range(T+1):
#     defended = [v for v in V if pulp.value(D[t, v]) == 1]
#     print(f"Time {t}: Defended {defended}")
