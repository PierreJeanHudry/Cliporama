package cliporama;

import java.util.regex.Pattern;

/**
 * Classe permettant d'identifier le type d'une ligne lue dans le fichier srt
 */
public enum Etat {
	TimeCode("^..:..:..,... --> ..:..:..,...$"), Texte(".*");	//définiton des expression régulières, précédées par leur nom

	final Pattern pattern;

	/**
	 * Permet la compilation des expression régulières pour le switch dans "srt"
	 * @param regex expression régulière à compiler
	 */
	Etat(String regex){
		pattern = Pattern.compile(regex);
	}
}
