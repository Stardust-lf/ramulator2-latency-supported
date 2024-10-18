
for trace in [600,602,605,625,631,657,641,648,620,623]:
    lc, w, r = 0, 0, 0
    with open('/home/fan/projects/ramulator2/ctraces/{}.trace'.format(trace), 'w+') as fout:
        with open('ori_trace/{}.trace'.format(trace)) as f:
            for line in f:
                if lc % 10000000 == 0:
                    print("{} {}".format(trace, lc))
                if lc >= 30000000:
                    break
                try:
                    sp = line.split(' ')
                    if int(sp[0]) > 4:
                        sp[0] = 4
                    if sp[1] == 'W':
                        fout.write('{0} {1} {2}\n'.format(int(sp[0]), int(sp[2][:-1],16), int(sp[2][:-1],16)))
                        lc += 1
                        w += 1
                    elif sp[1] == 'R':
                        fout.write('{0} {1}\n'.format(int(sp[0]), int(sp[2][:-1],16)))
                        lc +=1
                        r += 1
                except Exception:
                    continue
    print(trace)
    print("w",w)
    print("r",r)
    print(w + r)