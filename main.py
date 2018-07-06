import json
from functools import reduce
import re
r = {}


print("Enter JSON (Minified)")
bins = json.loads(input())

def _check(conditions):
    globals().update(r)
    condition_met = []
    for condition in conditions:
        for conditio in condition:
            if eval(conditio):
                condition_met.append(True)
            else:
                condition_met.append(False)
    return sum(condition_met)


def _calculate(formula):
    globals().update(r)
    return eval(formula)


def _add(var, data):
    match = re.search(r'([a-z]+)(\[)([0-9])(\])', var)
    if match:
        run = "r['{}'].insert({},'{}')".format(match.group(1), match.group(3), data)
        eval(run)
    else:
        r[var] = data


for block in bins['questions']:
    if isinstance(block, dict):
        if not block.get('conditions', False) and not block.get('calculated_variable'):
            if block.get('instruction', False):
                if block.get('list_var', False):
                    globals().update(r)
                    i = int(block['list_length'])
                    for i in range(i):
                        args = []
                        for v in block['instruction_var']:
                            args.append(eval(v))
                        print(block['instruction'] % tuple(args))
                elif block.get('instruction_var', False):
                    print(block['instruction'] % tuple([r[s] for s in block['instruction_var']]))
                else:
                    print(block['instruction'])
            print(block['text']) if block.get('text', False) else 0
            if block.get('var', False):
                if block.get('options', False):
                    o = block['options']
                    c = True
                    while c:
                        print("Select from following option.")
                        for idx, op in enumerate(o):
                            print("\t{} - {}".format(idx, op))
                        op = (input()).strip()
                        if op.isdigit():
                            op = int(op)
                            if op < len(o):
                                r[block['var']] = o[op]
                                c = False
                            else:
                                print("Wrong option; try again.")
                        elif op.lower() in map(str.lower, o):
                            r [block['var']] = reduce(lambda m, f: m if m.lower() == op.lower() else f, o)
                            c = False
                        else:
                            print("Wrong option; try again.")
                else:
                    _add(block['var'], (input()).strip())
        elif block.get('conditions', False):
            while _check(block['conditions']):
                print(block['text'])
                r[block['var']] = (input()).strip()
        elif block.get('calculated_variable', False):
            if block['calculated_variable']:
                data = _calculate(block['formula'])
                if isinstance(data, list):
                    data = [list(i) for i in data]
                    r[block['var']] = data
                else:
                    r[block['var']] = data
