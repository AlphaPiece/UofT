#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.  

'''This file will contain different constraint propagators to be used within 
   bt_search.

A propagator is a function with the following template:
    propagator(csp, newly_instaniated_variable=None)
        ...
        returns (True/False, [(Variable, Value),(Variable,Value),...])
        
    csp is a CSP object, which the propagator can use to get access to
    the variables and constraints of the problem
    
    newly_instaniated_variable is an optional argument;
        if it is not None, then:
            newly_instaniated_variable is the most recently assigned variable
        else:
            the propagator was called before any assignment was made
    
    the prop returns True/False and a list of variable-value pairs;
        the former indicates whether a DWO did NOT occur,
        and the latter specifies each value that was pruned
     
The propagator SHOULD NOT prune a value that has already been pruned
or prune a value twice

In summary, this is what the propagator must do:

    If newly_instantiated_variable = None
      
        for plain backtracking;
            we do nothing...return true, []

        for forward checking;
            we check all unary constraints of the CSP
            
        for gac;
            we establish initial GAC by initializing the GAC queue
            with all constaints of the CSP


     If newly_instantiated_variable = a variable V
      
         for plain backtracking;
            we check all constraints with V that are fully assigned
            (use csp.get_cons_with_var)

         for forward checking;
            we check all constraints with V that have one unassigned variable

         for gac;
            we initialize the GAC queue with all constraints containing V
   '''

def prop_BT(csp, newVar=None):
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []

def prop_FC(csp, newVar=None):
    cons = csp.get_cons_with_var(newVar) if newVar else csp.get_all_cons()
    prunings = []
    for c in cons:
        if c.get_n_unasgn() == 1:
            var = c.get_unasgn_vars()[0]
            for val in var.cur_domain():
                if not c.has_support(var, val):
                    var.prune_value(val)
                    prunings.append((var, val))
                    if var.cur_domain_size() == 0:
                        return False, prunings
    return True, prunings

def prop_GAC(csp, newVar=None):
    cons = csp.get_cons_with_var(newVar) if newVar else csp.get_all_cons()
    c_queue = []
    for c in cons:
        c_queue.append(c)
    prunings = []

    while c_queue:
        c = c_queue.pop(0)
        for var in c.get_unasgn_vars():
            for val in var.cur_domain():
                if not c.has_support(var, val):
                    var.prune_value(val)
                    prunings.append((var, val))
                    if var.cur_domain_size() == 0:
                        return False, prunings
                    else:
                        for new_c in csp.get_cons_with_var(var):
                            c_queue.append(new_c)
    return True, prunings