# Prescriptive model for cost minimization in ICU bed management

This model aims to minimize costs related to constructing new hospitals and acquiring, repairing, and transfering equipments, infrastructure, and staff while managing the allocation of ICU beds in the territory of Brazil's Federal District.

## Data

- $F$: set of hospitals eligible to accommodate ICU beds;
- $K$: subset of $F$ for hospitals already constructed;
- $R$: set of requirements necessary for allocating an ICU bed;
- $E \subseteq R$: subset of equipment requirements (e.g., ventilator, electrocardiograph);
- $I \subseteq R$: subset of infrastructure requirements (e.g., X-ray room, laundry);
- $S \subseteq R$: subset of staff requirements (e.g., nurse, janitor);
- $d$: total demand for ICU beds;
- $c_i$: construction cost of hospital $i \in F$ ($c_i = 0$ for all $i \in K$);
- $l_i$: minimum number of ICU beds allocated to hospital $i \in F$, if constructed;
- $u_i$: maximum number of ICU beds allocated to hospital $i \in F$;
- $p_j$: price of acquiring requirement $j \in R$;
- $r_j$: repair cost of requirement $j \in E \cup I$;
- $n_j$: proportion of requirement $j$ needed per ICU bed;
- $a_{ji}$: total number of units of requirement $j \in E \cup I$ in working condition at hospital $i \in F$;
- $m_{ji}$: number of units of requirement $j \in E \cup I$ needing repair at hospital $i \in F$ within the analyzed time period;
- $t_{jil}$: cost of transferring requirement $j \in E \cup S$ from hospital $i \in F$ to hospital $l$.

## Variables

- $x_i$: number of ICU beds hospital $i \in F$ should accommodate;
- $y_i$: whether hospital $i \in F$ is constructed;
- $z_{ji}$: number of units of requirement $j \in R$ acquired for hospital $i \in F$;
- $w_{ji}$: number of units of requirement $j \in E \cup I$ from hospital $i \in F$ undergoing repair;
- $v_{jil}$: number of units of requirement $j \in E \cup S$ transferred from hospital $i \in F$ to hospital $l \in F$ (where $l \neq i$).

## Formulation

$$\begin{align}
    \min & \sum_{i \in F} \left(c_i y_i + \sum_{j \in R} p_j z_{ji} + \sum_{j \in E \cup I} m_{ji} w_{ji} + \sum_{j \in E \cup S} \sum_{l \in F\ |\ l \neq i} t_{jil} v_{jil}\right) \\
\text{subject to}   & \quad \sum_{i \in F} x_i \geq d \\
  & \quad a_{ji} + z_{ji} + w_{ji} + \sum_{l \in F\ |\ l \neq i} v_{jli} - v_{jil} \geq n_j x_i \quad \forall\ i \in F, j \in E \\
  & \quad a_{ji} + z_{ji} + w_{ji} \geq n_j x_i \quad \forall\ i \in F, j \in I \\
  & \quad a_{ji} + z_{ji} + \sum_{l \in F\ |\ l \neq i} v_{jli} - v_{jil} \geq n_j x_i \quad \forall\ i \in F, j \in S \\
  & \quad w_{ji} \leq m_{ji} \quad \forall\ i \in F, j \in E \cup I \\
  & \quad y_i l_i \leq x_i \leq u_i \quad \forall\ i \in F \\
  & \quad y_i = 1 \quad \forall\ i \in K \\
  & \quad x_i/u_i \leq y_i \leq x_i \quad \forall\ i \in F \\
  & \quad x_i \in \mathbb{Z} \quad \forall\ i \in F \\
  & \quad y_i \in \{0, 1\} \quad \forall\ i \in F \\
  & \quad z_{ji} \in \mathbb{Z} \quad \forall\ i \in F, j \in R \\
  & \quad w_{ji} \in \mathbb{Z} \quad \forall\ i \in F, j \in E \cup I \\
  & \quad v_{jil} \in \mathbb{Z} \quad \forall\ i, l \in F, j \in E \cup S.
\end{align}
$$

The objective function aims to minimize the sum of costs for constructing new hospitals and acquiring, repairing, and transferring requirements for all hospitals. Constraints 1 ensure that the total demand for ICU beds is met. Constraints 2-4 determine that each hospital has all necessary requirements to operate its ICU beds, considering present requirements ($a_{ji}$), acquired ($z_{ji}$), repaired ($w_{ji}$), incoming transfers ($v_{jli}$), and outgoing transfers ($v_{jil}$). Constraints 5 limit the number of requirements undergoing repair to the number of requirements in that condition in each hospital, while Constraints 6 limit the number of ICU beds per hospital within the minimum and maximum allowed. Constraints 7 inform about existing constructed hospitals. Constraints 8 ensure that $y_i=1$ if $x_i$ is positive (i.e., if hospital $i$ has at least one ICU bed, then it is necessarily constructed). Finally, Domain Constraints 9-13 ensure that the variables $x_i$, $z_{ji}$, $w_{ji}$, and $v_{jil}$ are integers, and the variables $y_i$ are binary.

## Installation

Install the package dependencies, then build the pyomo extensions with:

```console
foo@bar:~$ pyomo build-extensions
```

