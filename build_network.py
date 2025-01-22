import os
import shutil
import numpy as np
import pandas as pd
import argparse
import json
from pprint import pprint

from bmtk.builder.networks import NetworkBuilder
from bmtk.builder.bionet.swc_reader import get_swc


def load_models(models_path, model_processing=None, N_default=None):
    models = []
    models_dict = json.load(open(models_path, "r"))
    for layer, layer_dict in models_dict["locations"].items():
        for model_name, models_dict in layer_dict.items():
            ei = models_dict.get("ei", None)
            for model in models_dict["models"]:
                if not model.get("enabled", True):
                    continue

                models.append(
                    {
                        "N": N_default or model.get("N", 1),
                        "pop_name": model_name,
                        "ei": ei,
                        "model_type": model["model_type"],
                        "model_template": model["model_template"],
                        "model_processing": model_processing
                        or model.get("model_processing", None),
                        "dynamics_params": model["dynamics_params"],
                        "morphology": model.get("morphology", None),
                    }
                )

    return models


def build_network(axon_type, rng_seed=None):
    if rng_seed is not None:
        np.random.seed(rng_seed)

    if axon_type == "stub":
        model_processing = "aibs_perisomatic"
        output_dir = "network_stub_mechanism_check"
    elif axon_type in ["axon", "full"]:
        model_processing = "aibs_axon"
        output_dir = "network_axon_mechanism_check"
    else:
        raise ValueError("Unknown axon_type")

    # models = load_models(
    #     'model_props/v1_node_models.biophysical_simplified.json',
    #     model_processing=model_processing,
    #     N_default=1
    # )
    models = load_models(
        "model_props/v1_node_models.biophysical_simplified.mechanism_check.json",
        model_processing=model_processing,
        N_default=1,
    )

    print(f"Found {len(models)} models.")

    net = NetworkBuilder("v1")
    for model in models:
        net.add_nodes(**model)

    net.build()
    net.save(output_dir=output_dir)

    # def set_synapses(src, trg, section_names=('soma', 'apical', 'basal'), distance_range=(0.0, 1.0e20)):
    #     trg_swc = get_swc(trg, morphology_dir='./components/morphologies/', use_cache=True)

    #     sec_ids, seg_xs = trg_swc.choose_sections(section_names, distance_range, n_sections=1)
    #     sec_id, seg_x = sec_ids[0], seg_xs[0]
    #     swc_id, swc_dist = trg_swc.get_swc_id(sec_id, seg_x)
    #     # coords = trg_swc.get_coords(sec_id, seg_x)

    #     return [sec_id, seg_x, swc_id, swc_dist]  # coords[0], coords[y], coords[z]

    # virt = NetworkBuilder('virt')
    # virt.add_nodes(
    #     N=90,
    #     ei='e',
    #     model_type='virtual'
    # )

    # cm = virt.add_edges(
    #     source=virt.nodes(),
    #     target=net.nodes(pop_name='Rorb'),
    #     connection_rule=lambda *_: np.random.randint(5, 12),
    #     delay=2.0,
    #     dynamics_params='AMPA_ExcToExc.json',
    #     model_template='exp2syn'
    # )
    # cm.add_properties('syn_weight', rule=5e-05, dtypes=float)
    # cm.add_properties(
    #     ['afferent_section_id', 'afferent_section_pos', 'afferent_swc_id', 'afferent_swc_pos'],
    #     rule=set_synapses,
    #     rule_params={
    #         'section_names': ['basal', 'apical'],
    #         # 'section_names': ['soma'],
    #         'distance_range': [0.0, 150.0]
    #     },
    #     dtypes=[int, float, int, float]
    # )

    # cm = virt.add_edges(
    #     source=virt.nodes(),
    #     target=net.nodes(pop_name='Nr5a1'),
    #     connection_rule=lambda *_: np.random.randint(5, 12),
    #     delay=2.0,
    #     dynamics_params='AMPA_ExcToExc.json',
    #     model_template='exp2syn'
    # )
    # cm.add_properties('syn_weight', rule=5e-05, dtypes=float)
    # cm.add_properties(
    #     ['afferent_section_id', 'afferent_section_pos', 'afferent_swc_id', 'afferent_swc_pos'],
    #     rule=set_synapses,
    #     rule_params={
    #         'section_names': ['basal', 'apical'],
    #         # 'section_names': ['soma'],
    #         'distance_range': [0.0, 150.0]
    #     },
    #     dtypes=[int, float, int, float]
    # )

    # cm = virt.add_edges(
    #     source=virt.nodes(),
    #     target=net.nodes(pop_name='Scnn1a'),
    #     connection_rule=lambda *_: np.random.randint(5, 12),
    #     delay=2.0,
    #     dynamics_params='AMPA_ExcToExc.json',
    #     model_template='exp2syn'
    # )
    # cm.add_properties('syn_weight', rule=5e-05, dtypes=float)
    # cm.add_properties(
    #     ['afferent_section_id', 'afferent_section_pos', 'afferent_swc_id', 'afferent_swc_pos'],
    #     rule=set_synapses,
    #     rule_params={
    #         'section_names': ['basal', 'apical'],
    #         # 'section_names': ['soma'],
    #         'distance_range': [0.0, 150.0]
    #     },
    #     dtypes=[int, float, int, float]
    # )

    # cm = virt.add_edges(
    #     source=virt.nodes(),
    #     target=net.nodes(pop_name='PV1'),
    #     connection_rule=lambda *_: np.random.randint(2, 10),
    #     delay=2.0,
    #     dynamics_params='AMPA_ExcToInh.json',
    #     model_template='exp2syn'
    # )
    # cm.add_properties('syn_weight', rule=0.0008, dtypes=float)
    # cm.add_properties(
    #     ['afferent_section_id', 'afferent_section_pos', 'afferent_swc_id', 'afferent_swc_pos'],
    #     rule=set_synapses,
    #     rule_params={
    #         'section_names': ['somatic', 'basal'],
    #         # 'section_names': ['soma'],
    #         'distance_range': [0.0, 1.0e+20]
    #     },
    #     dtypes=[int, float, int, float]
    # )

    # cm = virt.add_edges(
    #     source=virt.nodes(),
    #     target=net.nodes(pop_name='PV2'),
    #     connection_rule=lambda *_: np.random.randint(2, 10),
    #     delay=2.0,
    #     dynamics_params='AMPA_ExcToInh.json',
    #     model_template='exp2syn'
    # )
    # cm.add_properties('syn_weight', rule=0.0008, dtypes=float)
    # cm.add_properties(
    #     ['afferent_section_id', 'afferent_section_pos', 'afferent_swc_id', 'afferent_swc_pos'],
    #     rule=set_synapses,
    #     rule_params={
    #         'section_names': ['somatic', 'basal'],
    #         # 'section_names': ['soma'],
    #         'distance_range': [0.0, 1.0e+20]
    #     },
    #     dtypes=[int, float, int, float]
    # )

    # virt.build()
    # virt.save(output_dir=output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("axon_types", nargs="*", type=str, default=["stub", "axon"])
    parser.add_argument("--rng-seed", nargs="?", type=int, default=100)
    args = parser.parse_args()

    for axon_type in args.axon_types:
        build_network(axon_type=axon_type, rng_seed=args.rng_seed)
