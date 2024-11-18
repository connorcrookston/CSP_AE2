% Infectious Defence Firefighter Problem in MiniZinc

% Parameters
int: V; % Number of vertices
int: T; % Total time steps
set of int: Vertices = 1..V;
set of int: Times = 0..T;

% Input Data
int: root; % The starting node where the fire begins

% Adjacency List
array[Vertices] of set of Vertices: Adj; % Now provided in the data file

% Decision Variables
array[Times, Vertices] of var 0..1: B; % Burning state
array[Times, Vertices] of var 0..1: D; % Defended state
array[Times, Vertices] of var 0..1: A; % Defend action

% Initial Conditions
constraint
  forall (v in Vertices) (
    B[0, v] = if v = root then 1 else 0 endif /\
    D[0, v] = 0 /\
    A[0, v] = 0
  );

% Defend Action Constraints
constraint
  forall (t in 1..T) (
    sum(v in Vertices)(A[t, v]) <= 1 /\
    forall (v in Vertices) (
      A[t, v] <= 1 - B[t-1, v] - D[t-1, v]
    )
  );

% State Transitions
  % Burning State Update
constraint
  forall (t in 1..T) (
    forall (v in Vertices) (
      B[t, v] = 
        if B[t-1, v] = 1 then 1
        else if (1 - D[t-1, v]) = 1 /\ exists(u in Adj[v])(B[t-1, u] = 1) then 1
        else 0
        endif
      endif
    )
  );

  
constraint
  forall (t in 1..T) (
    forall (v in Vertices) (
      % Defended State Update
      D[t, v] >= D[t-1, v] /\
      D[t, v] >= A[t, v] /\
      D[t, v] >= max([D[t-1, u] * (1 - B[t-1, v]) | u in Adj[v]])
    )
  );

% Burning and Defended States Are Exclusive
constraint
  forall (t in 0..T) (
    forall (v in Vertices) (
      B[t, v] + D[t, v] <= 1
    )
  );


% Objective Function
var int: Saved = sum(v in Vertices)(1 - B[T, v]);
var int: TotalDefendActions = sum(t in 1..T)(sum(v in Vertices)(A[t, v]));

solve maximize Saved * V + TotalDefendActions;

output [
    "Vertices saved: " ++ show(Saved)
];

% % Output Section
% output [
%     "\nStatus each turn:\n",
%     concat([ "Turn " ++ show(t) ++ ":\n" ++
%              "  Burning: " ++ show([B[t, v] | v in Vertices]) ++ "\n" ++
%              "  Defended: " ++ show([D[t, v] | v in Vertices]) ++ "\n" ++
%              "  Action: " ++ show([A[t, v] | v in Vertices]) ++ "\n" 
%              | t in 1..T ])
% ]; 


