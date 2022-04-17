from extraction import Extracted


class DoubanGameExtracted(Extracted):
    @property
    def image(self):
        if self.images:
            return self.images[1]
        return None
