import numpy as np
import sympy
from sympy import Matrix, integrate, simplify, trigsimp, solve

def mintegrate(m, var, l1, l2, mname, sufix, norm=False, do_simplify=False,
               conds='none'):
    print('\tstarting integration of {mname} over {var}'.format(
            mname=mname, var=var))
    m = Matrix(m)
    sympy.var('AAA')
    if norm:
        # changing variables
        subs = {var: (l2-l1)*AAA + l1}
        m = m.subs(subs)
        m *= (l2-l1)
    # integration
    for (i, j), ki in np.ndenumerate(m):
        tmp = '{mname}_{sufix}[{i}, {j}] over {var}'.format(mname=mname,
                  sufix=sufix, i=i, j=j, var=var)
        try:
            if norm:
                ki = integrate(ki, (AAA, 0, 1), conds=conds)
            else:
                ki = integrate(ki, (var, l1, l2), conds=conds)
            print('\tfinished integrate {tmp}'.format(tmp=tmp))
        except:
            print('\t\tintegrate() failed for {tmp}'.format(tmp=tmp))
        m[i, j] = ki
    for (i, j), ki in np.ndenumerate(m):
        tmp = '{mname}_{sufix}[{i}, {j}] over {var}'.format(mname=mname,
                  sufix=sufix, i=i, j=j, var=var)
        try:
            if do_simplify:
                ki = simplify(ki)
            else:
                ki = trigsimp(ki)
        except:
            print('\t\ttrigsimp failed {tmp}'.format(tmp=tmp))
            ki = simplify(ki)
        print('\tfinished simplify {tmp}'.format(tmp=tmp))
        m[i, j] = ki
    # printing
    filename = 'print_{mname}_{sufix}_over_{var}.txt'.format(mname=mname,
                   sufix=sufix, var=var)
    with open(filename, 'w') as f:
        def myprint(sth):
            f.write(str(sth).strip() + '\n')
        myprint('matrix ' + mname + ' in file ' + filename)
        for (i, j), v in np.ndenumerate(m):
            if v:
                myprint(mname + '[{0},{1}] = {2}'.format(i,j,v))
    return m

def dbl_mintegrate(m, a, a1, a2, b, b1, b2, mname, sufix,
        norm1=False, norm2=False, do_simplify=False, conds='none'):
    m = mintegrate(m, a, a1, a2, mname, sufix, norm=norm1,
                   do_simplify=do_simplify, conds=conds)
    m = mintegrate(m, b, b1, b2, mname, sufix, norm=norm2,
                   do_simplify=do_simplify, conds=conds)
    return m

def mprint_mathematica(m, mname, sufix):
    from mathematica_printer import print_mathematica
    filename = 'print_mathematica_{0}_{1}.txt'.format(mname, sufix)
    with open(filename, 'w') as f:
        f.write(print_mathematica(m) + '\n')

def mprint(m, mname, sufix='', header=None):
    if sufix:
        filename = 'print_{mname}_{sufix}.txt'.format(mname=mname, sufix=sufix)
    else:
        filename = 'print_{mname}.txt'.format(mname=mname)
    with open(filename, 'w') as f:
        if header:
            f.write(header)
        def myprint(sth):
            f.write(str(sth).strip() + '\n')
        if sufix:
            myprint('{mname}_{sufix}'.format(mname=mname, sufix=sufix))
        else:
            myprint('{mname}'.format(mname=mname))
        for (i, j), v in np.ndenumerate(m):
            if v:
                myprint('{mname}[row+{i},col+{j}] += {v}'.format(
                    mname=mname, v=v, i=i, j=j))

def mprint_as_sparse(m, mname, sufix, numeric=False, use_cse=False,
        header=None):
    if use_cse:
        subs, m_list = sympy.cse(m)
        for i, v in enumerate(m_list):
            m[i] = v

    filename = 'print_{mname}_{sufix}.txt'.format(mname=mname, sufix=sufix)
    with open(filename, 'w') as f:
        if header:
            f.write(header)
        def myprint(sth):
            f.write(str(sth).strip() + '\n')
        if use_cse:
            myprint('cdefs')
            num = 10
            for i, sub in enumerate(subs[::num]):
                myprint('cdef double ' + ', '.join(
                            map(str, [j[0] for j in subs[num*i:num*(i+1)]])))
            myprint('subs')
            for sub in subs:
                myprint('{0} = {1}'.format(*sub))
        if not numeric:
            myprint('# {mname}_{sufix}'.format(mname=mname, sufix=sufix))
            num = len([i for i in list(m) if i])
            myprint('# {mname}_{sufix}_num={num}'.format(
                mname=mname, sufix=sufix, num=num))
            for (i, j), v in np.ndenumerate(m):
                if v:
                    myprint('c += 1')
                    myprint('{mname}r[c] = row+{i}'.format(mname=mname, i=i))
                    myprint('{mname}c[c] = col+{j}'.format(mname=mname, j=j))
                    myprint('{mname}v[c] += {v}'.format(mname=mname, v=v))
        else:
            myprint('# {mname}_{sufix}'.format(mname=mname, sufix=sufix))
            num = len([i for i in list(m) if i])
            myprint('# {mname}_{sufix}_num={num}'.format(
                mname=mname, sufix=sufix, num=num))
            myprint('#')
            myprint('# values')
            myprint('#')
            for (i, j), v in np.ndenumerate(m):
                if v:
                    myprint('c += 1')
                    myprint('fval[c+fdim*pti] = {v}'.format(mname=mname, v=v))
            myprint('#')
            myprint('# rows and columns')
            myprint('#')
            for (i, j), v in np.ndenumerate(m):
                if v:
                    myprint('c += 1')
                    myprint('csub += 1')
                    myprint('rows[c] = row+{i}'.format(i=i))
                    myprint('cols[c] = col+{j}'.format(j=j))
                    myprint('k0Lv[c] = subv[csub]')
    return open(filename).read()

def old_vdiff(x, vector):
    x = np.array(x)
    shape = x.shape
    ans = [np.array([e.diff(vi) for e in x.ravel()]) for vi in vector]
    ans = [a.reshape(shape) for a in ans]
    return np.array(ans).swapaxes(0, 1)

def vdiff(x, vector):
    x = np.array(x)
    shape = x.shape
    ans = []
    for vi in vector:
        if vi.is_Symbol:
            tmp = []
            for e in x.ravel():
                tmp.append(e.diff(vi))
        else:
            subs = {}
            new_var = sympy.var('new_var')
            for s in vi.free_symbols:
                subs[s] = solve(new_var - vi, s)[0]
            tmp = []
            for e in x.ravel():
                e = e.subs(subs)
                e = e.diff(new_var)
                e = e.subs({new_var: vi})
                tmp.append(e.diff(new_var))
        ans.append(np.array(tmp))
    ans = [a.reshape(shape) for a in ans]
    return np.array(ans).swapaxes(0, 1)

