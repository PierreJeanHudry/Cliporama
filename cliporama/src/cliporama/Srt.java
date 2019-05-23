package cliporama;

import java.io.*;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.regex.Matcher;

import org.apache.commons.io.FileUtils;

import at.mukprojects.giphy4j.Giphy;
import at.mukprojects.giphy4j.entity.search.SearchFeed;
import at.mukprojects.giphy4j.exception.GiphyException;

/**
 * Classe définie par un fichier srt
 */
public class Srt {
	private String nomfichier;

	/**
	 * Contructeur
	 * @param fich Chemin du fichier srt
	 */
	public Srt(String fich) {
		this.nomfichier = fich;
	}

	/**
	 * Traduit le fichier SRT en une liste chainée de "Mot", via une série
	 * de transformations
	 *
	 * @return LinkedList<Mot>
	 */
	public LinkedList<Mot> traduction() {
		//On fait l'interface hors de la boucle pour créer une fenêtre dans tous les cas
		//si il y a un problème, on a une interface sans rien, juste avec fond
		LinkedList<Mot> paroles = new LinkedList<Mot>(); // liste chainée des mots du texte
		try (BufferedReader fichier = Files.newBufferedReader(Paths.get(this.nomfichier))) {

			/* --- initialisation --- */

			String line = ""; // chaine de caractères lue depuis le fichier srt
			double tps = 0; // temps d'apparition de la phrase en secondes
			double duree = 0; // durée de la phrase en secondes
			String phrase = ""; // chaine de caractères utlisée pour combiner les lignes d'une seule phrase du
								// fichier srt

			//Creation de la liste des mots à éliminer
			Set<String> set = listeMots();

			//Api key Giphy
			Giphy giphy = new Giphy("Fxe6Ib7RS60Vx30kVKbD5UpXlOarp3dR");

			/* --- Debut de la boucle sur la totalité du fichier SRT --- */
			while ((line = fichier.readLine()) != null) {

				Etat etatMatched = rechercheEtat(line);
				switch (etatMatched) {

				//La ligne corespond à un timecode
				case TimeCode:
					String[] times = line.split("[:,\\s+]"); // "\\s+" indique espace
					tps = tpsTransfo(times);
					duree = dureeTransfo(times);
					break;

				//La ligne correspond à du texte
				case Texte:
					if (line.isEmpty()) {
						String[] mots = nettoyage(phrase);
						duree = duree / mots.length; // tous les mots d'une phrase ont la meme duree

						for (String mot : mots) {
							if (mot.length() > 2) { // On ne considère que les mots de plus de deux lettres

								try {

									// Vérifie si le mot fait parti de l'enemble des mots à éliminer
									int n = 0; // et ajoute le mot à paroles ssi il n'est pas dans l'ensemble
									Iterator<String> iterator = set.iterator();
									while (iterator.hasNext()) {
										if (iterator.next().equals(mot)) {
											n++;
										}
									}
									//Ajoute le mot
									if (n == 0) {
										String chemin = "data/" + mot + ".gif";
										File gifMot = new File(chemin);
										if(!gifMot.exists()) {
											SearchFeed giphyData = giphy.search(mot, 1, 0);	//donne le mot à chercher, le nombre de gif à sélectionné et l'offset
											if (!giphyData.getDataList().isEmpty()) {

												if (telechargerGif(giphyData.getDataList().get(0).getId(), chemin)) {
													Mot m = new Mot(mot, tps, chemin);
													paroles.add(m);
												}

											} else {
												System.out.println("Mot ignoré car pas de gif associé " + mot);
											}
										}else {
											System.out.println("Le gif pour le mot " + mot+ " existe déjà");
											Mot m = new Mot(mot, tps, chemin);
											paroles.add(m);
										}

									} else {
										System.out.println("Mot ignoré " + mot);
									}

								} catch (GiphyException e) {
									e.printStackTrace();
								}

								tps = Math.floor(((tps + duree) * 100)) / 100; // troncature à deux décimales près
							}
						}
						phrase = "";
						tps = 0;
						duree = 0;
					} else {
						phrase += " " + line; // Comme une phrase peut etre mise sur plusieurs lignes du SRT, on ne
												// traite pas immédiatement
					}
					break;

				default:
					System.out.println("Erreur dans le fichier SRT");
					break;
				}
			}
			fichier.close();

		} catch (Exception e) {
			e.printStackTrace();
		}
		return paroles;
	}


	/**
	 * Telecharge un gif à partir de son id dans chemin, le booléen indique le succès de l'opération
	 * @param id		String
	 * @param chemin	String
	 * @return			boolean
	 */
	protected boolean telechargerGif(String id, String chemin)  {

		try {
			File outputFile = new File(chemin);
			String adresse = "https://i.giphy.com/"+id+".gif"; //Télécharge en .gif et non .html
			System.out.println("Téléchargement du gif "+adresse+" dans "+chemin);
			URL url = new URL(adresse);
			FileUtils.copyURLToFile(url, outputFile);
		}catch(IOException ex) {
			System.out.println(ex.getMessage());
			return false;
		}

		return true;

	}

	/**
	 * Uniformise les espaces du fichier SRT, supprime les
	 * apostrophes, tous les caractères non alphabétiques et non
	 * chiffres
	 * @param String
	 * @return String[]
	 */
	public String[] nettoyage(String p) {
		p = p.replaceAll(" ", " "); // tous les espaces des SRT du site repéré ne sont pas les memes
		p = p.toLowerCase();
		p = p.replaceAll("['′]", " "); // supprime les apostrophes (deux types)
		p = p.replaceAll("[^\\p{IsAlphabetic}^\\p{IsDigit} ]", ""); // supprime tous les caractères hors de l'alphabet
																	// et des chiffres et espace
		p = p.replaceAll("  ", " ");
		return p.split(" "); // retourne la liste de mots de la phrase
	}

	/**
	 * Permet la transformation des timecodes transformés du SRT en une durée (double) pour chaque phrase
	 *
	 * @param String[]
	 * @return double
	 */
	public double dureeTransfo(String[] times) {
		try {
			return ((Integer.parseInt(times[5]) - Integer.parseInt(times[0])) * 3600
					+ (Integer.parseInt(times[6]) - Integer.parseInt(times[1])) * 60 + Integer.parseInt(times[7])
					- Integer.parseInt(times[2]) + (Integer.parseInt(times[8]) - Integer.parseInt(times[3])) * 0.001);
		} catch (NumberFormatException e) {
			System.out.println("ERREUR BadTimeCode dureeTransfo");
			return -1;
		}
	}

	/**
	 * Permet la transformation d'une chaine de caractère TimeCode en un double
	 * donnant le temps associé en secondes
	 *
	 * @param String[]
	 * @return double
	 */
	public double tpsTransfo(String[] times) {
		try {
			return Integer.parseInt(times[0]) * 3600 + Integer.parseInt(times[1]) * 60 + Integer.parseInt(times[2])
			+ Integer.parseInt(times[3]) * 0.001;
		} catch (NumberFormatException e) {
			System.out.println("ERREUR BadTimeCode tpsTransfo");
			return -1;
		}
	}

	/**
	 * Construit à partir d'un .txt contenant des mots communs anglais dont on ne souhaite pas tenir compte un set contenant tous
	 * ces mots
	 * @return Set
	 * @throws IOException
	 */
	protected Set<String> listeMots() throws IOException {
		Set<String> set = new HashSet<String>(); // Creation l'ensemble indéxé
		InputStream fluxx = new FileInputStream("data/musiques/test.txt"); // et ajoute les mots à supprimer dans l'ensemble
		InputStreamReader lecc = new InputStreamReader(fluxx);
		BufferedReader buf = new BufferedReader(lecc);
		String linee;
		while ((linee = buf.readLine()) != null) {
			set.add(linee);
		}
		buf.close();
		return set;
	}

	/**
	 * Permet l'identification du pattern d'une ligne du fichier srt
	 * @param String
	 * @return Etat
	 */
	protected Etat rechercheEtat(String line) {
		Etat etatMatched = null;
		Matcher matcher = null;
		for (Etat etat : new Etat[] { Etat.Texte, Etat.TimeCode }) {
			matcher = etat.pattern.matcher(line);
			if (matcher.find()) {
				etatMatched = etat;
			}
		}
		return etatMatched;
	}
}
