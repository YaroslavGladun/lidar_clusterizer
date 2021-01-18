import enum


class ClusteringMethod(enum.Enum):
    NONE = 0
    K_MEANS = 1
    DBSCAN = 2
    OPTICS = 3
    GAUSSIAN_MIXTURE = 4


class MenuState:

    def __init__(self):
        self.clustering_method = ClusteringMethod.NONE

    def set_clustering_method(self, clustering_method: ClusteringMethod):
        self.clustering_method = clustering_method
