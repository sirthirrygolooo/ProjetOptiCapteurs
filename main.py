import sys
import random
from verif import verifier_configurations
from solv import resoudre_ordonnancement, afficher_solution
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor

import random

def generer_configurations_tabou(n_capteurs: int, zones_par_capteur: list[list[int]], iterations: int = 400, tenure: int = 15) -> list[tuple[int]]:
    cibles_uniques = {z for zones in zones_par_capteur for z in zones}
    n_cibles = len(cibles_uniques)
    
    # alpha = punition. Très élevé pour forcer la couverture complète, mais pas trop pour ne pas négliger la taille de la solution.
    alpha = n_capteurs + 1
    
    zone_to_idx = {z: i for i, z in enumerate(cibles_uniques)}
    zones_idx = [[zone_to_idx[z] for z in zones] for zones in zones_par_capteur]
    
    solutions = set()
    visited_full = set() 
    
    acteurs = set()
    zone_counts = [0] * n_cibles
    current_coverage = 0
    
    for i in range(n_capteurs):
        if random.random() < 0.3:
            acteurs.add(i)
            for z in zones_idx[i]:
                if zone_counts[z] == 0:
                    current_coverage += 1
                zone_counts[z] += 1

    tabu_list = [-1] * n_capteurs

    for iter_idx in range(iterations):
        meilleur_delta = float('inf')
        meilleur_capteur = -1
        meilleur_action = 0
        
        for capteur in range(n_capteurs):
            if tabu_list[capteur] > iter_idx:
                continue

            z_capteur = zones_idx[capteur]
            
            if capteur in acteurs:
                zones_perdues = sum(zone_counts[z] == 1 for z in z_capteur)
                delta = -1 + alpha * zones_perdues
                action = 1
            else:
                zones_gagnees = sum(zone_counts[z] == 0 for z in z_capteur)
                delta = 1 - alpha * zones_gagnees
                action = 0

            if delta < meilleur_delta:
                meilleur_delta = delta
                meilleur_capteur = capteur
                meilleur_action = action

        if meilleur_capteur == -1:
            break

        z_meilleur = zones_idx[meilleur_capteur]
        if meilleur_action == 1:
            acteurs.remove(meilleur_capteur)
            for z in z_meilleur:
                if zone_counts[z] == 1:
                    current_coverage -= 1
                zone_counts[z] -= 1
        else:
            acteurs.add(meilleur_capteur)
            for z in z_meilleur:
                if zone_counts[z] == 0:
                    current_coverage += 1
                zone_counts[z] += 1

        tabu_list[meilleur_capteur] = iter_idx + tenure

        if current_coverage == n_cibles:
            frozen = frozenset(acteurs)
            if frozen not in visited_full:
                visited_full.add(frozen)
                
                comptes_locaux = list(zone_counts)
                combi_pure = set(acteurs)
                
                for c in list(combi_pure):
                    if not any(comptes_locaux[z] <= 1 for z in zones_idx[c]):
                        combi_pure.remove(c)
                        for z in zones_idx[c]:
                            comptes_locaux[z] -= 1
                            
                solutions.add(tuple(sorted(c + 1 for c in combi_pure)))

    return list(solutions)


def collecter_grand_pool(n_capteurs: int, zones_par_capteur: list[list[int]], n_restarts: int = 10) -> list[tuple[int]]:
    pool_global = set()
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(generer_configurations_tabou, n_capteurs, zones_par_capteur, 300) for _ in range(n_restarts)]
        for f in futures:
            pool_global.update(f.result())
    return list(pool_global)


def solveur(n_capteurs: int, n_zones: int, zones_par_capteur: list[list[int]], duree_de_vie_capteurs: list[int]) -> None:
    # trouver les combinaisons de capteurs qui couvrent toutes les zones
    # donc au moins un capteur doit couvrir chaque zone
    t1 = perf_counter()
    combinaisons = collecter_grand_pool(n_capteurs, zones_par_capteur, 50)
    duree_totale, resultats_configurations = resoudre_ordonnancement(n_capteurs, duree_de_vie_capteurs, combinaisons)
    print(f"\nTemps d'exécution : {perf_counter() - t1:.2f} secondes.")
    afficher_solution(duree_totale, resultats_configurations)
    # verifier_configurations(zones_par_capteur, combinaisons)



def main() -> int:
    # fichier d'input
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        return 1
    input_file = sys.argv[1]
    
    with open(input_file, 'r') as f:
        data = f.read().strip().splitlines()
        # nombre de capteurs
        n_capteurs = int(data[0])
        # nombre de zones
        n_zones = int(data[1])
        # zones surveillées par le capteur n
        zones_par_capteur = []
        # durée de vie des capteurs
        duree_de_vie_capteurs = list(map(int, data[2].split()))
        for i in range(3,3 + n_capteurs):
            zones = list(map(int, data[i].split()))
            zones_par_capteur.append(zones)

        solveur(n_capteurs, n_zones, zones_par_capteur, duree_de_vie_capteurs)
    return 0

if __name__ == "__main__":
    exit(main())
