package cliporama;

import javafx.scene.image.Image;
import javafx.scene.image.ImageView;

/**
 * Classe définissant un objet composé d'un mot, d'une image, d'une position et d'un temps
 */
@SuppressWarnings("restriction")
public class Imagif {
	private String mot;
	private Image image;
	private double x;
	private double y;
	private double time;
	private ImageView imageView;

	public Imagif(String mot, Image im, double x, double y, double time) {
		this.mot = mot;			//Permet d'afficher le mot en sous-titre
		image = im;
		this.x = x;
		this.y = y;
		this.time = time;
	}

	public String toString() {
		return "Sprite<" + x + ", " + y + "> " + time;
	}

	public double getTime() {
		return time;
	}

	public Image getImage() {
		return image;
	}

	/**
	 * Parametrage de l'imageView
	 * @return ImageView
	 */
	public ImageView getImageView() {
		if (imageView == null) {
			imageView = new ImageView(this.image);
			imageView.setX(this.x);
			imageView.setY(this.y);
		}
		return imageView;

	}

	public String getMot() {
		return mot;
	}
}
