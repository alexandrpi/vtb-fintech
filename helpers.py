<<<<<<< HEAD
token = '445186548:AAGPAHB7eDP7eXoEe3Zoxqc1uFvTsRahDbU'
=======
"""Различные вспомогательные функциии"""
import pickle

token = '145372030:AAFX7Vsv4_CMr7EtaoRpcfTyIfEfBh37Occ'


def quote(s):
    return '\'{}\''.format(s)


def quote2(s):
    return '\"{}\"'.format(s)


def load_config():
    with open('aws-rds-params.pickle', 'rb') as cfg_file:
        config = pickle.load(cfg_file)
    return config


def prepared(n):
    return ['$' + str(k) for k in range(1, n + 1)]
>>>>>>> 0790ae2... Столько всего, что я не в состоянии описать, что сделал. Пора спать, время 2 часа ночи, так больше нельзя.
