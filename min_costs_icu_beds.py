import pyomo.environ as pyo
from pyomo.opt import SolverFactory

class Data:
  def __init__(self, filename):
    with open(filename) as file_object:
      self.F = list(range(int(file_object.readline()))) # F: set of facilities
      self.K = [int(n) for n in file_object.readline().split()] # K: built facilities
      n_req = 0
      req = []
      for n in file_object.readline().split():
        req.append(list(range(n_req, n_req + int(n))))
        n_req += int(n)
      self.E, self.I, self.S = req # E: set of equipments; I: set of infrastructure; S: set of staff
      self.d = int(file_object.readline()) # d: demand of ICU beds
      self.c = [] # c: cost of building facilities
      for i, n in enumerate(file_object.readline().split()):
        if i in self.K:
          self.c.append(0)
        else:
          self.c.append(float(n))
      self.l = [int(n) for n in file_object.readline().split()] # l: lower bound of ICU beds in each facility, if built
      self.u = [int(n) for n in file_object.readline().split()] # u: upper bound of ICU beds in each facility
      self.p = [float(n) for n in file_object.readline().split()] # p: price of each requirement
      self.r = [float(n) for n in file_object.readline().split()] # r: repair price of each requirement (equipments and infrastructure)
      self.n = [float(n) for n in file_object.readline().split()] # n: necessary rate of each requirement per ICU bed
      self.a = [] # a: availability of each requirement in each facility
      for _ in self.F:
        self.a.append([int(n) for n in file_object.readline().split()])
      self.m = [] # m: number of units of each requirement in need of repair
      for _ in self.F:
        self.m.append([int(n) for n in file_object.readline().split()])
      self.t = [] # t: transfer cost of each requirement among hospitals
      for _ in self.E:
        costs_for_req_j = []
        for _ in self.F:
          costs_for_req_j.append([int(n) for n in file_object.readline().split()])
        self.t.append(costs_for_req_j)
      for _ in self.I:
        self.t.append(None)
      for _ in self.S:
        costs_for_req_j = []
        for _ in self.F:
          costs_for_req_j.append([int(n) for n in file_object.readline().split()])
        self.t.append(costs_for_req_j)

  def print_data(self):
    print('F:', self.F)
    print('K:', self.K)
    print('E:', self.E)
    print('I:', self.I)
    print('S:', self.S)
    print('d:', self.d)
    print('c:', self.c)
    print('l:', self.l)
    print('u:', self.u)
    print('p:', self.p)
    print('r:', self.r)
    print('n:', self.n)
    print('a:', self.a)
    print('m:', self.m)
    print('t:', self.t)

class Model:
  def __init__(self, data):
    model = pyo.ConcreteModel()
    model.F = data.F
    model.E = data.E
    model.I = data.I
    model.S = data.S
    model.K = data.K
    model.x = pyo.Var(model.F, within=pyo.Integers) # x: number of ICU beds in each facility
    model.y = pyo.Var(model.F, within=pyo.Binary) # y: whether each facility is built or not
    model.z = pyo.Var(model.F, (model.E + model.I + model.S), within=pyo.Integers) # z: number of each requirement acquired by each facility
    model.w = pyo.Var(model.F, (model.E + model.I), within=pyo.Integers) # w: number of each requirement repaired in each facility
    model.v = pyo.Var((model.E + model.S), model.F, model.F, within=pyo.Integers) # v: number of each requirement transferred from each facility to each facility
    # Objective function
    model.objective = pyo.Objective(expr=sum(data.c[i]*model.y[i] + sum(data.p[j]*model.z[i, j]
      for j in (model.E + model.I + model.S)) + sum(data.m[i][j]*model.w[i, j]
      for j in (model.E + model.I)) + sum(sum(data.t[j][i][l]*model.v[j, i, l]
      for l in model.F if l != i) for j in (model.E + model.S)) for i in model.F),
      sense=pyo.minimize)
    # Constraints
    model.demand_constraint = pyo.Constraint(expr=sum(model.x[i] for i in model.F) >= data.d)
    model.equipment_constraint = pyo.ConstraintList()
    for i in model.F:
      for j in model.E:
        model.equipment_constraint.add(data.a[i][j] + model.z[i, j] + model.w[i, j] +
          sum(model.v[j, i, l] for l in model.F if l != i) >= data.n[j]*model.x[i])
    model.infrastructure_constraint = pyo.ConstraintList()
    for i in model.F:
      for j in model.I:
        model.infrastructure_constraint.add(data.a[i][j] + model.z[i, j] + model.w[i, j] >=
          data.n[j]*model.x[i])
    model.staff_constraint = pyo.ConstraintList()
    for i in model.F:
      for j in model.S:
        model.staff_constraint.add(data.a[i][j] + model.z[i, j] + sum(model.v[j, i, l]
          for l in model.F if l != i) >= data.n[j]*model.x[i])
    model.repair_constraint = pyo.ConstraintList()
    for i in model.F:
      for j in (model.E + model.I):
        model.repair_constraint.add(model.w[i, j] <= data.m[i][j])
    model.bed_limit_constraint = pyo.ConstraintList()
    for i in model.F:
      model.bed_limit_constraint.add(data.l[i]*model.y[i] <= model.x[i])
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

model = Model(Data('instances/mock.txt'))
