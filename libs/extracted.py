from extraction import Extracted
from extraction.techniques import Technique


class DoubanGameExtracted(Extracted):
    @property
    def image(self):
        if self.images:
            return self.images[1]

    @property
    def description(self):
        if self.descriptions:
            return self.descriptions[3]


class MetacriticExtracted(Extracted):
    @property
    def description(self):
        return None
