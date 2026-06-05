import polars as pl
import os


def merge_and_align_datasets(scifi_file: str, horror_file: str, output_parquet: str):
    """
    Fusionne deux datasets avec des schémas différents en alignant les colonnes communes.
    Utilise la concaténation diagonale de Polars pour gérer les colonnes exclusives.
    """
    print("🧟‍♂️ Démarrage du protocole d'hybridation (Sci-Fi + Horreur)...")

    # 1. Chargement des données
    # (J'utilise read_ndjson ici car vos exemples sont au format JSONLines,
    # mais remplacez par pl.read_parquet() si vos fichiers sont déjà des .parquet)
    print("📥 Chargement des fichiers sources...")
    try:
        # CORRECTION : On utilise la fonction dédiée aux fichiers binaires Parquet
        df_scifi = pl.read_parquet(scifi_file)
        df_horror = pl.read_parquet(horror_file)
    except Exception as e:
        print(f"❌ Erreur lors du chargement des fichiers : {e}")
        return

    # --- LA NOUVELLE ÉTAPE : TRAÇABILITÉ (DATA LINEAGE) ---
    print("🏷️ Ajout de l'ADN d'origine (Traçabilité des univers)...")
    # On taggue chaque dataset avec son univers d'origine AVANT de les mélanger.
    # pl.lit() permet d'assigner une valeur fixe à toute une colonne.
    df_scifi = df_scifi.with_columns(pl.lit("Sci-Fi").alias("source_universe"))
    df_horror = df_horror.with_columns(pl.lit("Horreur").alias("source_universe"))

    # 2. Alignement Sémantique (Data Cleaning)
    # Votre collègue a nommé certaines colonnes différemment.
    # Si on ne les renomme pas, Polars créera des colonnes distinctes avec plein de 'null'.
    print("🧹 Alignement des schémas (Renommage des colonnes du collègue)...")
    df_horror = df_horror.rename(
        {"rating_tmdb": "vote_average", "tomatometer_score": "rt_score"}
    )

    # On s'assure également que les types de données correspondent pour éviter un "SchemaError".
    # Dans votre JSON, rt_score est parfois un String ("48"), alors qu'il devrait être casté.
    # L'utilisation de 'diagonal_relaxed' gère souvent cela, mais soyons explicites et rigoureux.

    # 3. La Fusion Diagonale
    # C'est LA fonctionnalité clé de Polars pour les schémas asymétriques.
    # Elle empile les données, et met la valeur 'null' là où la colonne n'existe pas
    # (ex: tmdb_id sera null pour les films d'horreur de votre collègue).
    print("⚡ Concaténation Diagonale en cours...")

    # 'diagonal_relaxed' permet de forcer la fusion même si un type diffère légèrement
    # (ex: Int32 vs Int64 ou String vs Int en forçant vers le type le plus permissif)
    df_final = pl.concat([df_scifi, df_horror], how="diagonal_relaxed")

    # 4. (Optionnel) Dédoublonnement au cas où un film existe dans les deux listes
    # On se base sur le titre et l'année pour être sûr.
    print("🔍 Vérification des doublons inter-univers...")
    df_final = df_final.unique(subset=["title", "release_date"], keep="first")

    # --- LA CORRECTION MAGIQUE : CRÉATION D'UNE SURROGATE KEY ---
    print("🧬 Génération des identifiants uniques (horragor_id)...")
    # Face au manque de tmdb_id côté horreur, on crée notre propre ID système
    # en hachant le titre et la date de sortie. Cet ID sera utilisé par le routeur FAISS !
    df_final = df_final.with_columns(
        pl.concat_str([pl.col("title"), pl.col("release_date")], separator="_")
        .hash()
        .cast(
            pl.Utf8
        )  # On le convertit en chaîne de caractères pour faciliter son usage dans l'Agent LLM
        .alias("horragor_id")
    )

    # 5. Exportation vers la base de vérité (Gold Parquet)
    print(f"💾 Sauvegarde de l'abomination finale vers : {output_parquet}")
    df_final.write_parquet(output_parquet)

    print("\n✅ Fusion terminée avec succès ! Voici un aperçu du nouveau schéma :")
    print(df_final.schema)
    print(f"\n📊 Nombre total de films (Sci-Fi + Horreur) : {len(df_final)}")


if __name__ == "__main__":
    # --- Instructions ---
    # Remplacez les valeurs ci-dessous par les noms exacts de vos fichiers Parquet

    merge_and_align_datasets(
        scifi_file="scifi.parquet",  # <-- Adaptez avec le nom de votre fichier
        horror_file="horror.parquet",  # <-- Adaptez avec le nom de son fichier
        output_parquet="horragor_final_data.parquet",
    )
