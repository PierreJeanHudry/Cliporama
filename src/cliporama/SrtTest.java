package cliporama;

import static org.junit.Assert.*;
import java.io.IOException;
import org.junit.Test;

/**
 * Classe de test JUnit concernant la classe Srt
 */
public class SrtTest {

	Srt srt = new Srt("test");

	/**
	 * Permet le test sur la méthode traduction de la classe Srt
	 */
	@Test
	public void testTraduction() {
		Srt srt1=new Srt("data/musiques/Test.srt");				//Par contruction, on ne peut pas lui donner un fichier inexistant
		assertFalse("Fichier Srt conforme",(srt1.traduction()).isEmpty());
		}

	/**
	 * Permet le test sur la méthode nettoyage de la classe Srt
	 */
	@Test
	public void testNettoyage() {
		String phrase = "If the bands make ′em dance‚ then the rain gon′ come";
		assertTrue("Entrée conforme", (srt.nettoyage(phrase)).length>10); 	//s'il y a au moins 11 mots dans phrase
		assertFalse("Entrée vide",(srt.nettoyage("")).equals(null));		//s'il n'y a aucun mot, que cela ne retourne pas "null"
		phrase = "uF5SawFq4O nZMgJnO EJWLh";
		assertTrue("Entrée aléatoire", (srt.nettoyage(phrase)).length>2);	//Si c'est pas des mots
	}

	/**
	 * Permet le test sur la méthode dureeTransfo de la classe Srt
	 */
	@Test
	public void testDureeTransfo() {	//l'application ne peut pas être appelée autrement que pour une entrée correspondant à ce format
		String[] timecode = ("01:01:01,001 --> 02:02:02,002").split("[:,\\s+]");
		assertTrue("Entrée conforme",srt.dureeTransfo(timecode)==3661.001);
		timecode=("01:0a:01,001 --> 02:02:02,002").split("[:,\\s+]");		//s'il y a une lettre au lieu d'un chiffre
		assertTrue("Entrée non conforme",srt.dureeTransfo(timecode)==-1);
	}

	/**
	 * Permet le test sur la méthode tpsTransfo de la classe Srt
	 */
	@Test
	public void testTpsTransfo() {
		String[] timecode = ("01:01:01,001 --> 02:02:02,002").split("[:,\\s+]");
		assertTrue("Entrée conforme",srt.tpsTransfo(timecode)==3661.001);
		timecode=("01:0a:01,001 --> 02:02:02,002").split("[:,\\s+]");		//s'il y a une lettre au lieu d'un chiffre
		assertTrue("Entrée non conforme",srt.dureeTransfo(timecode)==-1);
	}

	/**
	 * Permet le test sur la méthode listeMots de la classe Srt
	 * @throws IOException
	 */
	@Test
	public void testListeMots() throws IOException { //(String id, String chemin)
		assertFalse("Liste de mots non vide",(srt.listeMots()).isEmpty());
	}

	/**
	 * Permet le test sur la méthode rechercheEtat de la classe Srt
	 */
	@Test
	public void testRechercheEtat() { //(String id, String chemin)
		String line = "azerty";
		assertTrue("Etat Texte",srt.rechercheEtat(line)==Etat.Texte);
		line="01:01:01,001 --> 02:02:02,002";
		assertTrue("Etat TimeCode",srt.rechercheEtat(line)==Etat.TimeCode);
	}

}
