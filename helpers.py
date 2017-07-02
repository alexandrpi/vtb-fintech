"""Различные вспомогательные функциии"""
import json

token = '145372030:AAFX7Vsv4_CMr7EtaoRpcfTyIfEfBh37Occ'


def quote(s):
    return '\'{}\''.format(s)


def quote2(s):
    return '\"{}\"'.format(s)


def load_config():
    with open('config.json', 'r') as cfg_file:
        config = json.load(cfg_file)
    return config


def prepared(n):
    return ['$' + str(k) for k in range(1, n + 1)]