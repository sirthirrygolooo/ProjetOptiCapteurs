import sys


def solveur(n_capteurs: int, n_zones: int, zones_par_capteur: list[list[int]], duree_de_vie_capteurs: list[int]) -> None:
    return


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
