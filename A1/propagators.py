# =============================
# Student Names:
# Group ID:
# Date:
# =============================
# CISC 352 - W23
# propagators.py
# desc:
#


#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.

'''This file will contain different constraint propagators to be used within
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method).
      bt_search NEEDS to know this in order to correctly restore these
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated
        constraints)
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
   '''

def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check_tuple(vals):
                return False, []
    return True, []

def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return '''
    
    # Initialize a list to keep track of pruned values.
    vals = []
    constraints = []
    # If no specific variable is provided, get all constraints in the CSP.
    # Otherwise, get only the constraints that involve the new variable.
    if(newVar != None):
        constraints = csp.get_cons_with_var(newVar)
    else:
        constraints = csp.get_all_cons()

    
    # Iterate over all constraints.
    for c in constraints:
        # Check if the constraint has exactly one uninstantiated variable.
        if c.get_n_unasgn() == 1:
            # Get the first (and only) uninstantiated variable in the constraint.
            var = c.get_unasgn_vars()[0]
            
            # Iterate over each value in the current domain of the uninstantiated variable.
            for d_element in var.cur_domain():
                
                if c.has_support(var, d_element) == False:
                    
                    pair = (var, d_element)
                    
                    if pair not in vals:
                        # Prune the value from the variable's domain.
                        var.prune_value(d_element)
                        # Record the pruning.
                        vals.append(pair)
            
            # After pruning, check if the domain of the variable is empty.
            # An empty domain means no values are left that satisfy the constraints,
            # indicating a dead end in the search.
            if var.cur_domain_size() == 0:
                # Return False (indicating failure) and the list of pruned values.
                return False, vals
    
    # If the function has not returned by this point, it means forward checking
    # did not encounter any empty domains. Return True (indicating success)
    # and the list of pruned values.
    return True, vals

    


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Quezue'''
    #IMPLEMENT
    vals = []
    queue = []
    if(newVar == None):
        constraints = csp.get_all_cons() # local variable according to lecture
    else:
        constraints = csp.get_cons_with_var(newVar)

    for c in constraints:
        queue.append(c)

    while len(queue) != 0: # not empty
        c = queue.pop(0)
        variables_inScope = c.get_scope()

        for var in variables_inScope: # Removed-inconsistent-Values(Xi, X)
            for d in var.cur_domain():
                if c.has_support(var, d) == False: # No Y in domain(X) allows (x,Y) satisfy constraint
                    pair = (var, d)
                    if pair not in vals:
                        vals.append(pair)
                        var.prune_value(d) # Delete it.
                        
                    if var.cur_domain_size() == 0: # Meaning we prune every domain from v, reaching deadend.
                        return False, vals
                    else:
                        for elements in csp.get_cons_with_var(vars):
                            if elements not in queue:
                                queue.append(elements) # Add (Xk, *) to queue
    return True, vals
