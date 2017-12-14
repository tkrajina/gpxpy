try:
    import lxml.etree as mod_etree  # Load LXML or fallback to cET or ET
except ImportError:
    try:
        import xml.etree.cElementTree as mod_etree
    except ImportError:
        import xml.etree.ElementTree as mod_etree



class GarminTrackPtExt(mod_etree.Element):
    EXT_NAMESPACE = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
    def __init__(self):
        pass

    @property
    def atemp(self):
        pass

    @atemp.setter
    def atemp(self, temp):
        pass

    @atemp.deleter
    def atemp(self):
        pass

    @property
    def wtemp(self):
        pass

    @wtemp.setter
    def wtemp(self, temp):
        pass

    @wtemp.deleter
    def wtemp(self):
        pass

    @property
    def hr(self):
        pass

    @hr.setter
    def hr(self, hr):
        pass

    @hr.deleter
    def hr(self):
        pass

    @property
    def depth(self):
        pass

    @depth.setter
    def depth(self, depth):
        pass

    @depth.deleter
    def depth(self):
        pass

    @property
    def cad(self):
        pass

    @cad.setter
    def cad(self, cadence):
        pass

    @cad.deleter
    def cad(self):
        pass
