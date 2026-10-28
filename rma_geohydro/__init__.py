# -*- coding: utf-8 -*-
def classFactory(iface):
    from .plugin import RMAGeoHydroPlugin
    return RMAGeoHydroPlugin(iface)
