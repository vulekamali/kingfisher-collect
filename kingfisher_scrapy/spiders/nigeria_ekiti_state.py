from kingfisher_scrapy.spiders.european_dynamics_saas_base import EuropeanDynamicsSassBase


class NigeriaEkitiState(EuropeanDynamicsSassBase):
    """
    Domain
      Nigeria Ekiti State Open Contracting Portal
    """
    name = 'nigeria_ekiti_state'

    # EuropeanDynamicsSassBase
    base_url = 'https://ocds.bpp.ekitistate.gov.ng/'

