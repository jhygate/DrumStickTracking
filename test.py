import numpy as np

a = np.array([[360, 214], [355, 187], [349, 160], [343, 130], [336, 96], [328, 59], [314, 3]])
b = np.array([[363, 200], [357, 177], [351, 152], [345, 125], [338, 93], [329, 57], [318, 4]])

from scipy.spatial import distance_matrix
print(distance_matrix(a,b))