package cliporama;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.*;
import javafx.stage.Stage;

public class Main extends Application {

	public static void main(String[] args) {
		launch(args);
	}

	/**
	 * Lance le cadre de l'interface JAVAFX
	 */
	@Override
	public void start(Stage primaryStage) {
		Parent root;
		try {
			root = FXMLLoader.load(getClass().getResource("Lanceur.fxml"));	//Charge l'interface
		} catch (Exception e) {
			e.printStackTrace();
			return;
		}

		Scene scene = new Scene(root);	//Permet la création de la fenetre contenant l'interface
		primaryStage.setScene(scene);
		primaryStage.sizeToScene();
		primaryStage.show();
	}
}