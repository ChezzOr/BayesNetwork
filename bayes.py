import fileinput
import decimal
import itertools
import sys
import functools


class Node:

    def __init__(self, name):
        self.name = name
        self.probability = -1
        self.parents = []
        self.probabilities = {}

    def set_probability(self, probability):
        self.probability = probability

    def set_parents(self, parents):
        parents = parents.split(',')
        [self.parents.append(parent[1]) for parent in parents if parent[1] not in self.parents]
        self.parents = sorted(self.parents)

    def set_probabilities(self, probabilities):
        self.set_parents(probabilities)
        p_value = float(probabilities.split('=')[1])
        probabilities = probabilities.split(',')
        probabilities = sorted(probabilities, key=lambda x: x[1] )
        dict_k = ''
        for prob in probabilities:
            dict_k += prob[:2]
        self.probabilities[dict_k] = float(decimal.Decimal(p_value))

    def total_probability(self, negative, nodes):
        # print("Function")
        if len(self.parents) == 0 or self.probability != -1:
            if negative:
                return round(float(decimal.Decimal(1) - decimal.Decimal(self.probability)), 7)
            else:
                return round(self.probability, 7)
        else:
            t_p = 0
            keys = self.probabilities.keys()
            for key in keys:
                # print("SubFunction")
                acum = self.probabilities[key]
                # print('Acum:'+str(acum))
                for p_len in range(0, len(key), 2):
                    aux_node = nodes[key[1+p_len]]
                    if len(aux_node.parents) == 0:
                        # print('Key:'+str(key)+" AN 1:" + str(aux_node.probability))
                        if key[p_len] == '+':
                            acum = float(decimal.Decimal(str(aux_node.probability)) *
                                         decimal.Decimal(str(acum)))
                        else:
                            acum = float(
                                (decimal.Decimal(1) -
                                decimal.Decimal(str(aux_node.probability))) *
                                decimal.Decimal(str(acum)))
                        # print("T:"+str(acum))
                    else:
                        #print('Key:'+str(key))
                        #print('p_len:' + str(p_len))
                        #print('probs:' + str(aux_node.probabilities))
                        #print(" AN 2:" + str(aux_node.probabilities[key[:p_len]]))
                        if key[p_len] == '+':
                            acum = float(decimal.Decimal(str(aux_node.probabilities[key[:p_len]])) *
                                         decimal.Decimal(str(acum)))
                        else:
                            acum = float(
                                (decimal.Decimal(1) -
                                decimal.Decimal(str(aux_node.probabilities[key[:p_len]]))) *
                                decimal.Decimal(str(acum)))
                        # print("T:"+str(acum))
                t_p = float(decimal.Decimal(t_p) + decimal.Decimal(acum))
            self.probability = t_p
            # print("Totalprob: "+str(t_p))
            if negative:
                return round(float(decimal.Decimal(1) - decimal.Decimal(t_p)), 7)
            else:
                return round(float(decimal.Decimal(t_p)), 7)

    def enumeration(self, evidences):
        t_p = 0
        keys = self.probabilities.keys()
        evidences = evidences.split(',')
        #print(evidences)
        keys = [key for evidence in evidences for key in keys if key.find(evidence) != -1]
        # print(keys)
        t_p = 0
        for key in keys:
            # print("SubFunction")
            acum = self.probabilities[key]
            # print('Acum:'+str(acum))
            for p_len in range(0, len(key), 2):
                aux_node = nodes[key[1 + p_len]]
                if len(aux_node.parents) == 0:
                    # print('Key:'+str(key)+" AN 1:" + str(aux_node.probability))
                    if key[p_len] == '+':
                        acum = float(decimal.Decimal(str(aux_node.probability)) *
                                     decimal.Decimal(str(acum)))
                    else:
                        acum = float(
                            (decimal.Decimal(1) -
                             decimal.Decimal(str(aux_node.probability))) *
                            decimal.Decimal(str(acum)))
                        # print("T:"+str(acum))
                else:
                    # print('Key:'+str(key)+" AN 2:" + str(aux_node.probabilities[key[:p_len]]))
                    if key[p_len] == '+':
                        acum = float(decimal.Decimal(str(aux_node.probabilities[key[:p_len]])) *
                                     decimal.Decimal(str(acum)))
                    else:
                        acum = float(
                            (decimal.Decimal(1) -
                             decimal.Decimal(str(aux_node.probabilities[key[:p_len]]))) *
                            decimal.Decimal(str(acum)))
                        # print("T:"+str(acum))
            t_p = float(decimal.Decimal(t_p) + decimal.Decimal(acum))
        # print(t_p)
        return t_p


if __name__ == '__main__':
    lines = []
    nodes = {}
    queries = []

    print(sys.version)

    for line in fileinput.input():
        if line[0] != '#':
            line = line.strip('\n')
            line = line.replace(' ', '')
            if line != '':
                lines.append(line)

    #print(lines)

    nodes = {n[0]: Node(n[0]) for n in lines[1].split(",")}

    #print(lines[2:])

    for idx, line in enumerate(lines[3:]):
        if line != '[Queries]':
            if line.find('|') == -1:
                nodes[line[1]].set_probability(float(line.split('=')[1]))
            else:
                prob_l = line.split('|')
                nodes[prob_l[0][1]].set_probabilities(prob_l[1])
        else:
            break

    #print(lines[3+idx:])

    for line in lines[4+idx:]:
        if line.find('|') == -1:
            if line[0] == '+':
                print(str(nodes[line[1]].total_probability(False, nodes)))
            else:
                print(str(nodes[line[1]].total_probability(True, nodes)))
        else:
            if line[0] == '+':
                #print("Enumeration method")
                query = line.split('|')[0]
                query = query.split(',')
                query = [single_q[:2] for single_q in query]
                evidence_nodes = line.split('|')[1].split(',')
                evidence_nodes = [evidence_node[:2] for evidence_node in evidence_nodes]
                # print('Query:'+str(query))
                # print('Evidence:' + str(evidence_nodes))
                has_parents = [evidence
                               for single_q in query
                               for evidence in evidence_nodes
                               if evidence[1:2] in nodes[single_q[1:2]].parents]

                has_parents = [parent[:2] for parent in has_parents]
                # print(has_parents)

                bot = [nodes[has_parent[1]].total_probability(True if has_parent[0] == '-' else False, nodes)
                       for has_parent in has_parents]
                bot = eval(str(bot).replace(',', '*'))

                if len(has_parents) == 0:
                    aux = query
                    query = evidence_nodes
                    evidence_nodes = aux
                    #print('Query:' + str(query))
                    #print('Evidence:' + str(evidence_nodes))
                    has_parents = [parent
                                   for single_q in query
                                   for evidence in evidence_nodes
                                   for parent in nodes[single_q[1:2]].parents]
                    aux_h = []
                    [aux_h.append('+'+parent) for parent in has_parents if parent not in aux_h]
                    [aux_h.append('-'+parent) for parent in has_parents if parent not in aux_h]

                    has_parents = aux_h
                    #print('Parents:'+str(has_parents))
                    #print('Query'+str(query))
                    bot = [nodes[single_q[1]].total_probability(True if single_q[0] == '-' else False, nodes)
                           for single_q in query]
                    bot = eval(str(bot).replace(',', '*'))

                # print(has_parents)
                top_list = [evidence[:2] for evidence in evidence_nodes]
                top = [nodes[single_q[1:2]].enumeration(''.join(top_list)) for single_q in query]
                top = eval(str(top).replace(',', '*'))

                #print('Top:'+str(top[0]))
                #print('Bot:'+str(bot[0]))
                print(str(round((top[0]/bot[0]), 7)))
            else:
                print("-")
    '''
    for n in nodes:
        print(n + ' ' + nodes[n].name + '\n' + str(nodes[n].probability)
              + '\n' + str(nodes[n].probabilities.keys()) + '\n'
              + str(nodes[n].probabilities.values()) + '\n'
              + 'Parents' + str(nodes[n].parents))

        nodes[n].total_probability(False, nodes)'''





