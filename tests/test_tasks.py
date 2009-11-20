import jug.task
from jug.backends.dict_store import dict_store


jug.task.Task.store = dict_store()

def add1(x):
    return x + 1
def add2(x):
    return x + 2

def _assert_tsorted(tasks):
    for i in xrange(len(tasks)):
        for j in xrange(i+1,len(tasks)):
            for dep in list(tasks[i].dependencies) + tasks[i].kwdependencies.values():
                if type(dep) is list:
                    assert tasks[j] not in dep
                else:
                    assert tasks[j] is not dep
            
def test_topological_sort():
    bases = [jug.task.Task(add1,i) for i in xrange(10)]
    derived = [jug.task.Task(add1,t) for t in bases]
    derived2 = [jug.task.Task(add1,t) for t in derived]
    derived3 = [jug.task.Task(add1,t) for t in derived]
    
    alltasks = bases + derived
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived)
    _assert_tsorted(alltasks)
    
    alltasks.reverse()
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived)
    _assert_tsorted(alltasks)

    alltasks = bases + derived
    alltasks.reverse()
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived)
    _assert_tsorted(alltasks)

    alltasks = derived + bases
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived)
    _assert_tsorted(alltasks)

    alltasks = derived + bases + derived2
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived) + len(derived2)
    _assert_tsorted(alltasks)

    alltasks = derived + bases + derived2 + derived3
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived) + len(derived2) + len(derived3)
    _assert_tsorted(alltasks)

def test_topological_sort_kwargs():
    def add2(x):
        return x + 2
    def sumlst(lst,param):
        return sum(lst)

    bases = [jug.task.Task(add2,x=i) for i in xrange(10)]
    derived = [jug.task.Task(sumlst,lst=bases,param=p) for p in xrange(4)]

    alltasks = bases + derived
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived)
    _assert_tsorted(alltasks)
    
    alltasks.reverse()
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived)
    _assert_tsorted(alltasks)

    alltasks = bases + derived
    alltasks.reverse()
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived)
    _assert_tsorted(alltasks)

    alltasks = derived + bases
    jug.task.topological_sort(alltasks)
    assert len(alltasks) == len(bases) + len(derived)
    _assert_tsorted(alltasks)

def data():
    return range(20)
def mult(r,f):
    return [f*rr for rr in r]
def reduce(r):
    return sum(r)

def test_topological_sort_canrun():

    Task = jug.task.Task
    input = Task(data)
    for f in xrange(80):
        Task(reduce, Task(mult,input,f))

    alltasks = jug.task.alltasks
    jug.task.topological_sort(alltasks)
    for t in alltasks:
        assert t.can_run()
        t.run()

def test_load_after_run():
    T = jug.task.Task(add1,1)
    T.run()
    assert T.can_load()

def test_hash_same_func():
    T0 = jug.task.Task(add1,0)
    T1 = jug.task.Task(add1,1)

    assert T0.hash() != T1.hash()
    
def test_hash_different_func():
    T0 = jug.task.Task(add1,0)
    T1 = jug.task.Task(add2,0)

    assert T0.hash() != T1.hash()


def test_taskgenerator():
    @jug.task.TaskGenerator
    def double(x):
        return 2*x
    T=double(2)
    assert type(T) == jug.task.Task
    assert not T.print_result
    @jug.task.TaskGenerator(print_result=True)
    def square(x):
        return x*x
    T=square(2)
    assert type(T) == jug.task.Task
    assert T.print_result


def test_unload():
    T0 = jug.task.Task(add1,0)
    assert not T0.finished
    assert T0.can_run()
    T0.run()
    assert T0.finished
    assert T0.result == 1
    T0.unload()
    assert T0.result == 1

def identity(x):
    return x

def test_cachedfunction():
    assert jug.task.CachedFunction(identity,123) == 123
    assert jug.task.CachedFunction(identity,'mixture') == 'mixture'

def test_npyload():
    import numpy as np
    A = np.arange(23)
    assert np.all(jug.task.CachedFunction(identity,A) == A)

@jug.task.TaskGenerator
def double(x):
    return 2 * x

def test_value():
    two = double(1)
    four = double(two)
    eight = double(four)
    two.run()
    four.run()
    eight.run()
    assert jug.task.value(eight) == 8
