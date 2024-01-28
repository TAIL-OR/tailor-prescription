# Prescriptive model for maximizing ICU beds

This model aims to maximize the allocation of ICU beds in the territory of Brazil's Federal District (DF) during public health emergencies, considering a fixed budget, as well as available equipment and professional staff in each hospital.

## Data

-   $F$: set of hospitals eligible to accommodate ICU beds;

-   $K$: subset of $F$ for hospitals already built;

-   $E$: set of equipment required for allocating an ICU bed;

-   $O$: set of professional occupations required for allocating an ICU bed;

-   $b$: total budget available for ICU bed distribution;

-   $c_i$: construction cost of hospital $i$ ($c_i = 0\ \forall\ i \in K$);

-   $l_i$: lower bound for ICU beds allocated to hospital $i$, if
    built;

-   $u_i$: upper bound for ICU beds allocated to hospital $i$;

-   $p_j$: price of acquiring equipment $j$;

-   $n_j$: number of units of equipment $j$ required per ICU bed;

-   $h_k$: hiring cost of profession $k$;

-   $r_k$: required proportion of profession $k$ per ICU bed;

-   $a_{ji}$: number of units of equipment $j$ at hospital $i$ (including
    those in use);

-   $s_{ki}$: number of people in profession $k$ working at hospital
    $i$.

## Variables

-   $x_i$: number of ICU beds hospital $i$ accommodates;

-   $y_i$: whether hospital $i$ is built;

-   $z_{ji}$: number of units of equipment $j$ purchased for hospital
    $i$;

-   $w_{ki}$: number of people in profession $k$ hired for hospital
    $i$.

## Formulation

$$\begin{align}
    \max &\qquad \sum_{i \in F} x_i \\
\text{subject to}   & \qquad \sum_{i \in F} \left(c_i y_i + \sum_{j \in E} p_j z_{ji} + \sum_{k \in O} h_k w_{ki}\right) \leq b \\
  & \qquad a_{ji} + z_{ji} \geq n_j x_i && i \in F, j \in E \\
  & \qquad s_{ki} + w_{ki} \geq r_k x_i && i \in F, k \in O \\
  & \qquad y_i l_i \leq x_i \leq u_i && i \in F \\
  & \qquad y_i = 1 && i \in K \\
  & \qquad x_i/u_i \leq y_i \leq x_i && i \in F \\
  & \qquad x_i \in \mathbb{Z} && i \in F \\
  & \qquad y_i \in \{0, 1\} && i \in F \\
  & \qquad z_{ji} \in \mathbb{Z} && i \in F, j \in E \\
  & \qquad w_{ki} \in \mathbb{Z} && i \in F, k \in O.
\end{align}
$$

The objective function aims to maximize the total number of ICU beds in the DF. Constraints 1 ensure that the total spending (considering construction costs, equipment acquisition, and professional hiring) does not exceed the available budget. Constraints 2 ensure that the required equipment quantity for each ICU bed in hospitals is met, considering both the existing ($a_{ji}$) and the acquired ($z_{ji}$) equipment. Constraints 3 ensure that the required professional quantity for each ICU bed in hospitals is met, considering both the existing ($s_{ki}$) and the hired ($w_{ki}$) staff. Constraints 4 establish that the number of ICU beds to be allocated in each hospital must lie within the lower and upper bounds set. Constraints 5 indicate the existence of already built hospitals. Constraints 6 ensure that $y_i=1$ if $x_i$ is positive (i.e., if hospital $i$ has at least one ICU bed, then it is necessarily built). Finally, domain constraints 7, 8, 9, and 10 ensure that the variables $x_i$, $z_{ji}$, and $w_{ki}$ are integers, and the variables $y_i$ are binary.

## Installation

Install the package dependencies, then build the pyomo extensions with:

```console
foo@bar:~$ pyomo build-extensions
```

