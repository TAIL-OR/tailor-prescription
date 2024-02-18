import pyomo.environ as pyo

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
      self.a = [] # a: availability of each working requirement in each facility
      for i in self.F:
        if i in self.K:
          self.a.append([int(n) for n in file_object.readline().split()])
        else:
          self.a.append([0]*len(self.E + self.I + self.S))
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
    # Data
    self.data = data
    self.model = pyo.ConcreteModel()
    self.model.F = self.data.F
    self.model.E = self.data.E
    self.model.I = self.data.I
    self.model.S = self.data.S
    self.model.K = self.data.K

    # Variables
    self.model.x = pyo.Var(self.model.F, within=pyo.NonNegativeIntegers) # x: number of ICU beds in each facility
    self.model.y = pyo.Var(self.model.F, within=pyo.Binary) # y: whether each facility is built or not
    self.model.z = pyo.Var(self.model.F, (self.model.E + self.model.I + self.model.S),
      within=pyo.NonNegativeIntegers) # z: number of each requirement acquired by each facility
    self.model.w = pyo.Var(self.model.F, (self.model.E + self.model.I), within=pyo.NonNegativeIntegers) # w: number of each requirement repaired in each facility
    self.model.v = pyo.Var((self.model.E + self.model.S), self.model.F, self.model.F,
      within=pyo.NonNegativeIntegers) # v: number of each requirement transferred from each facility to each facility
    
    # Objective function
    self.model.objective = pyo.Objective(expr=sum(self.data.c[i]*self.model.y[i] +
        sum(self.data.p[j]*self.model.z[i, j] for j in (self.model.E + self.model.I + self.model.S)) +
        sum(self.data.m[i][j]*self.model.w[i, j] for j in (self.model.E + self.model.I)) +
        sum(sum(self.data.t[j][i][l]*self.model.v[j, i, l] for l in self.model.F if l != i)
        for j in (self.model.E + self.model.S)) for i in self.model.F), sense=pyo.minimize)
    
    # Constraints
    self.model.demand_constraint = pyo.Constraint(expr=sum(self.model.x[i] for i in self.model.F) >=
      self.data.d)
    self.model.equipment_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in self.model.E:
        self.model.equipment_constraint.add(self.data.a[i][j] + self.model.z[i, j] +
          self.model.w[i, j] + sum(self.model.v[j, l, i] - self.model.v[j, i, l] for l in self.model.F
          if l != i) >= self.data.n[j]*self.model.x[i])
    self.model.infrastructure_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in self.model.I:
        self.model.infrastructure_constraint.add(self.data.a[i][j] + self.model.z[i, j] +
          self.model.w[i, j] >= self.data.n[j]*self.model.x[i])
    self.model.staff_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in self.model.S:
        self.model.staff_constraint.add(self.data.a[i][j] + self.model.z[i, j] +
          sum(self.model.v[j, l, i] - self.model.v[j, i, l] for l in self.model.F if l != i) >=
          self.data.n[j]*self.model.x[i])
    self.model.repair_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in (self.model.E + self.model.I):
        self.model.repair_constraint.add(self.model.w[i, j] <= self.data.m[i][j])
    self.model.transfer_constraint = pyo.ConstraintList()
    for j in self.model.E:
      for i in self.model.F:
        for l in self.model.F:
          if l != i:
            self.model.transfer_constraint.add(self.model.v[j, i, l] <= self.data.a[i][j])
    self.model.bed_limit_constraint = pyo.ConstraintList()
    for i in self.model.F:
      self.model.bed_limit_constraint.add(self.data.l[i]*self.model.y[i] <= self.model.x[i])
      self.model.bed_limit_constraint.add(self.model.x[i] <= self.data.u[i])
    self.model.y_fix_constraint = pyo.ConstraintList()
    for i in self.model.K:
      self.model.y_fix_constraint.add(self.model.y[i] == 1)
    self.model.y_dependent_constraint = pyo.ConstraintList()
    for i in self.model.F:
      self.model.y_dependent_constraint.add(self.model.x[i] / self.data.u[i] <= self.model.y[i])
      self.model.y_dependent_constraint.add(self.model.y[i] <= self.model.x[i])
    self.model.write('model.lp', io_options={'symbolic_solver_labels': True})
    opt = pyo.SolverFactory('appsi_highs')
    self.results = opt.solve(self.model, tee=True)
    
  def print_solution(self):
    for i in self.model.F:
      if pyo.value(self.model.y[i]) > 0:
        if i not in self.model.K:
          print('Build Hospital', i)
        else:
          print('Hospital', i)
        cur_beds = min([self.data.a[i][j]/self.data.n[j] for j in self.model.E + self.model.I +
          self.model.S])
        print('\tTotal ICU beds:\t', int(pyo.value(self.model.x[i])))
        print('\tAdded ICU beds:\t', int(pyo.value(self.model.x[i]) - cur_beds))
        
        printedAcquire = False
        for j in self.model.E:
          if pyo.value(self.model.z[i, j]) > 0:
            if not printedAcquire:
              print('\tAcquire:')
              printedAcquire = True
            print('\t\t\t', int(pyo.value(self.model.z[i, j])), 'units of equipment', j)
        for j in self.model.I:
          if pyo.value(self.model.z[i, j]) > 0:
            if not printedAcquire:
              print('\tAcquire:')
              printedAcquire = True
            print('\t\t\t', int(pyo.value(self.model.z[i, j])), 'units of infrastructure', j)
        for j in self.model.S:
          if pyo.value(self.model.z[i, j]) > 0:
            if not printedAcquire:
              print('\tAcquire:')
              printedAcquire = True
            print('\t\t\t', int(pyo.value(self.model.z[i, j])), 'professionals to staff', j)

        printedRepair = False
        for j in self.model.E:
          if pyo.value(self.model.w[i, j]) > 0:
            if not printedRepair:
              print('\tRepair:')
              printedRepair = True
            print('\t\t\t', int(pyo.value(self.model.w[i, j])), 'units of equipment', j)
        for j in self.model.I:
          if pyo.value(self.model.w[i, j]) > 0:
            if not printedRepair:
              print('\tRepair:')
              printedRepair = True
            print('\t\t\t', int(pyo.value(self.model.w[i, j])), 'units of infrastructure', j)
        
        printedTransfer = False
        for j in self.model.E:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, i, l]) > 0:
                if not printedTransfer:
                  print('\tTransfer:')
                  printedTransfer = True
                print('\t\t\t', int(pyo.value(self.model.v[j, i, l])), 'units of equipment', j,
                  'to Hospital', l)
        for j in self.model.S:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, i, l]) > 0:
                if not printedTransfer:
                  print('\tTransfer:')
                  printedTransfer = True
                print('\t\t\t', int(pyo.value(self.model.v[j, i, l])), 'professionals of staff', j,
                  'to Hospital', l)
        
        printedReceive = False
        for j in self.model.E:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, l, i]) > 0:
                if not printedReceive:
                  print('\tReceive:')
                  printedReceive = True
                print('\t\t\t', int(pyo.value(self.model.v[j, l, i])), 'units of equipment', j,
                  'from Hospital', l)
        for j in self.model.S:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, l, i]) > 0:
                if not printedReceive:
                  print('\tReceive:')
                  printedReceive = True
                print('\t\t\t', int(pyo.value(self.model.v[j, l, i])), 'professionals of staff', j,
                  'from Hospital', l)

model = Model(Data('instances/mock.txt'))
model.print_solution()
