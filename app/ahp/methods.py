# Methods for AHP calculations
import numpy as np

def matrix_multiply(matrix1, matrix2):
    """
        result = matrix_multiply(A, B)
        for row in result:
         print(row)
    """
    # Check if the matrices can be multiplied
    if len(matrix1[0]) != len(matrix2):
        raise ValueError("The number of columns in matrix1 must be equal to the number of rows in matrix2")

    # Initialize a result matrix with zeros
    result = [[0] * len(matrix2[0]) for _ in range(len(matrix1))]

    # Perform matrix multiplication
    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            for k in range(len(matrix2)):
                result[i][j] += matrix1[i][k] * matrix2[k][j]

    return result


# Relative Comparison Matrix definition for a KPI
def rcm_def(alt_values:list, kpi_hb):
    """
    kpi types:
        0: numeric, higher is better
        1: numeric, lower is better
        2,3 To be defined
    """

    rcm = []  # Array, initialize rcm
    if kpi_hb:
        length = len(alt_values)
        for i in range(length):
            temp_row = []  # each row of rcm as a list
            for j in range(length):
                temp_row.append(alt_values[i] / alt_values[j])
            rcm.append(temp_row)
    else:
        length = len(alt_values)
        for i in range(length):
            temp_row = []  # each row of rcm as a list
            for j in range(length):
                temp_row.append(alt_values[j] / alt_values[i])
            rcm.append(temp_row)

    return rcm

# Calculate numeric Relative Ranking Vectors for KPIs --> quick AHP
def qahp_rrv_kpi_calc(alt_values:list, kpi_hb):
    #
    q_rrv = []
    print(kpi_hb)
    if kpi_hb==1:
        b_ratio = 1 / sum(alt_values)
        for v in alt_values:
            q_rrv.append(v*b_ratio)
    if kpi_hb==0:
        b_ratio = 1 / sum(1/v for v in alt_values)
        for v in alt_values:
            q_rrv.append((1/v)*b_ratio)
    return q_rrv

# Calculate numeric Relative Ranking Vectors for Attributes
def attr_rrv(attributes, kpis):
    """
    """
    # Sort descending so lower-level attributes are calculated first.
    attributes = sorted(attributes, key=lambda x: x.id, reverse=True)
    
    for attr in attributes:

        # find siblings
        siblings = []
        for k in kpis:
            if attr.id == k.pid:
                siblings.append(k)
        for k in attributes:
            if attr.id == k.pid:
                siblings.append(k)

        # Define the rcm for attribute
        rcm = []
        w_vector = []
        for s in siblings:
            w_vector.append(s.weight)
            rcm.append(s.rrv)
        
        # Prepare vectors and calculate rrv
        rcm = np.array(rcm).transpose()
        w_vector = np.array(w_vector)
        attr.rrv = rcm.dot(w_vector).tolist()

    return attributes