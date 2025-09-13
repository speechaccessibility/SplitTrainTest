
lists = {}
for d in range(1,11):
    with open('../lists/list%d.txt'%(d)) as f:
        lists['list%d'%(d)] = [ x.strip() for x in f.readlines() ]


twolists = {}
onelist = {}

for (k,v) in lists.items():
    for u in v:
        if u in twolists:
            twolists[u].append(k)
        elif u in onelist:
            twolists[u] = [onelist.pop(u), k]
        else:
            onelist[u] = k

print('twolists:\n')
print('\n'.join([ '%s %s'%(k,[x for x in v]) for (k,v) in twolists.items()]) + '\n\n')

print('onelists:\n')
print('\n'.join([ '%s %s'%(k,v) for (k,v) in onelist.items()]) + '\n\n')
