import sys

sys.stdin = open('fsa.txt')
sys.stdout = open('result.txt', 'w')

Errors = []


def add_error(e, p=''):
    if e == 1:
        Errors.append('E1: A state \'' + p + '\' is not in set of states')
    elif e == 3:
        Errors.append('E3: A transition \'' + p + '\' is not represented in the alphabet')
    elif e == 2:
        Errors.append('E2: Some states are disjoint')
    elif e == 4:
        Errors.append('E4: Initial state is not defined')
    elif e == 5:
        Errors.append('E5: Input file is malformed')
    elif e == 6:
        Errors.append('E6: FSA is nondeterministic')


used = []


def dfs1(s):
    used[s] = 1
    if s in E:
        for al in E[s]:
            if not used[E[s][al]]:
                dfs1(E[s][al])
    if s in TE:
        for al in TE[s]:
            if not used[TE[s][al]]:
                dfs1(TE[s][al])


reachable = []


def dfs2(s):
    global complete
    reachable[s] = True
    if s in E:
        if len(E[s].keys()) != len(alpha):
            complete = False
        for al in E[s]:
            if not reachable[E[s][al]]:
                dfs2(E[s][al])
    elif len(trans) != 0:
        complete = False


def add_to_R(k, i, j, st):
    if k not in R:
        R[k] = {}
    if i not in R[k]:
        R[k][i] = {}
    if j not in R[k][i]:
        R[k][i][j] = st
    else:
        R[k][i][j] += '|' + st


inp = ['states', 'alpha', 'init.st', 'fin.st', 'trans']
complete = True
states = []
alpha = []
init = []
fin = []
trans = []

for i in range(5):
    st = input()
    st = st.rstrip()
    if st[0:len(inp[i]) + 2] != inp[i] + '={' or st[-1] != '}':
        add_error(5)
    cur_st = st[0:len(inp[i]) - (3 if inp[i].count('.st') != 0 else 0)];
    exec(cur_st + ' = list(st[len(inp[i])+2:-1].split(\',\'))')
    if len(eval(cur_st)) == 1 and eval(cur_st)[0] == '':
        exec(cur_st + ' = []')

for i in states + alpha:
    for ch in i:
        if i in states and ch == '_':
            add_error(5)
            break
        if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9' or ch == '_':
            pass
        else:
            add_error(5)
            break


if len(init) == 0:
    add_error(4)

if len(fin) != 0 and fin[0] not in states:
    add_error(1, fin[0])

used = [False] * len(states)
reachable = [False] * len(states)
E = {}
TE = {}

R = {}

for t in trans:
    sa = t[:t.find('>')]
    sb = t[t.rfind('>') + 1:]
    a, b = -1, -1
    al = t[t.find('>') + 1:t.rfind('>')]

    if sa not in states:
        add_error(1, sa)
    else:
        a = states.index(sa)

    if sb not in states:
        add_error(1, sb)
    else:
        b = states.index(sb)

    if al not in alpha: add_error(3, al)
    if a in E and al in E[a]: add_error(6)

    if a not in E:
        E[a] = {}
    if b not in TE:
        TE[b] = {}

    add_to_R('-1', states[a], states[b], al)

    E[a][al] = b
    TE[b][al] = a

if len(states) != 0:
    dfs1(0)

for i in range(len(states)):
    if not used[i]:
        add_error(2)
        break

if len(init) != 0 and init[0] not in states:
    add_error(1, init[0])

if len(Errors) != 0:
    print('Error:')
    Errors.sort()
    print(Errors[0], end='')
    '''
    for e in Errors:
        print()
        print(e, end = '')
    '''
    sys.stdout.close()
    exit(0)

if len(fin) == 0:
    print('{}', end='')
    exit(0)

dfs2(states.index(init[0]))

for k in states + ['-1']:
    for i in states:
        for j in states:
            if i == j:
                add_to_R(k, i, j, 'eps')
            if k not in R or i not in R[k] or j not in R[k][i]:
                add_to_R(k, i, j, '{}')

for ind_k in range(len(states)):
    k = states[ind_k]
    R[k] = {}
    for i in states:
        for j in states:
            prev_k = ''
            if ind_k == 0:
                prev_k = '-1'
            else:
                prev_k = states[ind_k - 1]
            if i not in R[k]:
                R[k][i] = {}
            R[k][i][j] = '(' + R[prev_k][i][k] + ')' + '(' + R[prev_k][k][k] + ')*(' + R[prev_k][k][j] + ')|(' + \
                         R[prev_k][i][j] + ')'  # TODO: Improve it

ans = ''

for s in fin:
    ans += R[states[-1]][init[0]][s] + '|'

print(ans[:-1], end='')

sys.stdout.close()
