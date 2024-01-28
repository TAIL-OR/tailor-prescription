import pyomo.environ as pyo
from pyomo.opt import SolverFactory

class Data:
  def __init__(self, filename):
    with open(filename) as file_object:
      self.F, self.E, self.O = [range(int(n)) for n in file_object.readline().split()]
        # F: set of facilities, E: set of equipments, O: set of occupations
      self.K = [int(n) for n in file_object.readline().split()] # K: Built facilities
      self.b = float(file_object.readline()) # b: Budget
      self.c = [] # c: cost of building facilities
      for n in file_object.readline().split():
        if n in self.K:
          self.c.append(0)
        else:
          self.c.append(float(n))
      self.l = [int(n) for n in file_object.readline().split()] # l: lower bound of ICU beds in each facility
      self.u = [int(n) for n in file_object.readline().split()] # u: upper bound of ICU beds in each facility
      self.p = [float(n) for n in file_object.readline().split()] # p: price of each equipment
      self.n = [int(n) for n in file_object.readline().split()] # n: necessary quantity of each equipment for one ICU bed
      self.h = [float(n) for n in file_object.readline().split()] # h: hiring cost of each occupation
      self.r = [float(n) for n in file_object.readline().split()] # r: necessary rate of each occupation per ICU bed
      self.a = [] # a: availability of each equipment in each facility
      for _ in self.F:
        self.a.append([int(n) for n in file_object.readline().split()])
      self.s = [] # s: staff of each occupation in each facility
      for _ in self.F:
        self.s.append([int(n) for n in file_object.readline().split()])

class Model:
  def __init__(self, data):
    model = pyo.ConcreteModel()
    model.F = data.F
    model.E = data.E
    model.O = data.O
    model.K = data.K
    model.x = pyo.Var(model.F, within=pyo.Integers) # x: number of ICU beds in each facility
    model.y = pyo.Var(model.F, within=pyo.Binary) # y: whether each facility is built or not
    model.z = pyo.Var(model.F, model.E, within=pyo.Integers) # z: number of each equipment in each facility
    model.w = pyo.Var(model.F, model.O, within=pyo.Integers) # w: number of each occupation in each facility
    # Objective function
    model.objective = pyo.Objective(expr=sum(model.x[i] for i in model.F), sense=pyo.maximize)
    # Constraints
    model.budget_constraint = pyo.Constraint(expr=sum(data.c[i] * model.y[i] + sum(data.p[j] * model.z[i, j]
      for j in model.E) + sum(data.h[k] * model.w[i, k] for k in model.O) for i in model.F) <= data.b)
    model.equipment_constraint = pyo.ConstraintList()
    for i in model.F:
      for j in model.E:
        model.equipment_constraint.add(data.a[i][j] + model.z[i, j] >= data.n[j] * model.x[i])
    model.staff_constraint = pyo.ConstraintList()
    for i in model.F:
      for k in model.O:
        model.staff_constraint.add(data.s[i][k] + model.w[i, k] >= data.r[k] * model.x[i])
    model.bed_limit_constraint = pyo.ConstraintList()
    for i in model.F:
      model.bed_limit_constraint.add(data.l[i] * model.y[i] <= model.x[i])
      model.bed_limit_constraint.add(model.x[i] <= data.u[i])
    model.y_fix_constraint = pyo.ConstraintList()
    for i in model.K:
      model.y_fix_constraint.add(model.y[i] == 1)
    model.y_dependent_constraint = pyo.ConstraintList()
    for i in model.F:
      model.y_dependent_constraint.add(model.x[i] / data.u[i] <= model.y[i])
      model.y_dependent_constraint.add(model.y[i] <= model.x[i])
    opt = pyo.SolverFactory('appsi_highs')
    results = opt.solve(model, tee=True)
    results.write()

model = Model(Data('../instances/mock.txt'))
