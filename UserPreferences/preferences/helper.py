from abc import ABCMeta

from discord.ext.commands import CogMeta


class CogABCMeta(ABCMeta, CogMeta):
    """A metaclass that implements ABCMeta and CogMeta"""
