import pickle
from neuron import h
from abstract_circuit import AbstractCircuit, AbsCell, AbsSegment, AbsConnection
import os
import json
import copy


def load_json(file_name):
    with open(file_name, 'r+') as f:
        data_dic = json.load(f)
    return data_dic


def pkl_new2old(config_file, src_file, dst_file):
    config = load_json(config_file)
    cell_info = config["cell_info"]
    cells_id_sim = cell_info["cells_id_sim"]

    circuit = pickle.load(open(src_file, 'rb'))
    conn_dict = {}
    for post_neuron in circuit.neurons:  # for each post neuron
        id_post_cell = post_neuron.index
        if (id_post_cell > 0) and (str(id_post_cell) not in cells_id_sim):
            print("neuron ids in config file and connection do not match!")
            exit()
        id_post_cell = str(id_post_cell)
        for pre_connect in post_neuron.pre:
            if id_post_cell not in conn_dict.keys():
                conn_dict[id_post_cell] = []
            id_pre_cell = pre_connect.pre.index
            id_pre_point = pre_connect.pre_segment.index
            id_post_point = pre_connect.post_segment.index
            category = pre_connect.category
            w = pre_connect.weight
            if (id_pre_cell > 0) and (str(id_pre_cell) not in cells_id_sim):  # for each pre neuron
                print("neuron ids in config file and connection do not match!")
                exit()
            id_pre_cell = str(id_pre_cell)
            # pre_seg = self.get_3dp_segment(str(id_pre_cell), id_pre_point) if id_pre_cell > 0 else None
            # post_seg = self.get_3dp_segment(str(id_post_cell), id_post_point)
            if category == 'gj': # construct gap junction
                cate = 0
                # wx = w
                conn_dict[id_post_cell].append([id_pre_cell, id_pre_point, id_post_point, cate, w])
                # gapjunction = h.gapjunction(post_seg)
                # gapjunction.weight = w
                # gapjunction._ref_vpre = pre_seg._ref_v
                # self.synapse_list.append(gapjunction)
            elif category == 'syn' and w > 0:
                # construct synapse
                cate = 1
                # wx = w
                conn_dict[id_post_cell].append([id_pre_cell, id_pre_point, id_post_point, cate, w])
                # synapse = h.neuron_to_neuron_exc_syn(post_seg) if pre_seg else h.exc_syn_advance(post_seg)
                # synapse.weight = w
                # if pre_seg:
                #     synapse._ref_vpre = pre_seg._ref_v
                # self.synapse_list.append(synapse)
            elif category == 'syn' and w < 0:
                cate = 2
                # wx = w
                conn_dict[id_post_cell].append([id_pre_cell, id_pre_point, id_post_point, cate, -w])
                # synapse = h.neuron_to_neuron_inh_syn(post_seg) if pre_seg else h.inh_syn_advance(post_seg)
                # synapse.weight = abs(w)
                # if pre_seg:
                #     synapse._ref_vpre = pre_seg._ref_v
                # self.synapse_list.append(synapse)
            # if not pre_seg:
                # self.input_synapse[int(abs(id_pre_cell)-1)] = synapse
    print(conn_dict)
    pickle.dump(conn_dict, open(dst_file, 'wb'))


def pkl_newer2old(config_file, src_file, dst_file):
    config = load_json(config_file)["config"]
    cell_info = config["cell_info"]
    cells_id_sim = cell_info["cells_id_sim"]

    circuit = pickle.load(open(src_file, 'rb'))
    conn_dict = {}
    cnt = 0
    cnt_gj, cnt_exc, cnt_inh = 0, 0, 0
    for post_neuron in circuit.cells:  # for each post neuron
        id_post_cell = post_neuron.index
        if (id_post_cell > 0) and (str(id_post_cell) not in cells_id_sim):
            print("neuron ids in config file and connection do not match!")
            exit()
        id_post_cell = str(id_post_cell)
        for pre_connect in post_neuron.pre_connections:
            if id_post_cell not in conn_dict.keys():
                conn_dict[id_post_cell] = []
            if pre_connect.pre_cell is None:
                continue
            id_pre_cell = pre_connect.pre_cell.index
            id_pre_point = pre_connect.pre_segment.index
            id_post_point = pre_connect.post_segment.index
            category = pre_connect.category
            w = pre_connect.weight
            if (id_pre_cell > 0) and (str(id_pre_cell) not in cells_id_sim):
                print("neuron ids in config file and connection do not match!")
                exit()
            id_pre_cell = str(id_pre_cell)
            if category == 'gj': # construct gap junction
                cate = 0
                # wx = w
                conn_dict[id_post_cell].append([id_pre_cell, id_pre_point, id_post_point, cate, w])
                cnt += 1
                cnt_gj += 1
                # gapjunction = h.gapjunction(post_seg)
                # gapjunction.weight = w
                # gapjunction._ref_vpre = pre_seg._ref_v
                # self.synapse_list.append(gapjunction)
            elif category == 'syn' and w > 0:
                # construct synapse
                cate = 1
                # wx = w
                conn_dict[id_post_cell].append([id_pre_cell, id_pre_point, id_post_point, cate, w])
                cnt += 1
                cnt_exc += 1
                # synapse = h.neuron_to_neuron_exc_syn(post_seg) if pre_seg else h.exc_syn_advance(post_seg)
                # synapse.weight = w
                # if pre_seg:
                #     synapse._ref_vpre = pre_seg._ref_v
                # self.synapse_list.append(synapse)
            elif category == 'syn' and w < 0:
                cate = 2
                # wx = w
                conn_dict[id_post_cell].append([id_pre_cell, id_pre_point, id_post_point, cate, -w])
                cnt += 1
                cnt_inh += 1
                # synapse = h.neuron_to_neuron_inh_syn(post_seg) if pre_seg else h.inh_syn_advance(post_seg)
                # synapse.weight = abs(w)
                # if pre_seg:
                #     synapse._ref_vpre = pre_seg._ref_v
                # self.synapse_list.append(synapse)
            # if not pre_seg:
                # self.input_synapse[int(abs(id_pre_cell)-1)] = synapse
    # print(conn_dict)
    print(len(circuit.cells), cnt, len(circuit.connections), len(circuit.input_connections), cnt_gj, cnt_exc+cnt_inh, cnt_exc, cnt_inh)
    pickle.dump(conn_dict, open(dst_file, 'wb'))

import sys
sys.setrecursionlimit(1000000)
def synlist2abs_circuit(opt_weight_file, opt_abs_circuit_file):
    synlist = pickle.load(open(opt_weight_file, 'rb'))
    ref_circuit = pickle.load(open(abs_circuit_file, 'rb'))
    abs_circuit = AbstractCircuit()
    cnt_cell = 0
    cnt_conn = 0
    for cell in ref_circuit.cells:
        abs_cell = AbsCell(index=cell.index, name=cell.name)
        for segment in cell.segments:
            abs_cell.add_segment(AbsSegment(index=segment.index, cell=abs_cell, name=segment.name))
        abs_circuit.add_cell(abs_cell)
        cnt_cell += 1
    for id_post_cell in synlist.keys():
        for id_post_seg in synlist[id_post_cell].keys():
            syninfo_list = synlist[id_post_cell][id_post_seg]
            for syninfo in syninfo_list:
                id_pre_cell, id_pre_seg, category, weight, _ = syninfo
                abs_pre_segment = abs_circuit.cell(int(id_pre_cell)).segments[id_pre_seg]
                abs_post_segment = abs_circuit.cell(int(id_post_cell)).segments[id_post_seg]
                abs_circuit.add_connection(AbsConnection(pre_segment=abs_pre_segment,
                post_segment=abs_post_segment, category=category, weight=weight))
                cnt_conn += 1
    print(f"cell num: {cnt_cell}")
    print(f"connection num: {cnt_conn}")
    pickle.dump(abs_circuit, open(opt_abs_circuit_file, 'wb'))
    print(f"saved abs_circuit into {opt_abs_circuit_file}")



if __name__ == "__main__":
    OUTPUT_PATH = './gain_01/'

    config_file = os.path.join(OUTPUT_PATH, "000_circuit_search_config.json")
    src_file = os.path.join(OUTPUT_PATH, "sample_#0_circuit.pkl")
    dst_file = os.path.join(OUTPUT_PATH, "sample_#0_circuit_old.pkl")
    pkl_newer2old(config_file, src_file, dst_file)

    # opt_weight_file = os.path.join(OUTPUT_PATH, "net_synlist.pkl")
    # abs_circuit_file = os.path.join(OUTPUT_PATH, "sample_#0_circuit.pkl")
    # opt_abs_circuit_file = os.path.join(OUTPUT_PATH, "optimal_abs_circuit.pkl")
    # synlist2abs_circuit(opt_weight_file, opt_abs_circuit_file)
