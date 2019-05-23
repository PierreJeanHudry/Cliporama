package cliporama;

import java.io.File;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.Queue;
import java.util.concurrent.ArrayBlockingQueue;
import javafx.animation.AnimationTimer;
import javafx.animation.FadeTransition;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.TextArea;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.media.AudioClip;
import javafx.scene.text.Font;
import javafx.scene.text.Text;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.util.Duration;

/**
 * Gestion de l'interface graphique et de l'animation
 */
@SuppressWarnings("restriction")
public class LanceurCtrl{
	private File srt;
	private File audio;
	int flag = 0;		//drapeau indiquant si les deux champs ont bien été remplis: si flag>1,c'est bon, sinon c'est qu'un champ est vide

    @FXML
    private Button monBouton;

    @FXML
    private Button butSrt;

    @FXML
    private TextArea txtAudio;

    @FXML
    private TextArea txtSrt;

    @FXML
    private Button butTest;

    @FXML
    private Button butAudio;

    /**
     * Permet de définir l'action à lancer lors d'une interaction avec un bouton
     * Ici, c'est la selection des fichiers, ou le lancement du traitement du texte, et son animation
     */
    @FXML
    void initialize() {

    	/**
    	 * Bouton de lancement au clic du traitement des fichiers donnés et de l'animation complète
    	 */
    	monBouton.setOnAction(new EventHandler<ActionEvent>() {	//Si le bouton est cliqué, le traitement sur SRT est lancé, l'audio et l'animation sont lancés dans la fenetre

			public void handle(ActionEvent event) {
				if (flag>1){
					Srt test = new Srt(srt.getPath());
					LinkedList<Mot> lyrics = null;
					lyrics = test.traduction();
					Stage stage= new Stage();
					start(stage,lyrics);
					play_audio(audio);
				}
			}
		});

    	/**
    	 * Permet de préremplir rapidement les champs avec des fichiers de tests rapides
    	 */
    	butTest.setOnAction(new EventHandler<ActionEvent>() {
			public void handle(ActionEvent event) {
				//Permet de mettre des fichiers de test dans la racine
				audio= new File("data/musiques/Gorillaz.mp3");
				srt=new File("data/musiques/Test.srt");
				txtSrt.clear();
				txtAudio.clear();
				txtSrt.appendText(srt.getPath());
				txtAudio.appendText(audio.getPath());
				flag=2;
			}
		});

    	/**
    	 * Ouvre une au clic une fenetre de dialogue pour sélectionner un fichier mp3
    	 */
    	butAudio.setOnAction(new EventHandler<ActionEvent>() {
			public void handle(ActionEvent event) {
				//Permet de mettre le fichier audio dans la racine
				Stage stagemp3= new Stage();
				FileChooser fl = new FileChooser();
				FileChooser.ExtensionFilter filtre = new FileChooser.ExtensionFilter("MP3 files (*.mp3)", "*.mp3");
				fl.getExtensionFilters().add(filtre);
				File audiotmp = fl.showOpenDialog(stagemp3);
				if (!(audiotmp==null)){									//permet de conserver les informations déjà entrées si on ouvre la fenetre de choix puis la referme
					audio=audiotmp;
					txtAudio.clear();
					txtAudio.appendText(audio.getPath());
					flag++;
				}
			}
		});

    	/**
    	 * Ouvre une au clic une fenetre de dialogue pour sélectionner un fichier srt
    	 */
    	butSrt.setOnAction(new EventHandler<ActionEvent>() {
			public void handle(ActionEvent event) {
				//Permet de mettre le fichier srt dans la rscine
				Stage stagesrt= new Stage();
				FileChooser fl = new FileChooser();
				FileChooser.ExtensionFilter filtre = new FileChooser.ExtensionFilter("SRT files (*.srt)", "*.srt");
				fl.getExtensionFilters().add(filtre);
				File srttmp = fl.showOpenDialog(stagesrt);
				if (!(srttmp==null)){
					srt=srttmp;
					txtSrt.clear();
					txtSrt.appendText(srt.getPath());
					flag++;
				}
			}
		});
    }

    /**
     * Permet de lancer l'audio
     * @param audio	File fichier mp3
     */
    public void play_audio(File audio){
	    AudioClip music = new AudioClip(audio.toURI().toString());
	    music.play(1.0);
    }

    /**
     * Anime la fenetre JAVAFX en faisant apparaitre les images
     * @param stage		stage défini dans handle
     * @param lyrics	liste chainée de "Mot" dérivée du fichier SRT
     */
    public void start(Stage stage,LinkedList<Mot> lyrics){
    	final int WIDTH = 1116;		//Concerne la fenetre
	    final int HEIGHT = 788;
	    final int TAILLE = 300;		//Concerne les gifs

	    stage.setTitle("CLIPORAMA");
	    stage.setResizable(false);

	    //Création de l'arborescence d'un groupe : 			//root-->scene-->ImageView-->fondImage-->fond
	    final Group root = new Group();							//			  -->ImageView-->Image
	    Scene scene = new Scene(root);
	    File fond = new File("data/fond/fond.gif");
	    Image fondImage = new Image(fond.toURI().toString(), WIDTH, HEIGHT, false, false);
	    root.getChildren().add(new ImageView(fondImage));

	    //Mise en place des sous-titres basé sur les mots des gifs
	    final Text mots = new Text();
	    mots.setX(WIDTH/3);
	    mots.setY(HEIGHT-25);
	    mots.setFont(new Font(50));
	    root.getChildren().add(mots);

	    Iterator<Mot> it=lyrics.iterator();
	    final LinkedList<Imagif> images= new LinkedList<Imagif>();
        int margeBas = 50;
	    while (it.hasNext()) {		//Boucle faisant charger les images et leurs paramètres dans la liste images
    		Mot m = it.next();
	    	try {

	    		String URL = m.getImagePath();
	    		File file = new File(URL);
	    		Image im = new Image(file.toURI().toString(),TAILLE,TAILLE,true,false);	//le ratio est conservé ici et toutes les images ont la meme largeur

	    		images.add( new Imagif(m.getMot(),im, (WIDTH-im.getWidth()) * Math.random(), (HEIGHT-margeBas-im.getHeight()) * Math.random(), m.getTemps()));
	    	} catch (Exception e) {
				System.out.println("Erreur élément non trouvé : "+m.getMot());;
				e.printStackTrace();
	    	}
	    }

	    stage.setScene(scene);
	    stage.show();

	    //Fait un tableau FIFO pour les gifs afin de n'en garder que 5 à l'écran  *Stack pour LIFO*
	    final Queue<ImageView> queue = new ArrayBlockingQueue<>(5);


	   /**
	     * Permet la gestion du temps lors de l'animation JAVAFX
	     */
	    new AnimationTimer() {
	    	long init = System.currentTimeMillis();

	        public void handle(long arg0) {
	          double timesec = (System.currentTimeMillis()-init)/1000;
	          Iterator<Imagif> ite=images.iterator();		//Parcours d'images et affichage au bon temps
	          String motsAffiches = "";
	          while(ite.hasNext()) {
	        	  Imagif ima = ite.next();
	        	  double tpsima=ima.getTime();

	        	  if ((Double.compare(timesec,tpsima)<0)&(Double.compare(tpsima,timesec+1)<0.3)) {
	        		  ImageView imgView = ima.getImageView();
	        		  //si l'image n'est pas déjà affichée
	        		  if(!queue.contains(imgView)) {
	        			  root.getChildren().add(imgView);
	        			  //si la queue (FIFO) est déjà pleine
		        		  if(queue.size() == 5) {
		        			  //on ajoute un effet de fondu à l'image sortante
		        			  final ImageView aSupprimer = queue.poll();

		        			  FadeTransition ft = new FadeTransition(Duration.millis(1500), aSupprimer);
		        			  ft.setFromValue(1.0); //valeur de départ pour le fondu (1 pour ne pas être fondu du tout)
		        			  ft.setToValue(0.0);	//valeur d'arrivée pour le fondu (0 pour être totalement transparente)
		        			  ft.play();

		        			  //lorsque le fondu est terminé
		        			  ft.setOnFinished(new EventHandler<ActionEvent>() {
		        				  @Override
		        				  public void handle(ActionEvent event) {
		        					// on supprime l'élément de la scene
		        					  root.getChildren().remove(aSupprimer);
		        				}
							});
		        		  }
		        		  queue.add(imgView);

		        		  //ajout du mot pour affichage
		        		  motsAffiches+=" "+ima.getMot();
	        		  }

	        	  }

	          }
	          if(motsAffiches != "") {
	        	  mots.setText(motsAffiches);

	          }
	        }
	      }.start();
    }
}