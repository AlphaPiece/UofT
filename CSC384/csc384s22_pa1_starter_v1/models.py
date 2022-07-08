#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = warehouse_binary_ne_grid(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the warehouse.

The grid-only models do not need to encode the cage constraints.

1. warehouse_binary_ne_grid
    - A model of the warehouse problem w/o room constraints built using only 
      binary not-equal constraints for the row/column constraints.

2. warehouse_nary_ad_grid
    - A model of the warehouse problem w/o room constraints built using only n-ary 
      all-different constraints for the row/column constraints. 

3. warehouse_full_model
    - A model of the warehouse problem built using either the binary not-equal or n-ary
      all-different constraints for the row/column constraints.
'''
from cspbase import *
import itertools

def warehouse_binary_ne_grid(warehouse_grid):
    n = warehouse_grid[0][0]
    domain = list(range(1, n + 1))
    var_array = [[0 for _ in range(n)] for _ in range(n)]
    vars = []
    cons = []
    sat_tuples = []

    for t in itertools.product(domain, domain):
        if t[0] != t[1]:
            sat_tuples.append(t)

    for i in range(1, len(warehouse_grid)):
        building = warehouse_grid[i]
        operation = building[len(building) - 2]
        target_val = building[len(building) - 1]
        for j in range(len(building) - 2):
            col = building[j] // 10
            row = building[j] % 10
            var = Variable("R{}{}".format(col, row), domain)
            vars.append(var)
            var_array[(n + 1 - row) - 1][col - 1] = var

    def build_row_col_constraints(i, j):
        # Build constraint with every room in the same column
        for k in range(j + 1, n):
            c = Constraint("C(R{}{},R{}{})".format(i + 1, j + 1, i + 1, k + 1), [var_array[i][j], var_array[i][k]])
            c.add_satisfying_tuples(sat_tuples)
            cons.append(c)

        # Build constraint with every room in the same row
        for k in range(i + 1, n):
            c = Constraint("C(R{}{},R{}{})".format(i + 1, j + 1, k + 1, j + 1), [var_array[i][j], var_array[k][j]])
            c.add_satisfying_tuples(sat_tuples)
            cons.append(c)

    for i in range(n):
        for j in range(n):
            build_row_col_constraints(i, j)

    csp = CSP("Warehouse-{}".format(n), vars)
    for c in cons:
        csp.add_constraint(c)

    return csp, var_array

def warehouse_nary_ad_grid(warehouse_grid):
    n = warehouse_grid[0][0]
    domain = list(range(1, n + 1))
    domain_list = [domain for _ in range(n)]
    var_array = [[0 for _ in range(n)] for _ in range(n)]
    vars = []
    cons = []
    sat_tuples = []

    for t in itertools.product(*domain_list):
        if len(set(t)) == len(t):
            sat_tuples.append(t)

    for i in range(1, len(warehouse_grid)):
        building = warehouse_grid[i]
        operation = building[len(building) - 2]
        target_val = building[len(building) - 1]
        for j in range(len(building) - 2):
            col = building[j] // 10
            row = building[j] % 10
            var = Variable("R{}{}".format(col, row), domain)
            vars.append(var)
            var_array[(n + 1 - row) - 1][col - 1] = var

    def build_row_col_constraints(i):
        # Build constraint with every room in the same column
        c_col = Constraint("C(R-Col{})".format(i), [var_array[i][j] for j in range(n)])
        # Build constraint with every room in the same row
        c_row = Constraint("C(R-Row{})".format(i), [var_array[j][i] for j in range(n)])
        c_col.add_satisfying_tuples(sat_tuples)
        c_row.add_satisfying_tuples(sat_tuples)
        cons.append(c_col)
        cons.append(c_row)

    for i in range(n):
        build_row_col_constraints(i)

    csp = CSP("Warehouse-{}".format(n), vars)
    for c in cons:
        csp.add_constraint(c)

    return csp, var_array

def warehouse_full_model(warehouse_grid):
    n = warehouse_grid[0][0]
    domain = list(range(1, n + 1))
    domain_list = [domain for _ in range(n)]
    var_array = [[0 for _ in range(n)] for _ in range(n)]
    vars = []
    cons = []
    rc_sat_tuples = []

    # Get sat_tuples for row and col constraints
    for t in itertools.product(domain, repeat=n):
        if len(set(t)) == len(t):
            rc_sat_tuples.append(t)

    def get_builidng_sat_tuples(operation, target_val, rooms):
        def plus_f(t):
            return sum(t) == target_val
        def min_f(t):
            return min(t) >= target_val
        def max_f(t):
            return max(t) <= target_val

        f = None
        if operation == 0:
            return [(target_val,)]
        elif operation == 1:
            f = plus_f
        elif operation == 2:
            f = min_f
        elif operation == 3:
            f = max_f
        else:
            print("Error: Invalid operation value")

        domain_list = [domain for _ in range(len(rooms))]
        building_sat_tuples = []
        for t in itertools.product(domain, repeat=len(rooms)):
            if f(t):
                building_sat_tuples.append(t)
        return building_sat_tuples

    for i in range(1, len(warehouse_grid)):
        building = warehouse_grid[i]
        operation = building[len(building) - 2]
        target_val = building[len(building) - 1]
        current_building_rooms = []
        for j in range(len(building) - 2):
            col = building[j] // 10
            row = building[j] % 10
            var = Variable("R{}{}".format(col, row), domain)
            vars.append(var)
            current_building_rooms.append(var)
            var_array[(n + 1 - row) - 1][col - 1] = var
        c_building = Constraint("C(Building{})".format(i), current_building_rooms)
        c_building.add_satisfying_tuples(get_builidng_sat_tuples(operation, target_val, current_building_rooms))
        cons.append(c_building)

    def build_row_col_constraints(i):
        # Build constraint with every room in the same column
        c_col = Constraint("C(Col{})".format(i), [var_array[i][j] for j in range(n)])
        # Build constraint with every room in the same row
        c_row = Constraint("C(Row{})".format(i), [var_array[j][i] for j in range(n)])
        c_col.add_satisfying_tuples(rc_sat_tuples)
        c_row.add_satisfying_tuples(rc_sat_tuples)
        cons.append(c_col)
        cons.append(c_row)

    for i in range(n):
        build_row_col_constraints(i)

    csp = CSP("Warehouse-{}".format(n), vars)
    for c in cons:
        csp.add_constraint(c)

    return csp, var_array