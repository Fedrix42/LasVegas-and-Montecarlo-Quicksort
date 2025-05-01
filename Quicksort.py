import random
import matplotlib.pyplot as plt
import math
import multiprocessing
import os

def swap(array, i, j):
    array[j], array[i] = array[i], array[j]

def partition(array, begin, end):
    counter = 0
    pivot_idx = random.randrange(begin, end)
    swap(array, pivot_idx, end)
    pivot_idx = end
    i = begin
    for j in range(begin, end):
        counter += 1
        if array[j] <= array[pivot_idx]:
            swap(array, i, j)
            i = i + 1
    swap(array, i, end)
    return i, counter

def LVQuicksort(array, begin , end): 
    if(begin < end):
        pivot_idx, comparisons = partition(array, begin, end)
        comparisons += LVQuicksort(array , begin , pivot_idx - 1) 
        comparisons += LVQuicksort(array, pivot_idx + 1, end) 
        return comparisons
    else: return 0

mc_num_comparisons = 0
def LVQuicksort_InternalStop(array, begin, end, max_comparisons):
    global mc_num_comparisons
    if(begin < end):
        pivot_idx, tmp_cmp = partition(array, begin, end)
        mc_num_comparisons += tmp_cmp
        if(mc_num_comparisons > max_comparisons): 
            return
        LVQuicksort_InternalStop(array , begin , pivot_idx - 1, max_comparisons) 
        LVQuicksort_InternalStop(array, pivot_idx + 1, end, max_comparisons)

def MCQuicksort(array, k): 
    global mc_num_comparisons
    n = len(array)
    expected = 2*(n * math.log(n, 2))
    mc_num_comparisons = 0
    for r in range(k):
        LVQuicksort_InternalStop(array, 0, n - 1, expected)
        print(f"LasVegas_InternalStop esecuzione {r+1}/{k} con {mc_num_comparisons} confronti")
        mc_num_comparisons = 0

def is_sorted(array):
    for i in range(0, len(array) - 1):
        if array[i] > array[i+1]: return False
    return True

def get_rand_array(size, inf, sup):
    arr = []
    for _ in range(size):
        arr.append(random.randrange(inf, sup))
    return arr

def read_data():
    output = []
    files = os.listdir("results")
    print("Lettura dei file: ", files)
    if not files: # Lista è vuota 
        raise FileNotFoundError
    for file in files:
        with open(str("results/" + file), "r") as f:
            data = f.readline().split(",")
        for x in data:
            output.append(int(x))
    return output    

def write_data(path, array):
    f = open(path, "w")
    f.write(','.join(str(x) for x in array))
    f.close()

def run_sim(runs, array_size):
    """ 
    Executes RUNS times LasVegas Quicksort with random array of length ARRAY_SIZE
    Then write array containing the number of comparisons into file
    """
    cmp_array = []
    for i in range(runs):
        array = get_rand_array(array_size, -10**7, 10**7 + 1)
        lv_num_comparisons = LVQuicksort(array, 0, len(array) - 1)
        print(f"T({os.getpid()}) - Las Vegas esecuzione {i+1}/{runs} con {lv_num_comparisons} confronti")
        cmp_array.append(lv_num_comparisons)
        lv_num_comparisons = 0
    write_data(f"results/_{os.getpid()}_.txt", cmp_array)


def run_processes(nprocesses, runs, array_size):
    """
    Executes NPROCESSES processes calling run_sim function to speed up the RUNS executions of LasVegas Quicksort
    """
    processes = [] # Contenente i processes creati
    cmp_array_idx = [] # Array contenente i riferimenti agli array con il num di confronti
    for t in range(nprocesses):
        cmp_array = [] # Per memorizzare risultati intermedi
        processes.append(multiprocessing.Process(target=run_sim, args=[int(runs / nprocesses), array_size]))
        cmp_array_idx.append(cmp_array) # Aggiunta del riferimento

    print(f"Esecuzione di {nprocesses} processi...")
    for process in processes:
        process.start()

    for process in processes:
        process.join()
    


def main():
    """
    Exercise to implement LasVegas and Montecarlo Quicksort
    """
    runs = 10**5
    n = 10**4
    nprocesses = 8
    expected = (n * math.log(n, 2))
    print(f"Media empirica attesa: {expected}")
    print(f"2 * Media empirica attesa: {(2*expected)}")
    lv_comparisons_array = []
    
    # File con risultati
    try:
        lv_comparisons_array = read_data()
        print("Dati letti da file")
    except FileNotFoundError:
        # Esecuzione degli ordinamenti
        print(f"#### Esecuzione di {runs} run tramite {nprocesses} processi ####")
        run_processes(nprocesses, runs, n)
        lv_comparisons_array = read_data()

    
    # Calcolo del numero di confronti medio
    real = 0
    for num_cmp in lv_comparisons_array:
        real += num_cmp
    real /= runs

    print(f"Media empirica reale: {real}")

    plt.hist(lv_comparisons_array, 10)
    plt.xlabel("Confronti")
    plt.ylabel("Frequenza")
    plt.title(f"LVQuicksort {runs} Esecuzioni")
    

    # Montecarlo Quicksort
    k = 3
    a = get_rand_array(n, -10**7, 10**7 + 1)
    MCQuicksort(a, k)
    print(f"MCQuicksort ha ordinato l'array? {is_sorted(a)}")
    print(f"Ordinato con probabilità {(1 - 10**(-5*k))}") # 1 - e^k
    plt.show()

#With "None" parameter the seed is set according to the current system time
if __name__ == "__main__":
    random.seed(None)
    main()