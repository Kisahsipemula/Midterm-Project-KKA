import heapq
from collections import deque
import time
import tracemalloc

# --- KONFIGURASI MASALAH ---
CAP_A = 11    # Kapasitas Ember A (Liter)
CAP_B = 7     # Kapasitas Ember B (Liter)
TARGET = 5   # Target air yang dicari (Liter)

# Bobot Biaya (Cost) untuk operator
COST_ISI = 3
COST_PINDAH = 1

def get_successors(state):
    """
    Menghasilkan state berikutnya berdasarkan 8 Operator Resmi:
    state = (x, y) -> x = air di ember A, y = air di ember B
    """
    x, y = state
    successors = []
    
    # 1. Isi penuh ember A
    if x < CAP_A:
        successors.append(((CAP_A, y), "1. Isi penuh ember A", COST_ISI))
        
    # 2. Isi penuh ember B
    if y < CAP_B:
        successors.append(((x, CAP_B), "2. Isi penuh ember B", COST_ISI))
        
    # 3. Kosongkan ember A
    if x > 0:
        successors.append(((0, y), "3. Kosongkan ember A", COST_PINDAH))
        
    # 4. Kosongkan ember B
    if y > 0:
        successors.append(((x, 0), "4. Kosongkan ember B", COST_PINDAH))
        
    # 5. Pindahkan air dari A ke B sampai A kosong (A dituang semua ke B)
    if x > 0 and (x + y <= CAP_B):
        successors.append(((0, x + y), "5. Pindahkan air dari A ke B sampai A kosong", COST_PINDAH))
        
    # 6. Pindahkan air dari B ke A sampai B kosong (B dituang semua ke A)
    if y > 0 and (x + y <= CAP_A):
        successors.append(((x + y, 0), "6. Pindahkan air dari B ke A sampai B kosong", COST_PINDAH))
        
    # 7. Pindahkan air dari A ke B sampai B penuh
    if x > 0 and y < CAP_B and (x + y >= CAP_B):
        t = CAP_B - y
        successors.append(((x - t, CAP_B), "7. Pindahkan air dari A ke B sampai B penuh", COST_PINDAH))
        
    # 8. Pindahkan air dari B ke A sampai A penuh
    if y > 0 and x < CAP_A and (x + y >= CAP_A):
        t = CAP_A - x
        successors.append(((CAP_A, y - t), "8. Pindahkan air dari B ke A sampai A penuh", COST_PINDAH))
        
    return successors


# --- 1. BREADTH-FIRST SEARCH (BFS) ---
def bfs_water_jug():
    start = (0, 0)
    queue = deque([(start, [start], [], 0)])
    visited = {start}
    nodes_expanded = 0
    
    while queue:
        state, path_states, path_actions, total_cost = queue.popleft()
        nodes_expanded += 1
        
        if state[0] == TARGET or state[1] == TARGET:
            return path_states, path_actions, total_cost, nodes_expanded
            
        for next_state, action, step_cost in get_successors(state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path_states + [next_state], path_actions + [action], total_cost + step_cost))
                
    return None, None, 0, nodes_expanded


# --- 2. DEPTH-FIRST SEARCH (DFS) ---
def dfs_water_jug():
    start = (0, 0)
    stack = [(start, [start], [], 0)]
    visited = set()
    nodes_expanded = 0
    
    while stack:
        state, path_states, path_actions, total_cost = stack.pop()
        
        if state[0] == TARGET or state[1] == TARGET:
            return path_states, path_actions, total_cost, nodes_expanded
            
        if state not in visited:
            visited.add(state)
            nodes_expanded += 1
            
            for next_state, action, step_cost in get_successors(state):
                if next_state not in visited:
                    stack.append((next_state, path_states + [next_state], path_actions + [action], total_cost + step_cost))
                    
    return None, None, 0, nodes_expanded


# --- 3. UNIFORM COST SEARCH (UCS) ---
def ucs_water_jug():
    start = (0, 0)
    pq = [(0, start, [start], [])]
    explored = set()
    nodes_expanded = 0
    
    while pq:
        cost, state, path_states, path_actions = heapq.heappop(pq)
        
        if state in explored:
            continue
            
        explored.add(state)
        nodes_expanded += 1
        
        if state[0] == TARGET or state[1] == TARGET:
            return path_states, path_actions, cost, nodes_expanded
            
        for next_state, action, step_cost in get_successors(state):
            if next_state not in explored:
                new_cost = cost + step_cost
                heapq.heappush(pq, (new_cost, next_state, path_states + [next_state], path_actions + [action]))
                
    return None, None, float('inf'), nodes_expanded


# --- FUNGSI UTAMA UNTUK MENJALANKAN & MENGUKUR PERFORMA ---
def benchmark_algorithm(name, algo_func):
    tracemalloc.start()
    start_time = time.perf_counter()
    
    path_states, path_actions, total_cost, nodes_expanded = algo_func()
    
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Waktu dalam satuan detik (s)
    exec_time_sec = end_time - start_time
    # Memori dalam satuan Megabyte (MB)
    peak_mem_mb = peak_mem / (1024 * 1024)
    
    print(f"[{name}]")
    print(f"  - Total Biaya (Cost)  : {total_cost} poin")
    print(f"  - Jumlah Langkah      : {len(path_actions) if path_actions else 0} langkah")
    print(f"  - Node Diekspansi     : {nodes_expanded} node")
    print(f"  - Waktu Eksekusi      : {exec_time_sec:.6f} s")
    print(f"  - Penggunaan Memori   : {peak_mem_mb:.6f} MB")
    
    if path_states:
        path_str = " -> ".join([str(s) for s in path_states])
        print(f"  - Urutan Path (State) : {path_str}")
        print(f"  - Detail Jalur Aksi   :")
        for i, action in enumerate(path_actions):
            print(f"     Langkah {i+1}: {path_states[i]} --({action})--> {path_states[i+1]}")
    else:
        print(f"  - Urutan Path (State) : Tidak ada jalur ditemukan")
        
    print("-" * 80)


if __name__ == "__main__":
    print("=" * 80)
    print(f" BENCHMARK PENGUJIAN 8 OPERATOR: WATER JUG PUZZLE (Target: {TARGET} Liter)")
    print("=" * 80)
    
    benchmark_algorithm("Breadth-First Search (BFS)", bfs_water_jug)
    benchmark_algorithm("Depth-First Search (DFS)", dfs_water_jug)
    benchmark_algorithm("Uniform Cost Search (UCS)", ucs_water_jug)