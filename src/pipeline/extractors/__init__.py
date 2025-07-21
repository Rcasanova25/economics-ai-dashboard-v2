# Specific extractors for different PDF sources
# Each extractor knows the unique structure of its source's reports

from .stanford_hai import StanfordHAIExtractor
from .oecd import OECDExtractor
from .mckinsey import McKinseyExtractor
from .goldman_sachs import GoldmanSachsExtractor
from .academic import AcademicPaperExtractor
from .universal import UniversalExtractor

# Mapping of PDF patterns to extractors
EXTRACTOR_MAPPING = {
    'hai_ai_index': StanfordHAIExtractor,
    'stanford': StanfordHAIExtractor,
    'oecd': OECDExtractor,
    'mckinsey': McKinseyExtractor,
    'state-of-ai': McKinseyExtractor,  # McKinsey report
    'goldman': GoldmanSachsExtractor,
    'gs-': GoldmanSachsExtractor,  # Goldman Sachs reports often start with gs-
    'goldman_sachs': GoldmanSachsExtractor,
    'acemoglu': AcademicPaperExtractor,
    'productivity': AcademicPaperExtractor,
    'economic_impacts_paper': AcademicPaperExtractor,
    'artificial intelligence, scientific': AcademicPaperExtractor,
    # Add more mappings as needed
}

# Default extractor for unmatched PDFs
DEFAULT_EXTRACTOR = UniversalExtractor

__all__ = [
    'StanfordHAIExtractor',
    'OECDExtractor', 
    'McKinseyExtractor',
    'GoldmanSachsExtractor',
    'AcademicPaperExtractor',
    'UniversalExtractor',
    'EXTRACTOR_MAPPING',
    'DEFAULT_EXTRACTOR'
]