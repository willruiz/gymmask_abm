Empirical Fully-connected disease-avoidance simulation with damped chaotic outbreak behavior. 
Converges to SIR Model

Prcoess of project:

Overview:
We will have agents in a gym environment that will interact 
with 2x2 matrix payoffs.

Simple parameters
C: base payoff - mask cost + mask benefit(mb) + social pressure(n, sb) - covid risk(n,bb, )

A. Derive Payoff functions:
 x. parameters: [x, m, p, s,  n, b, c]
 a. CC: x  + p(b) + s(n,b) - m - c(nt - n) [both]
 b. DC: (1. x  - c(nt-n+1), 2. x  + p(n-1) + s(n-1,b) - m - c(nt-n+1))
 c. DD: x  - c(nt-n+2)  [both]

- payoff functions: p(b), s(n,b), c(nt -n)

B.. Design class objects
 a. gym class
 b. agent class

C. Create Data structures 
 a. Fully connected array (non-spatial prototype)
 b. Spatial array
 c. Spatial Network 

D. Implement action equilibriums

Assumptions:
1. Not considering entering/exit strategies
2. Agents entering and exiting is arrival Prcoess
3. Covid cost parameters are independent
4. Agents entering have fixed probability of having covid.


 
