import pulp

MAX_EXEMPTIONS_PER_YEAR = 3
MAX_PRICE_EXEMPTION = 200   # USD
MAX_WEIGHT_EXEMPTION = 20   # kg

x = pulp.LpVariable("x", 0, 3)
y = pulp.LpVariable("y", cat="Binary")
prob = pulp.LpProblem("myProblem", pulp.LpMaximize)
prob += x + y <= 5
prob += -4*x + y
status = prob.solve()
#status = prob.solve(pulp.GLPK(msg = 0))
pulp.LpStatus[status]
print(pulp.value(x))
print(pulp.value(y))
