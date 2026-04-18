from .mostaql    import MostaqlScraper
from .tafdhali   import TafdhaliScraper
from .kofeel     import KofeelScraper
from .pph        import PPHScraper
from .freelancer import FreelancerScraper

ALL_SCRAPERS = [
    MostaqlScraper(),
    TafdhaliScraper(),
    KofeelScraper(),
    PPHScraper(),
    FreelancerScraper(),
]
