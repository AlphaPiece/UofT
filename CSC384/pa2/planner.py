#Look for ### IMPLEMENT BELOW ### tags in this file. These tags indicate what has
#to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os
# Search engines
from search import * 
# Warehouse specific classes
from warehouse import WarehouseState, Direction, warehouse_goal_state

def heur_displaced(state):
    '''A trivial example heuristic that is admissible'''
    '''INPUT: a warehouse state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    '''In this case, simply the number of displaced boxes.'''
    count = 0
    for box in state.boxes:
        if box not in state.storage:
            count += 1
    return count

def heur_manhattan_distance(state):

    '''admissible heuristic: manhattan distance'''
    '''INPUT: a warehouse state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    
    #We want an admissible heuristic, which is an optimistic heuristic. 
    #It must always underestimate the cost to get from the current state to the goal.
    #The sum Manhattan distance of the boxes to their closest storage spaces is such a heuristic.  
    #When calculating distances, assume there are no obstacles on the grid and that several boxes can fit in one storage bin.
    #You should implement this heuristic function exactly, even if it is tempting to improve it.
    #Your function should return a numeric value; this is the estimate of the distance to the goal.
    
    ### IMPLEMENT BELOW ###
    def get_min_storage_distance(box):
        distances = []
        for pos in state.storage:
            # Check if this position is already occupied by some box
            distances.append(abs(box[0] - pos[0]) + abs(box[1] - pos[1]))
        return min(distances)

    distances_sum = 0
    for box in state.boxes:
        distances_sum += get_min_storage_distance(box)
    return distances_sum
    ### END OF IMPLEMENTATION ###

def weighted_astar(initial_state, heuristic, weight, timebound = 10):

    '''Provides an implementation of weighted a-star, as described in the PA2 handout'''
    '''INPUT: a warehouse state that represents the start state, the heursitic to be used,'''
    '''       weight for the A* search (w >= 1), and a timebound (number of seconds)'''
    '''OUTPUT: A WarehouseState (if a goal is found), else False'''
    
    ### IMPLEMENT BELOW ###
    search_engine = SearchEngine('custom', 'full')
    search_engine.init_search(initial_state, warehouse_goal_state, heuristic,
                              (lambda sN: sN.gval + weight * sN.hval))
    return search_engine.search(timebound)[0]
    ### END OF IMPLEMENTATION ###

def iterative_astar(initial_state, heuristic, weight, timebound = 10):

    '''Provides an implementation of iterative a-star, as described in the PA2 handout'''
    '''INPUT: a warehouse state that represents the start state, the heursitic to be used,'''
    '''       weight for the A* search (w >= 1), and a timebound (number of seconds)'''
    '''OUTPUT: A WarehouseState (if a goal is found), else False'''
    
    # HINT: Use os.times()[0] to obtain the clock time. Your code should finish within the timebound.'''
    
    ### IMPLEMENT BELOW ###
    start_time = os.times()[0]
    n = weight
    state = weighted_astar(initial_state, heuristic, weight, timebound)
    if not state:
        return False
    while os.times()[0] - start_time < timebound:
        if n < 0.1:
            n = weight * 0.1
        n /= 3
        weight -= n
        curr_state = weighted_astar(initial_state, heuristic, weight, timebound - (os.times()[0] - start_time))
        if curr_state:
            state = curr_state

    return state
    ### END OF IMPLEMENTATION ###

def heur_alternate(state):

    '''a better warehouse heuristic'''
    '''INPUT: a warehouse state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''        
  
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.
    
    ### IMPLEMENT BELOW ###
    def get_storage_distance(box):
        distances = []
        for pos in state.storage:
            # Check if this position is already occupied by some box
            distance = abs(box[0] - pos[0]) + abs(box[1] - pos[1])
            distances.append(distance)
        return max(distances)

    distances_sum = 0
    for box in state.boxes:
        distances_sum += get_storage_distance(box)
    return distances_sum
    ### END OF IMPLEMENTATION ###