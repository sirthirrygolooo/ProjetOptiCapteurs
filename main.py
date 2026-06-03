import sys
import random


def combinaison_elementaire(n_capteurs: int, zones_par_capteur: list[list[int]]) -> tuple[int]:
    cibles = {z for zones in zones_par_capteur for z in zones}
    
    # ==========================================
    # Algorithme Glouton Aléatoire
    # ==========================================
    zones_non_couvertes = set(cibles)
    config_valide = []
    capteurs_dispos = list(range(n_capteurs))
    
    while zones_non_couvertes:
        apports = []
        for c in capteurs_dispos:
            couverture = set(zones_par_capteur[c]) & zones_non_couvertes
            apports.append((len(couverture), c))
        
        max_couverture = max(apport[0] for apport in apports)
        
        if max_couverture == 0:
            break
            
        meilleurs_candidats = [c for apport, c in apports if apport == max_couverture]
        
        choix = random.choice(meilleurs_candidats)
        
        config_valide.append(choix)
        capteurs_dispos.remove(choix)
        zones_non_couvertes -= set(zones_par_capteur[choix])

    # ==========================================
    # La Purge
    # ==========================================
    config_elementaire = config_valide.copy()
    
    for capteur in reversed(config_valide):
        config_test = [c for c in config_elementaire if c != capteur]
        zones_couvertes_test = {z for c in config_test for z in zones_par_capteur[c]}
        
        if cibles.issubset(zones_couvertes_test):
            config_elementaire.remove(capteur)
            
    return tuple(sorted([c + 1 for c in config_elementaire]))


def creer_liste_combinaisons(k_iterations: int, n_capteurs: int, zones_par_capteur: list[list[int]]) -> list[tuple[int]]:
    liste_combi = set()
    for _ in range(k_iterations):
        config = combinaison_elementaire(n_capteurs, zones_par_capteur)
        if config:
            liste_combi.add(config)
    return list(liste_combi)


def solveur(n_capteurs: int, n_zones: int, zones_par_capteur: list[list[int]], duree_de_vie_capteurs: list[int]) -> None:
    # trouver les combinaisons de capteurs qui couvrent toutes les zones
    # donc au moins un capteur doit couvrir chaque zone
    combinaisons = creer_liste_combinaisons(100, n_capteurs, zones_par_capteur)
    print(f"Combinaisons élémentaires: {combinaisons}")


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
        
        
        print(f"Nombre de capteurs: {n_capteurs}")
        print(f"Nombre de zones: {n_zones}")
        print("Zones surveillées par chaque capteur:")
        for i, zones in enumerate(zones_par_capteur):
            print(f"Capteur {i+1}: {zones}")
        print(f"Durée de vie des capteurs: {duree_de_vie_capteurs}")

        solveur(n_capteurs, n_zones, zones_par_capteur, duree_de_vie_capteurs)
    return 0

if __name__ == "__main__":
    exit(main())
