from MusEciDataStructures import *
import BasicOperations as basic
import inspect

def compare(queryVal, targetVal):
    if queryVal==None:
        return True
    elif sameClass(queryVal, targetVal):
        if targetVal.__class__.__name__=="Note":
            if compareVals(queryVal.pitch, targetVal.pitch):
                if compareVals(queryVal.dur, targetVal.dur):
                    if compareVals(queryVal.vol, targetVal.vol):
                        if compareVals(queryVal.onset, targetVal.onset):
                            if compareParams(queryVal.params, targetVal.params):
                                return True
            return False
        elif targetVal.__class__.__name__=="Rest":
            if compareVals(queryVal.dur, targetVal.dur):
                if compareVals(queryVal.onset, targetVal.onset):
                    if compareParams(queryVal.params, targetVal.params):
                        return True
            return False
        elif targetVal.__class__.__name__=="Seq" or targetVal.__class__.__name__=="Par":
            if compareParams(queryVal.params, targetVal.params):
                if len(queryVal.trees) == len(targetVal.trees):
                    for i in range(0, len(targetVal.trees)):
                        if not(compare(queryVal.trees[i], targetVal.trees[i])):
                            return False
                    return True
            return False
        #elif targetVal.__class__.__name__=="Modify":
        #    if compareParams(queryVal.params, targetVal.params):
        #        if compareVals(queryVal.mod, targetVal.mod):
        #            return compare(queryVal.tree, targetVal.tree)
        #    return False
        elif targetVal.__class__.__name__=="Music":
            if compareParams(queryVal.params, targetVal.params):
                if compareVals(queryVal.bpm, targetVal.bpm):
                    return compare(queryVal.tree, targetVal.tree)
        else:
            raise MusEciException("Unknown class: "+targetVal.__class__.__name__)
    else:
        return False

def compareVals(query, target):
    if inspect.isfunction(query):
        return query(target)
    else:
        return query == target or query==None

def compareParams(x,y):
    return True # TODO?: How should param dictionaries be compared???

def sameClass(x,y):
    return x.__class__.__name__ == y.__class__.__name__


def select(query, target):
    '''
    Looks for matching parts of a Music structure. If a subtree matches completely, it is appended whole and
    not recursively checked. This means that if a chord matches, its individual notes do NOT appear elsewhere
    in the returned list.
    :param query:
    :param target:
    :return:
    '''
    retVals = []
    if target.__class__.__name__=="Note" or target.__class__.__name__=="Rest":
        if compare(query, target):
            retVals.append(target)
    elif target.__class__.__name__=="Seq" or target.__class__.__name__=="Par":
        if compare(query, target):
            retVals.append(target)
        else:
            for t in target.trees:
                retVals = retVals + select(query, t)
    elif target.__class__.__name__=="Music": # of target.__class__.__name__=="Modify"
        if compare(query, target):
            retVals.append(target)
        else:
            for t in target.tree:
                retVals = retVals + select(query, t)
    else:
        raise MusEciException("Unknown class: "+target.__class__.__name__)
    return retVals

