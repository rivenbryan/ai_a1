# =============================
# Student Names: Vincent Hung, Bryan Tay
# Group ID: 28
# Date: February 2, 2024
# =============================
# CISC 352 - W23
# cagey_csp.py
# desc:
#

#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = binary_ne_grid(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array is a list of all variables in the given csp. If you are returning an entire grid's worth of variables
they should be arranged in a linearly, where index 0 represents the top left grid cell, index n-1 represents
the top right grid cell, and index (n^2)-1 represents the bottom right grid cell. Any additional variables you use
should fall after that (i.e., the cage operand variables, if required).

1. binary_ne_grid (worth 10/100 marks)
    - A model of a Cagey grid (without cage constraints) built using only
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a Cagey grid (without cage constraints) built using only n-ary
      all-different constraints for both the row and column constraints.

3. cagey_csp_model (worth 20/100 marks)
    - a model of a Cagey grid built using your choice of (1) binary not-equal, or
      (2) n-ary all-different constraints for the grid, together with Cagey cage
      constraints.


Cagey Grids are addressed as follows (top number represents how the grid cells are adressed in grid definition tuple);
(bottom number represents where the cell would fall in the var_array):
+-------+-------+-------+-------+
|  1,1  |  1,2  |  ...  |  1,n  |
|       |       |       |       |
|   0   |   1   |       |  n-1  |
+-------+-------+-------+-------+
|  2,1  |  2,2  |  ...  |  2,n  |
|       |       |       |       |
|   n   |  n+1  |       | 2n-1  |
+-------+-------+-------+-------+
|  ...  |  ...  |  ...  |  ...  |
|       |       |       |       |
|       |       |       |       |
+-------+-------+-------+-------+
|  n,1  |  n,2  |  ...  |  n,n  |
|       |       |       |       |
|n^2-n-1| n^2-n |       | n^2-1 |
+-------+-------+-------+-------+

Boards are given in the following format:
(n, [cages])

n - is the size of the grid,
cages - is a list of tuples defining all cage constraints on a given grid.


each cage has the following structure
(v, [c1, c2, ..., cm], op)

v - the value of the cage.
[c1, c2, ..., cm] - is a list containing the address of each grid-cell which goes into the cage (e.g [(1,2), (1,1)])
op - a flag containing the operation used in the cage (None if unknown)
      - '+' for addition
      - '-' for subtraction
      - '*' for multiplication
      - '/' for division
      - '?' for unknown/no operation given

An example of a 3x3 puzzle would be defined as:
(3, [(3,[(1,1), (2,1)],"+"),(1, [(1,2)], '?'), (8, [(1,3), (2,3), (2,2)], "+"), (3, [(3,1)], '?'), (3, [(3,2), (3,3)], "+")])

'''

import itertools
from cspbase import *
#(1,n) != (1,n+1) != (1,n+2) Rows NE
#(n,1) != (n+1,1) != (n+2,1) Cols NE
def binary_ne_grid(cagey_grid):
    #Create grid
    n = cagey_grid[0] #index 0 should be size of the grid
    domain = [x+1 for x in range(n)] # [1,2,3]
    variable_grid = []
    
    
    #Create Variable grid, with cspbase
    #nxn array where each cell is Variable object which has domain of 1,2,3. Without contraints, it means that each cell can be any of the values in its domain
    for row in range(1,n+1):
        for col in range(1,n+1):
            variable_grid.append(Variable('Cell({},{})'.format(row,col),domain)) #Create variables for grid
    csp_grid = CSP("Grid",variable_grid)#create CSP object with grid of variables
  
    for row in range(n):
        sat_tuple = []
        #find all combinations, improve to itertools if theres time
        for satrow in range(1,n+1):
            for satcol in range(1,n+1):
                #Applying constraint
                if satrow != satcol: #Not equals self
                    sat_tuple.append((satrow, satcol))

        for cell in itertools.combinations(range(n), 2):
            #Add the two cells into scope
            row_var = []
            row_var.append(variable_grid[row*n + cell[0]])
            row_var.append(variable_grid[row*n + cell[1]])
            rowcon = Constraint('NE(V{}{}V{}{})'.format(row+1,cell[0]+1,row+1,cell[1]+1), row_var)

            #Acceptable possibilities added to constraint
            rowcon.add_satisfying_tuples(sat_tuple)
            csp_grid.add_constraint(rowcon)
    
    #Same as rows but for coloumns
    for col in range(n):
        sat_tuple = []
        for satrow in range(1,n+1):
            for satcol in range(1,n+1):
                #Applying constraint
                if satrow != satcol:
                    sat_tuple.append((satrow, satcol))
        for cell in itertools.combinations(range(n), 2):
            col_var = []
            col_var.append(variable_grid[col + cell[0]*n])
            col_var.append(variable_grid[col + cell[1]*n])
            ccon = Constraint('NE(V{}{}V{}{})'.format(cell[0]+1,col+1,cell[1]+1,col+1),col_var)

    
            #Acceptable possibilities added
            ccon.add_satisfying_tuples(sat_tuple)
            csp_grid.add_constraint(ccon)

    return csp_grid, variable_grid


#All different 
def nary_ad_grid(cagey_grid):
    #Create grid
    n = cagey_grid[0] #index 0 should be size of the grid
    #variable_grid = [[x for x in range(n)] for y in range(n)]
    domain = [x+1 for x in range(n)]
    variable_grid = []
    
    
    #Create Variable grid, with cspbase
    # nxn array where each cell is Variable object which has domain of 1-n. Without contraints, it means that each cell can be any of the values in its domain
    for row in range(1,n+1):
        for col in range(1,n+1):
            variable_grid.append(Variable('Cell({},{})'.format(row,col),domain))
    csp_grid = CSP("Grid",variable_grid)
    
    #Constraints for Rows
    for row in range(n):
        row_var = []
        for rows in range(n):
            row_var.append(variable_grid[row*n+rows])
        con = Constraint("Row{}".format(row),row_var)
        sat_tuples = []
        for combination in itertools.permutations(domain):
            sat_tuples.append(combination) # all possible valid row combinations
        con.add_satisfying_tuples(sat_tuples)
        csp_grid.add_constraint(con)

    #Constraints for Col
    for col in range(n):
        col_var = []
        for row in range(n):
            col_var.append(variable_grid[row*n + col])
        con = Constraint("Col{}".format(col+1), col_var)
        for combination in itertools.permutations(domain):
            sat_tuples.append(combination) # all possible valid row combinations
        con.add_satisfying_tuples(sat_tuples)
        csp_grid.add_constraint(con)

    return csp_grid, variable_grid

#Helper so there isnt a wall of if statements
def useoperator(val,val2,operator):
    if operator == "+":
        return val + val2
    elif operator == "-":
        return val - val2
    elif operator == "*":
        return val * val2
    elif operator == "/":
        return val / val2

def cagey_csp_model(cagey_grid):
    n = cagey_grid[0]
    csp_grid, variable_grid = binary_ne_grid(cagey_grid)
    '''each cage has the following structure
    (v, [c1, c2, ..., cm], op)

    v - the value of the cage.
    [c1, c2, ..., cm] - is a list containing the address of each grid-cell which goes into the cage (e.g [(1,2), (1,1)])
    op - a flag containing the operation used in the cage (None if unknown)'''
    #Extract cages
    #cage[0] = value
    #cage[1] = cells in cage
    #cage[2] = operator
    domain = ['+', '-', '/', '*', '?']
    for cage in cagey_grid[1]:
        #Add Cage as variable
        #Create constraint for cage
        #Create sat_tuples for constraint
        #Add to existing csp_grid
        #Add cage as variable

        #Add cage as variable
        cagevarlist = []
        for x in cage[1]:
            arrayindex = (x[0]-1)*n + (x[1]-1) #Based off explanation of grid
            cagevarlist.append(variable_grid[arrayindex])
        cage_op = Variable('Cage_op({}:{}:{})'.format(cage[0],cage[2],cagevarlist),domain)
        csp_grid.add_var(cage_op)

        #Create constraint for cage
        temp = cagevarlist #create duplicate list to maintain original list without operator added
        temp.append(cage_op)
        cage_con = Constraint('Cage({}:{}:{})'.format(cage[0],cage[2],cagevarlist),temp)

        cage_op.assign(cage[2])

        domains = []
        for v in temp:
            domains.append(v.cur_domain()) # since we select specific operator
        
        #Create sat_tuples for constraint
        sat_tuples = []
        if (cage[2] != "?") or (len(cagevarlist) == 1): #If not ?
            for t in itertools.product(*domains):
                if len(cagevarlist) == 1:#If only 1 cell in cage
                    if cage[0] == t[0]: #If the cell value matchs cage value
                        sat_tuples.append(t) 
                else:
                    total = t[0]
                    for idx in range(1,len(t)-1): #Get sum of cage using operator
                        total = useoperator(total, t[idx], t[-1])
                    if(total == cage[0]): #If total in cage matches value of cage
                        sat_tuples.append(t)
                        print(t)

            cage_con.add_satisfying_tuples(sat_tuples)

        else: #operator is unknown, try them all
            for oper in domain:
                domains[-1] = oper #replace ?
                #Do same as above
                for t in itertools.product(*domains):
                    if len(cagevarlist) == 1:#If only 1 cell in cage (Possible overlap with first part?)
                        if cage[0] == t[0]: #If the cell value matchs cage value
                            sat_tuples.append(t) 
                    else:
                        total = t[0]
                        for idx in range(1,len(t)-1): #Get sum of cage using operator
                            total = useoperator(total, t[idx], t[-1])
                        if(total == cage[0]): #If total in cage matches value of cage
                            sat_tuples.append(t)
                            
            cage_con.add_satisfying_tuples(sat_tuples)
        variable_grid.append(cage_op)
        csp_grid.add_constraint(cage_con)
        
    return csp_grid, variable_grid

        
#test = (3, [(3,[(1,1), (2,1)],"+"),(1, [(1,2)], '?'), (8, [(1,3), (2,3), (2,2)], "+"), (3, [(3,1)], '?'), (3, [(3,2), (3,3)], "+")])
#test1 = (2,[(6, [(1, 1), (1, 2), (2, 1), (2, 2)], '+')])
#binary_ne_grid(test)
#nary_ad_grid(test)
#cagey_csp_model(test1)
#testtttta(test1)
