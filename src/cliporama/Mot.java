package cliporama;

/**
 * Classe définissant un objet composé d'un mot, d'un temps et d'un chemin
 */
public class Mot {

	private String mot;
	private double temps;
	private String imagePath;	//contient le chemin dans lequel on va placer le Gif  téléchargé

	public Mot(String mot, double tps, String imagePath) {
		this.mot=mot;
		this.temps=tps;
		this.imagePath = imagePath;
	}

	public String getMot() {
		return mot;
	}

	public double getTemps(){
		return temps;
	}

	public String getImagePath() {
		return imagePath;
	}

	public void setImagePath(String imagePath) { //pas utilisé
		this.imagePath = imagePath;
	}



}
